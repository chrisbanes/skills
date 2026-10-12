Use only the supplied state and applicable skill instructions. Read skill entrypoints and needed Markdown references using standalone `cat` commands. Do not execute the workflow, run other commands, contact providers, launch agents or change files.

In `drain` with two slots and a user-set waiting cap of one, #90 is already waiting. #91 just pushed its reviewed PR. #92 pushed a PR but its independent review has not run. #93 is waiting on CI but still holds a named emulator lock. Separately, a `next` invocation is shepherding #94 through CI. Which claims may release a slot?
