# Development

<!-- TOC -->

* [Development](#development)
  * [Pre-Installation Requirements](#pre-installation-requirements)
  * [Installation](#installation)
  * [Development](#development-1)

<!-- TOC -->

## Pre-Installation Requirements

- [Python 3.12](https://www.python.org/downloads/)
- [NodeJs 23.0.0](https://nodejs.org/en/download/)
- [Docker](https://docs.docker.com/engine/install/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## Installation

* Run `make install` at the root of the project to install all dependencies and set up the environment.

  ```sh
  ❯ make install
  Installing python dependencies...
  Installing dependencies from lock file
  
  No dependencies to install or update
  
  Installing the current project: src (1.0.0)
  Installing node dependencies...
  Lockfile is up to date, resolution step is skipped
  Already up to date
  
  Done in 431ms using pnpm v10.9.0
  Installing pre-commit hooks...
  pre-commit installed at .git/hooks/pre-commit
  pre-commit installed at .git/hooks/pre-push
  pre-commit installed at .git/hooks/commit-msg
  Done
  ```

## Development

* `make` or `make help` to see available commands.

  ```sh
    ❯ make 
    install              Install the packages
    activate             Activate the virtual environment
    start                Start the local master server
    prepare-neos         Prepare s3 and iam roles for NEOS environment
    deploy-local         Deploy to the local environment
    deploy-neos          Deploy to the NEOS environment
    package-local        Create artifacts for local deployment
    package-neos         Create artifacts for NEOS deployment
    delete-local         Delete the local deployment
    delete-neos          Delete the NEOS deployment
    test                 Run the tests
    coverage             Check code coverage
  ```

* `make activate` to activate the virtual environment (Python & NodeJS).
    ```sh
    ❯ make activate
    Virtual environment activated.
    ```

* `make start` to start the local development environment.
    ```sh
    ❯ make start  
    Starting LocalStack...
    [+] Running 1/1
     ✔ Container localstack  Started                                                                                                                                                                                                                                                                                0.3s 
    LocalStack started successfully.
    ```

* `make deploy-local` to deploy the local environment.
    ```sh
    ❯ make deploy-local
    Deploying 'monitoring-agent' in stage 'local'...
    pnpm exec sls deploy --stage local --config serverless.agent.local.yml
    ...
    Service deployed to stack 'monitoring-agent-local' (1s)   

    Deploying 'monitoring-master' in stage 'local'...
    pnpm exec sls deploy --stage local --config serverless.master.local.yml
    ...
    Service deployed to stack 'monitoring-master-local' (1s)  
    ```
