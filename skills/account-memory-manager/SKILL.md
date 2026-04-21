---
name: account-memory-manager
description: "Manage persistent account memory files across Snowwork sessions. Use for: saving session context to an account, loading account memory, registering new accounts, updating account aliases, reviewing what's saved for an account. Triggers: save account context, save memory, load account context, account memory, register account, /save-account-context, what do I know about [account], update account memory."
---

# Account Memory Manager

Manages persistent memory files in `/memories` across sessions. Handles saving, loading, and registering account context so rich session knowledge survives context window resets.

---

## Key Paths

- **Memory files**: `~/.snowflake/cortex/memory/`
- **Account registry**: `~/.snowflake/cortex/hooks/account-lookup.json`
- **Active account state**: `~/.snowflake/cortex/hooks/.current-account.json`
- **Memory template**: `~/.snowflake/cortex/memory/ACCOUNT_TEMPLATE.md`

---

## Workflow: SAVE — Save Session Context

Use when the user says "save account context", "save memory", "/save-account-context", or at session end.

### Step 1 — Identify the Account

Read `~/.snowflake/cortex/hooks/.current-account.json` via bash. If it exists and contains a `name`, use that as the active account. If not, ask the user which account to save context for.

### Step 2 — Find the Memory File

Read `~/.snowflake/cortex/hooks/account-lookup.json`. Find the entry matching the account name. Expand the `memory_file` path (replace `~` with `$HOME`). If no entry exists, go to **Workflow: NEW ACCOUNT** first, then return here.

### Step 3 — Generate Session Summary

Synthesize the current session into a structured summary block:

```
### [TODAY'S DATE] — [SESSION TOPIC IN 5-8 WORDS]

**Key Decisions**
- [Decision 1]
- [Decision 2]

**Open Items / Next Steps**
- [ ] [Action item with owner if known]

**Artifacts Created**
| Type | Name | Link/Path |
|------|------|-----------|
| [e.g., Google Doc] | [Name] | [URL or path] |

**Context Notes**
[1-3 sentences of freeform context worth preserving]
```

### Step 4 — Append to Memory File

Read the current memory file. Append the summary block to the **Session Log** section at the bottom. Also update the **Open Items / Next Steps** section at the top of the file by:
- Checking off items completed this session (change `- [ ]` to `- [x]`)
- Adding any new open items from this session

Update the `## Last Updated:` line with today's date.

Write the updated file back using the `memory` tool (`str_replace` for targeted updates, or `create` to overwrite with new content).

### Step 5 — Confirm

Output exactly one sentence confirming what was saved and to which file.

---

## Workflow: LOAD — Load Account Memory

Use when the user says "load account context", "what do I know about [account]", or at the start of an account-focused session.

### Step 1 — Identify the Account

If the user named an account, find it in `account-lookup.json`. Otherwise read `.current-account.json`.

### Step 2 — Read and Present

Read the memory file (full content). Present it in a clean, readable format:
- Start with the **Account Overview** and **Active Engagements** sections
- Highlight any open **Next Steps** (unchecked `- [ ]` items)
- Show the 3 most recent Session Log entries
- Note the Last Updated date

Do NOT dump the raw markdown — format it nicely for the user.

---

## Workflow: NEW ACCOUNT — Register a New Account

Use when the user wants to track a new account that isn't in `account-lookup.json`.

### Step 1 — Gather Info

Use `ask_user_question` to collect:
- **Account name** (canonical name, e.g., "Acme Corp")
- **Aliases** (alternate names/abbreviations, comma-separated, e.g., "Acme, ACME")
- **Memory file name** (suggest a slug, e.g., `acme_corp_account_briefing.md`)

### Step 2 — Create Memory File from Template

Read `~/.snowflake/cortex/memory/ACCOUNT_TEMPLATE.md`. Replace `[ACCOUNT_NAME]` with the actual account name and `[DATE]` with today's date. Write the file to `~/.snowflake/cortex/memory/<suggested_filename>`.

### Step 3 — Register in account-lookup.json

Read `~/.snowflake/cortex/hooks/account-lookup.json`. Add a new entry:
```json
{
  "name": "<Account Name>",
  "aliases": ["<alias1>", "<alias2>"],
  "memory_file": "~/.snowflake/cortex/memory/<filename>.md"
}
```
Write the updated JSON back to the file.

### Step 4 — Confirm

Tell the user the account is registered and the memory file path. Offer to capture any initial context right now.

---

## Workflow: UPDATE — Update Account Aliases or Memory File Path

Use when the user says "add alias for [account]" or "update account registry".

### Step 1 — Find the Account

Read `account-lookup.json`. Find the matching entry.

### Step 2 — Update

Add/remove aliases or update the `memory_file` path as requested. Write the file back.

### Step 3 — Confirm

One sentence confirmation.

---

## Workflow: LIST — Show All Registered Accounts

Use when the user says "list my accounts", "show account registry", or "what accounts do I have memory for".

Read `account-lookup.json`. For each entry, check if the memory file exists and when it was last modified. Present a table:

| Account | Aliases | Memory File | Last Modified |
|---------|---------|-------------|---------------|
| ...     | ...     | ...         | ...           |

---

## Important Rules

- **Never delete existing memory file content** — always append, never overwrite the whole file unless explicitly asked
- **Always use `memory` tool** for reading/writing files in `/memories` — do not use bash cat/echo
- **Session Log entries go at the BOTTOM** of the memory file, newest last
- **Open Items at the TOP** should always reflect current state (completed items checked off)
- When the account-lookup.json has no match, offer to register the account before saving
- Keep session summaries concise — 10-20 lines max per session entry
