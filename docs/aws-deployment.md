# Deployment

## Prerequisites
  - [Docker](https://docs.docker.com/engine/install/)
  - [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
  - `make install & make activate` has been run.

## Deploy from your local
* Deploy neos
    ```shell
    ❯ make deploy-neos
    Deploying 'monitoring-agent' in stage 'neos'...
    pnpm exec sls deploy --stage neos --config serverless.agent.yml
    ...
    Service deployed to stack 'monitoring-agent-neos' (1s)   
  
    Deploying 'monitoring-master' in stage 'neos'...
    pnpm exec sls deploy --stage neos --config serverless.master.yml
    ...
    Service deployed to stack 'monitoring-master-neos' (1s)  
    ```

