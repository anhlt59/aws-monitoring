# Local Development Guide

This guide provides instructions for setting up and running the AWS Monitoring project on your local machine using
LocalStack for AWS service emulation.

## Prerequisites

Before you can run the project locally, you need to have the following prerequisites installed:

- [Python 3.12](https://www.python.org/downloads/)
- [NodeJs 23.0.0](https://nodejs.org/en/download/)
- [Docker](https://docs.docker.com/engine/install/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/anhlt59/aws-monitoring.git
    cd aws-monitoring
    ```
2. **Install dependencies:**
    ```bash
    make install
    ```
3. **Activate the virtual environment:**
    ```bash
    make install
    ```

## Local Development Environment

### LocalStack Setup

LocalStack provides local AWS service emulation. The project is configured to use:

| AWS Service     | LocalStack Port | Purpose              |
|-----------------|-----------------|----------------------|
| Lambda          | 4566            | Function execution   |
| DynamoDB        | 4566            | Event/Agent storage  |
| EventBridge     | 4566            | Event routing        |
| CloudWatch Logs | 4566            | Log storage          |
| API Gateway     | 4566            | REST endpoints       |
| S3              | 4566            | Deployment artifacts |

### Starting the Development Environment

```bash
# Start LocalStack container
make start

# Deploy both stacks to LocalStack
make deploy-local

# View deployment status
docker logs localstack
```

## Available Commands

### Development Commands

| Command             | Purpose                      | Details                       |
|---------------------|------------------------------|-------------------------------|
| `make install`      | Install all dependencies     | Python + Node.js + pre-commit |
| `make activate`     | Activate virtual environment | Sources Poetry shell          |
| `make start`        | Start LocalStack container   | Docker Compose up             |
| `make start-master` | Start master stack offline   | Serverless Offline port 3000  |
| `make start-agent`  | Start agent stack offline    | Serverless Offline port 3001  |

### Deployment Commands

| Command              | Purpose                    | LocalStack |
|----------------------|----------------------------|------------|
| `make deploy-local`  | Deploy both stacks         | ✅          |
| `make package-local` | Create deployment packages | ✅          |
| `make destroy-local` | Remove local deployment    | ✅          |

### Testing Commands

| Command         | Purpose                       | Details                    |
|-----------------|-------------------------------|----------------------------|
| `make test`     | Run all tests with coverage   | Pytest + coverage report   |
| `make coverage` | Generate HTML coverage report | Opens browser with results |
