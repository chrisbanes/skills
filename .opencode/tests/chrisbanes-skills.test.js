import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { test } from "node:test";
import { load } from "js-yaml";
import definition, { ChrisBanesSkillsPlugin } from "../plugins/chrisbanes-skills.js";

const root = fileURLToPath(new URL("../../", import.meta.url));
const marker = "CHRISBANES_SKILLS_OPENCODE_GUIDANCE";

async function register(plugin = definition) {
  let transform;
  let hook;
  await plugin.setup({
    skill: {
      transform: async (callback) => {
        assert.equal(transform, undefined, "register one catalog transform");
        transform = callback;
        return { dispose() {} };
      },
    },
    session: {
      hook: async (name, callback) => {
        assert.equal(name, "context");
        assert.equal(hook, undefined, "register one context hook");
        hook = callback;
        return { dispose() {} };
      },
    },
  });
  return { transform, hook };
}

function replay(transform) {
  const skills = new Map();
  const result = transform({ add: (skill) => skills.set(skill.id, skill) });
  assert.equal(result, undefined, "catalog edits are synchronous");
  return skills;
}

async function fixture(t, files = {}) {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), "opencode-plugin-test-"));
  t.after(() => fs.rm(directory, { recursive: true, force: true }));
  const entry = path.join(directory, ".opencode/plugins/chrisbanes-skills.js");
  await fs.mkdir(path.dirname(entry), { recursive: true });
  await fs.copyFile(path.join(root, ".opencode/plugins/chrisbanes-skills.js"), entry);
  await fs.writeFile(path.join(directory, "package.json"), '{"type":"module"}');
  await fs.symlink(path.join(root, "node_modules"), path.join(directory, "node_modules"));
  for (const [name, content] of Object.entries(files)) {
    const file = path.join(directory, "skills", name, "SKILL.md");
    await fs.mkdir(path.dirname(file), { recursive: true });
    await fs.writeFile(file, content);
  }
  return { directory, plugin: (await import(pathToFileURL(entry).href)).default };
}

test("the package exposes separate V1 and V2 entrypoints", () => {
  assert.equal(definition.id, "chrisbanes-skills");
  assert.equal(definition.server, ChrisBanesSkillsPlugin);
  assert.equal(typeof definition.setup, "function");
});

test("V1 registers the skills directory once and retains user guidance", async () => {
  const hooks = await definition.server({});
  const config = { skills: { paths: ["/existing"] } };
  await hooks.config(config);
  await hooks.config(config);
  assert.deepEqual(config.skills.paths, ["/existing", path.join(root, "skills")]);

  const messages = [
    { info: { role: "assistant" }, parts: [{ type: "text", text: "Earlier" }] },
    { info: { role: "user" }, parts: [{ id: "part-1", type: "text", text: "Review Compose" }] },
  ];
  const original = structuredClone(messages);
  await hooks["experimental.chat.messages.transform"]({}, { messages });
  await hooks["experimental.chat.messages.transform"]({}, { messages });
  assert.deepEqual(messages[0], original[0]);
  assert.equal(messages[1].parts.length, 2);
  assert.ok(messages[1].parts[0].text.includes(marker));
  assert.deepEqual(messages[1].parts[1], original[1].parts[0]);
});

test("V2 registers every repository skill with decoded metadata and exact source paths", async () => {
  const { transform } = await register();
  const skills = replay(transform);
  const entries = (await fs.readdir(path.join(root, "skills"), { withFileTypes: true }))
    .filter((entry) => entry.isDirectory());
  const expected = [];
  for (const entry of entries) {
    const file = path.join(root, "skills", entry.name, "SKILL.md");
    const source = await fs.readFile(file, "utf8");
    const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)([\s\S]*)$/);
    const metadata = load(match[1]);
    expected.push(entry.name);
    const skill = skills.get(entry.name);
    assert.equal(skill.name, metadata.name);
    assert.equal(skill.description, metadata.description);
    assert.equal(skill.path, file);
    assert.equal(skill.content, match[2]);
    assert.equal(skill.autoinvoke, metadata["disable-model-invocation"] !== true);
  }
  assert.deepEqual([...skills.keys()].sort(), expected.sort());
  assert.deepEqual(replay(transform), skills);
});

test("V2 adds guidance once per request without changing conversation messages", async () => {
  const { hook } = await register();
  const event = {
    system: [{ type: "text", text: "Existing instructions" }],
    messages: [{ role: "user", content: [{ type: "text", text: "Review Compose" }] }],
  };
  const original = structuredClone(event);
  await hook(event);
  await hook(event);
  assert.deepEqual(event.messages, original.messages);
  assert.deepEqual(event.system[0], original.system[0]);
  assert.equal(event.system.length, 2);
  assert.ok(event.system[1].text.includes(marker));
  const nextRequest = { system: [], messages: [] };
  await hook(nextRequest);
  assert.equal(nextRequest.system.length, 1);
});

test("V2 handles quoted and multiline YAML and captures files before transform replay", async (t) => {
  const { directory, plugin } = await fixture(t, {
    example: '---\nname: example\ndescription: >-\n  Use when a task has\n  multiple lines: preserve them.\ndisable-model-invocation: true\n---\n# Example\n\nRead `references/details.md`.\n',
    quoted: '---\nname: quoted\ndescription: "Use when quoting: \\"hello\\"."\n---\nQuoted body\n',
    override: '---\nname: override\ndescription: Use when checking metadata priority.\ndisable-model-invocation: true\nmetadata:\n  opencode/autoinvoke: "true"\n---\nOverride body\n',
  });
  await fs.writeFile(path.join(directory, "skills", "README.md"), "Not a skill");
  await fs.mkdir(path.join(directory, "skills", "supporting-directory"));
  const { transform } = await register(plugin);
  await fs.rm(path.join(directory, "skills"), { recursive: true });
  const skills = replay(transform);
  assert.equal(skills.size, 3);
  assert.equal(skills.get("example").description, "Use when a task has multiple lines: preserve them.");
  assert.equal(skills.get("example").autoinvoke, false);
  assert.equal(skills.get("quoted").description, 'Use when quoting: "hello".');
  assert.equal(skills.get("override").autoinvoke, true);
  assert.deepEqual(replay(transform), skills);
});

test("a missing skills directory warns without advertising unavailable skills", async (t) => {
  const { plugin } = await fixture(t);
  const warnings = t.mock.method(console, "warn", () => {});
  const registration = await register(plugin);
  assert.equal(registration.transform, undefined);
  assert.equal(registration.hook, undefined);
  assert.equal(warnings.mock.callCount(), 1);
  assert.match(warnings.mock.calls[0].arguments[0], /Skills directory not found/);
  const logged = [];
  const hooks = await plugin.server({ client: { app: { log: async (entry) => logged.push(entry) } } });
  const config = {};
  await hooks.config(config);
  assert.deepEqual(config, {});
  assert.match(logged[0].body.message, /Skills directory not found/);
});

test("malformed metadata fails setup before any partial registration", async (t) => {
  const { plugin } = await fixture(t, {
    example: '---\nname: example\ndescription: [not a string]\n---\nBody\n',
  });
  await assert.rejects(register(plugin), /Invalid skill metadata.*example/);
});
