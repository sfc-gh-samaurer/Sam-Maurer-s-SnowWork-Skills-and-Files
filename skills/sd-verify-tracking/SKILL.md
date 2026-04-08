---
name: sd-verify-tracking
description: "Verifies sd_project_tracking installation is complete and working. Use when: user says /sd-verify-tracking or asks to verify SD project tracking setup. Triggers: sd-verify-tracking, verify sd tracking, check sd hooks, setup-sa-tracking."
log_marker: SKILL_USED_SETUP_SD_TRACKING
---

# Verify sd_project_tracking Setup

Checks that `install.sh` ran successfully and the tracking system is properly configured.

## Instructions

Execute every step in order **without asking questions**.

### Step 1 — Check hooks folder and scripts

```bash
ls -la ~/.snowflake/cortex/hooks/cx_projects_tracking/cli/
```

Verify these files exist:
- `cli/session-tag-init.sh`
- `cli/user-prompt-check.sh`

Also check that the `snowwork/` subdirectory exists:
```bash
ls -la ~/.snowflake/cortex/hooks/cx_projects_tracking/snowwork/
```

If any are missing, report which ones and print:
```
Run install.sh to set up hooks.
```

### Step 2 — Check hooks.json

```bash
cat ~/.snowflake/cortex/hooks.json
```

Verify both event types (`SessionStart`, `UserPromptSubmit`) have entries with commands pointing to `cx_projects_tracking/cli/` scripts. If missing, print:
```
Run install.sh to register the hooks in hooks.json.
```

### Step 3 — Check project list source

At least ONE of the following must be true:
1. `sd_projects.txt` exists in the hooks folder:
   ```bash
   cat ~/.snowflake/cortex/hooks/cx_projects_tracking/sd_projects.txt
   ```
   If found, count non-comment, non-blank lines and verify pipe-delimited format: `account|projectID|project|milestoneID|milestone|email`.

2. A Snowhouse connection is configured — check for an account value containing "snowhouse" (case-insensitive) in either `~/.snowflake/connections.toml` or `~/.snowflake/config.toml`.

If neither is found, print:
```
WARNING: No project list source detected. You need either a Snowhouse connection or an sd_projects.txt file.
```

### Step 4 — Check installed skills

Verify these skill files exist:
- `~/.snowflake/cortex/skills/sd-submit-info/SKILL.md`
- `~/.snowflake/cortex/skills/sd-verify-tracking/SKILL.md`

If a Snowhouse connection was detected in Step 3, also check:
- `~/.snowflake/cortex/skills/sd-project-list-setup/SKILL.md`

Report any missing skills.

### Step 5 — Summary

Print a summary:
- Hook scripts found / missing
- hooks.json status (SessionStart, UserPromptSubmit)
- Project list source (Snowhouse, sd_projects.txt, or neither)
- sd_projects.txt entry count (if applicable)
- Skills installed / missing
- "Start a new cortex session to test" if everything is OK

## Important

- Do NOT write hook scripts or update hooks.json — install.sh handles that.
- This skill is read-only verification only.
