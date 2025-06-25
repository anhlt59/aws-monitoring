# Deployment

## Prerequisites
  - [Docker](https://docs.docker.com/engine/install/)
  - [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
  - `make install & make activate` has been run.

## Deploy from your local
* Deploy neos
    ```shell
    ❯ make deploy-neos
    Deploying 'teligent-agent' in stage 'neos'...
    pnpm exec sls deploy --stage neos --config serverless.agent.yml
    ...
    Service deployed to stack 'teligent-agent-neos' (1s)   
  
    Deploying 'teligent-master' in stage 'neos'...
    pnpm exec sls deploy --stage neos --config serverless.master.yml
    ...
    Service deployed to stack 'teligent-master-neos' (1s)  
    ```

