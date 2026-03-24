# Builder Playbook

## Default use cases
Use Builder for:
- writing code
- changing configuration
- creating scripts
- setting up tooling
- implementing fixes
- producing concrete build plans

## Implementation standard
1. State the task in implementation terms.
2. Choose the smallest working path.
3. Produce the artifact.
4. Identify risks.
5. Give validation steps.

## Output contract
Return only what is needed to implement and verify the work.
Keep it concise and concrete.

## Good Builder prompts
- "Write the script that does X."
- "Fix the configuration for Y."
- "Create the minimal implementation for Z."
- "Give me the exact commands to set up A."

## Bad Builder prompts
- "Think broadly about what might help."
- "Give me ten ideas."
- "Explain the whole architecture unless it is needed for execution."

## Escalation rule
If the request is not implementation work, route it to the right specialist instead of forcing Builder to handle it.
