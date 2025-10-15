# Claude Instructions

## Folder Structure
```
project-root/
├── .claude/
│   ├── instructions        # This file: Instructions for using Claude in the
│   ├── workflows
│   ├── agents/
│   │   ├── architect-agent.md
│   │   ├── code-gen-agent.md
│   │   ├── code-review-agent.md
│   │   └── doc-updater.md
│   ├── architect-agent/         # Subagent for system design
│   ├── code-gen-agent/          # Subagent for code generation
│   ├── code-reviewer/           # Subagent for code review
│   └── doc-updater/             # Subagent for documentation updates
├── docs
│   ├── requirements
│   ├── design
│   └── db
├── requirements.md              # Requirements documentation
├── system_design.md             # System design documentation
├── database_design.md           # Database design documentation
├── CHANGELOG.md                 # Changelog for tracking changes
├── README.md                    # Project overview and setup instructions
└── src/                          # Source code directory
    └── ...                      # Application code files
```

## Prerequisites




1. User stories
    * Nguồn gốc: Agile/Scrum.
    * Mục đích: Diễn đạt nhanh gọn nhu cầu của người dùng ở mức tính năng, để team dev hiểu “ai cần gì và tại sao”.
    * Cấu trúc thường dùng:
        * As a [type of user], I want [goal] so that [reason]
    * Đặc điểm:
        * Ngắn gọn, 1–2 câu.
        * Không đi sâu chi tiết logic.
        * Là “lời kể” của người dùng.
        * Thường đi kèm acceptance criteria để làm rõ khi nào tính năng được xem là hoàn thành.
    * Ví dụ:
        * As a customer, I want to reset my password so that I can regain access to my account if I forget it.
    *
