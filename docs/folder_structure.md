# 📁 Folder structure

```
.
├── docs
├── infra
│   ├── master            # Master stack infrastructure
│   │   ├── configs          # Stage configurations
│   │   ├── functions        # Lambda functions
│   │   ├── plugins          # Serverless Framework plugins
│   │   └── resources        # CloudFormation templates
│   ├── agent             # Agent stack infrastructure
│   │   ├── configs
│   │   ├── plugins
│   │   └── resources
│   └── roles             # IAM roles and policies for deployment
├── ops
│   ├── deployment        # Deployment scripts (package, deploy, delete, etc.)
│   ├── development       # Development scripts (install, start, tests, etc.)
│   ├── local             # Local development scripts (LocalStack, Docker, etc.)
│   ├── postman           # Postman collections
│   └── base.sh
├── src
│   ├── adapters          # Adapters for external services
│   │   ├── aws
│   │   ├── db
│   │   ├── api
│   │   └── notifiers
│   ├── common            # Common utilities and helpers
│   │   ├── exceptions
│   │   ├── utils
│   │   ├── logger
│   │   └── configs
│   ├── handlers          # Handlers for Lambda functions
│   │   ├── agent
│   │   └── master
│   └── models            # Data models and schemas
├── tests
├── docker-compose.yaml
├── Makefile
├── package.json                        # Node.js dependencies
├── pyproject.toml                      # Python dependencies
├── README.md
├── serverless.agent.local.yml
├── serverless.master.local.yml
├── serverless.agent.yml                # Serverless Framework template for agent stack
└── serverless.master.yml               # Serverless Framework template for master stack
```