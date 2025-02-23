## Deployment

### Deploy from your local

* Prerequisites
    - [Install Docker](https://docs.docker.com/engine/install/)
    - [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
    - [Configure following profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html):
        - denaribot_dev
        - denaribot_stg
        - denaribot_prod

    - Installed NodeJS and NodeJS packages.
      ```sh
      $ npm i --production
      ```

* Use serverless commands
    * Options
        * --stage or -s The stage in your service that you want to deploy to. Default: dev
        * --aws-profile The AWS profile to use, as specified in ~/.aws/credentials. Default: default

    * Deploy all functions
      ```shell
      $ npx sls deploy -s $STAGE --aws-profile $AWS_PROFILE
      ```

    * Deploy a function
      ```shell
      $ npx sls deploy function -s $STAGE --function $FunctionName --aws-profile $AWS_PROFILE
      ```
  More details in
  [Serverless Framework Documentation](https://www.serverless.com/framework/docs/providers/aws/cli-reference/deploy)

* Or use deploy script
    * [script](./scripts/deploy.sh)
      ```shell
      $ ./scripts/deploy.sh         
      Select a stage:
      - dev
        - stg
        - prod
        Choose from dev, stg, prod [dev]: dev
      
      Pull the latest source code y/n [n]: y
      No local changes to save
      Already on 'develop'
      Your branch is up to date with 'origin/develop'.
      
      Summary:
      STAGE - dev
      PROFILE - denaribot_dev
      BRANCH - develop
      
      Continue to deploy? y/n [y]: y
      
      Deploying denaribots to stage dev (ap-southeast-1)
      AccountID: 691802122630
      Prune versions plugin: Pruning Lambda function versions and layers...
      Prune versions plugin: Layer version pruning complete, no versions to prune in 1 layers
      Prune versions plugin: Function version pruning complete, no versions to prune in 15 functions
      
      ✔ Service deployed to stack denaribots-dev (86s)
      ```