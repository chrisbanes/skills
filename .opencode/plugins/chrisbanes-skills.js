import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const skillsDir = path.resolve(__dirname, "../../skills");
const guidanceMarker = "CHRISBANES_SKILLS_OPENCODE_GUIDANCE";
const guidance = `<${guidanceMarker}>
Chris Banes skills are available in OpenCode. Use OpenCode's native skill tool to load focused guidance. For broad Kotlin, Android, JVM, or Jetpack Compose tasks, start by loading the using-chrisbanes-skills skill.
</${guidanceMarker}>`;

const logWarning = async (client, message) => {
  try {
    await client?.app?.log?.({
      body: {
        service: "chrisbanes-skills",
        level: "warn",
        message,
      },
    });
  } catch {
    // Logging must never prevent OpenCode from starting.
  }
};

const ensureSkillPath = (config) => {
  config.skills = config.skills || {};
  config.skills.paths = config.skills.paths || [];

  if (!config.skills.paths.includes(skillsDir)) {
    config.skills.paths.push(skillsDir);
  }
};

const injectGuidance = (messages) => {
  if (!Array.isArray(messages)) return;

  const firstUser = messages.find((message) => message?.info?.role === "user");
  if (!firstUser || !Array.isArray(firstUser.parts) || firstUser.parts.length === 0) return;

  const alreadyInjected = firstUser.parts.some(
    (part) => part?.type === "text" && part.text?.includes(guidanceMarker),
  );
  if (alreadyInjected) return;

  const referencePart = firstUser.parts[0];
  firstUser.parts.unshift({ ...referencePart, type: "text", text: guidance });
};

export const ChrisBanesSkillsPlugin = async ({ client }) => {
  return {
    config: async (config) => {
      if (!fs.existsSync(skillsDir)) {
        await logWarning(client, `Skills directory not found: ${skillsDir}`);
        return;
      }

      ensureSkillPath(config);
    },

    "experimental.chat.messages.transform": async (_input, output) => {
      injectGuidance(output?.messages);
    },
  };
};
