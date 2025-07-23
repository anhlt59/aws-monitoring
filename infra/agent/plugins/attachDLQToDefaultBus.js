"use strict";

const {
  EventBridgeClient,
  DescribeEventBusCommand,
  UpdateEventBusCommand,
} = require("@aws-sdk/client-eventbridge");

class AttachDLQToDefaultBusPlugin {
  constructor(serverless, options) {
    this.serverless = serverless;
    this.options = options;

    this.hooks = {
      "after:deploy:deploy": this.attachDLQ.bind(this),
    };
  }

  async attachDLQ() {
    const provider = this.serverless.getProvider("aws");
    const accountId = await provider.getAccountId();
    const region = await provider.getRegion();
    const credentials = await provider.getCredentials();
    const stage = await provider.getStage();
    const dlqArn = `arn:aws:sqs:${region}:${accountId}:${this.serverless.service.service}-${stage}-MonitoringDLQ`;

    const client = new EventBridgeClient({
      region,
      credentials: credentials,
    });

    try {
      const { Policy } = await client.send(
        new DescribeEventBusCommand({ Name: "default" })
      );

      if (Policy && Policy.includes(dlqArn)) {
        this.serverless.cli.log(
          "DLQ is already attached to the default event bus."
        );
        return;
      }

      this.serverless.cli.log(`Attaching DLQ to default bus: ${dlqArn}`);
      await client.send(
        new UpdateEventBusCommand({
          Name: "default",
          DeadLetterConfig: {
            Arn: dlqArn,
          },
        })
      );

      this.serverless.cli.log(
        "DLQ successfully attached to the default event bus."
      );
    } catch (err) {
      this.serverless.cli.log(`Error attaching DLQ: ${err.message}`);
    }
  }
}

module.exports = AttachDLQToDefaultBusPlugin;
