---
name: _my-security-reviewer
description: Security-focused audit of a diff or named code area — injection, auth, secrets, unsafe deserialization, crypto, dependencies, configuration. Read-only by instruction; some harnesses also grant a shell.
tools: read_file, grep, list_dir, todo_write, web_search, web_fetch
disallowedTools: search_tool, use_tool
mcpInheritance: none
---
