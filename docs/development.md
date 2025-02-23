## Development

<!-- TOC -->

* [Development](#development)
    * [Installation](#installation)
    * [Development](#development)
        * [Pre-Installation Requirements](#pre-installation-requirements)
        * [Setup local environment](#setup-local-environment)

<!-- TOC -->

### Installation

* Setup [Virtual Environments](https://docs.python.org/3/library/venv.html) for Python
* Install Python packages
    ```sh
    $ pip install -r requirements/local.txt
    ```
* Install Nodejs packages
    ```sh
    $ npm i --save-dev
    ```
* Setup pre-commit to managing and maintaining pre-commit hooks
    ```sh
    $ pre-commit install
    ```
    ```sh
    ❯ git add . && git commit -m "fix: example commit"
    Detect AWS Credentials...................................................Passed
    Detect Private Key.......................................................Passed
    Trim Trailing Whitespace.................................................Passed
    Fix End of Files.........................................................Passed
    Check for merge conflicts................................................Passed
    black....................................................................Passed
    isort....................................................................Passed
    flake8...................................................................Passed
    bandit...................................................................Passed
    [develop 29ac707] fix: example commit
     Date: Mon Aug 21 17:42:54 2023 +0700
     4 files changed, 37 insertions(+), 59 deletions(-)
    ```

### Development

#### Pre-Installation Requirements

- [Docker](https://docs.docker.com/engine/install/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

#### Setup local environment

1. Setup local
    ```sh
    ❯ npm start  

    > denaribots@1.0.0 start
    > docker-compose up -d
    
    [+] Running 3/0
     ✔ Container localstack    Running                                                    0.0s 
     ✔ Container mysql         Running                                                    0.0s 
    ```
2. Start development mode
    ```sh
    ❯ npm run dev
    
    > denaribots@1.0.0 dev
    > npx serverless offline start --stage local

    Starting Offline at stage local (us-east-1)

    Offline [http for lambda] listening on http://localhost:3002
    Function names exposed for local invocation by aws-sdk:
           * ChangeESimPlan: denaribots-local-ChangeESimPlan
           * StreamsIOTToDynamoDB: denaribots-local-IOTStreamsToDynamoDB
           * StreamsIOTToRDS: denaribots-local-IOTStreamsToRDS
           * StreamsDynamoDBToRDS: denaribots-local-DynamoDBStreamsToRDS
           * LoadDisconnectedDevices: denaribots-local-LoadDisconnectedDevices
           * LoadRecoverAbsentDevices: denaribots-local-LoadRecoverAbsentDevices
           * PruneStatistics: denaribots-local-PruneStatistics
           * MonitorCase123: denaribots-local-MonitorCase123
           * MonitorCase4: denaribots-local-MonitorCase4
           * MonitorCase5: denaribots-local-MonitorCase5
           * MonitorCase6: denaribots-local-MonitorCase6
           * MonitorCase7: denaribots-local-MonitorCase7
           * NotifyUsers: denaribots-local-NotifyUsers

    ```