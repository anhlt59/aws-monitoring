# Workflow for Developing a New Feature with Claude AI

system: You are a senior software engineer experienced in using Claude AI to assist in the full lifecycle of feature development, from requirements gathering to documentation. Your goal is to ensure that every step is well-documented in Markdown files and that the documentation stays in sync with the codebase.
user: developer
## 1. Requirements Analysis
- **Information Gathering:** Identify feature requirements (user stories, acceptance criteria). Record them in a Markdown file (e.g., `requirements.md`). Clarify edge cases and non-functional requirements (performance, security).
- **Use Claude for Requirement Review:** Use a dedicated sub-agent (e.g., `requirement-agent`) with project context to review requirements. Claude can suggest additions or improvements. For example, Claude Code can analyze an initial idea and generate a detailed requirements document with a system overview. Studies show AI tools like ChatGPT reduce time spent defining requirements and improve accuracy.
- **Checklist:**
  - [ ] Ensure requirements are complete, clear, and human-readable.
  - [ ] Requirements are stored in Markdown and version-controlled.
  - [ ] Use Claude to verify logic and fill missing use cases.
- **Example:** For a “Product Search” feature — initial requirement: “User enters a keyword, system returns relevant products.” Ask Claude: “Should we add keyword suggestions, pagination, or handle no results?” Claude will propose enhancements and update `requirements.md` accordingly.

## 2. System and Architecture Design
- **Define the architecture:** Based on requirements, create a high-level system diagram (modules, data flow, integrations). Use tools like Mermaid or UML, or ask Claude to describe the design in plain English.
- **Detailed planning:** Switch to “Plan mode” in Claude Code to break the feature into smaller tasks. Claude will produce a detailed TO-DO list, task dependency graph, test plan, and deployment strategy.
- **Update design docs:** Update `system_design.md` and `database_design.md` with diagrams and logic descriptions. You can use embedded `CLAUDE.md` files for subprojects (backend, infra, etc.) to help Claude understand local context.
- **Checklist:**
  - [ ] Architecture diagrams are updated (component, sequence, flow diagrams, etc.).
  - [ ] Database schema (`database_design.md`) aligns with requirements.
  - [ ] Architectural changes are clearly explained and illustrated.
- **Example:** For “search,” ask Claude: “Generate a Mermaid diagram for the search feature workflow.” Claude will draw the user flow from input to results and may suggest indexing or caching strategies.

## 3. Coding and Implementation
- **Task breakdown:** Follow the TO-DO list. Implement each subtask in a separate branch or commit.
- **Use Claude for code generation:** Have Claude handle repetitive work. Use `code-generator` subagent (Python backend) to create templates for controllers, models, or AWS scripts (for infra). Claude Code can generate code, debug, and optimize.
- **Documentation and commits:** Let Claude write docstrings and comments. After each subfeature, commit with detailed messages (Claude can suggest one). Ask Claude to update documentation — e.g., append “Feature: X” to `README.md` or `CHANGELOG.md`.
- **Checklist:**
  - [ ] Code functions correctly and has basic tests.
  - [ ] All new logic includes comments or docstrings.
  - [ ] Commits have clear messages, and changes are reflected in docs.
- **Example:** For “Search API,” Claude can define endpoint `/search`, query logic, and JSON response, then suggest a commit message like “feat: add search endpoint.”

## 4. Code Review and Testing
- **Automated code review:** After code is written, use Claude’s `code-reviewer` subagent. It runs `git diff`, checks naming, duplication, error handling, validation, and security. It flags issues as *critical*, *warning*, or *suggestion*. You can also integrate tools like Codacy, Snyk, or DeepCode for automated code quality and security scanning.
- **Testing and debugging:** Run tests (unit, integration) or let Claude auto-generate test cases. Ask: “Generate unit tests for search feature.” Claude can produce test cases and check coverage. Use the `debugger` subagent for troubleshooting.
- **Checklist:**
  - [ ] All new code passes review and fixes reported issues.
  - [ ] Each feature has full test coverage and passes.
  - [ ] PR includes review summary and recommendations.
- **Example:** After building `/search`, Claude runs tests (“All 15 tests passed”) or flags issues like “Add empty keyword check (warning)” or “Use PreparedStatement to avoid SQL Injection (critical).”

## 5. Documentation Update and Maintenance
- **Sync docs with code:** Every code change must be reflected in docs. Use the `doc-updater` subagent to auto-suggest or generate Markdown updates. Tools like DeepDocs scan repos per commit to find and fix outdated docs automatically.
- **Review documentation:** Make doc review part of your PR process. No code merges without updated docs. Use tools like Docusaurus, Mintlify, or DocuWriter.ai for automatic API documentation.
- **Checklist:**
  - [ ] Requirements, system design, DB, and deployment docs updated.
  - [ ] AI checked for inconsistencies between code and docs.
  - [ ] Docs reviewed and merged with code.
- **Example:** When adding `/search`, Claude automatically adds: “Endpoint `/search` allows users to search for products by keyword” to `API.md`. DeepDocs or Claude ensures Markdown stays consistent with source code.

## 6. Best Practices for Maintaining Consistent Docs
- **Treat docs as code:** Store Markdown in Git, review with PRs. Update docs as part of CI/CD.
- **Dedicated subagents:** Create specialized agents — `requirement-agent`, `architect-agent`, `code-gen-agent`, `code-reviewer`, `doc-updater`. Each has a single clear purpose.
- **Detailed prompts:** Provide clear role instructions for each subagent (e.g., “You are a senior code reviewer focusing on security and maintainability”).
- **Tool control:** Restrict subagent access to only necessary tools (e.g., code-reviewer → read code, run lint).
- **Periodic audits:** Regularly review high-level docs (architecture, README) for drift. Claude can summarize code changes and propose doc updates.

**In summary:** Integrating Claude AI across the feature lifecycle automates repetitive tasks (analysis, coding, testing, docs). The key is structuring subagents properly, defining clear prompts, and treating documentation as part of your codebase. This ensures Markdown docs evolve with your codebase — reducing drift and improving maintainability.
