'use strict';

class LocalRefs {
    constructor(serverless, options) {
        this.serverless = serverless;
        this.options = options;
        this.hooks = {
            initialize: () => this.loadLocalsideEnvVars(),
        };
    }

    loadLocalsideEnvVars() {
        if (this.options.stage !== 'local') return null;

        // create a mapping for local resources
        const resourceRefs = createResourceRefsMapping(
            this.serverless.service.resources.Parameters,
            this.serverless.service.resources.Resources
        );

        // Update provider.environment that contains Ref or GetAttr
        for (const [key, value] of Object.entries(this.serverless.service.provider.environment || {})) {
            this.serverless.service.provider.environment[key] = replaceRefs(value, resourceRefs);
        }

        const functions = this.options.function
            ? {[this.options.function]: this.serverless.service.functions[this.options.function]}
            : this.serverless.service.functions;

        for (const fn of Object.values(functions)) {
            // Update function.environment
            for (const [key, value] of Object.entries(fn.environment || {})) {
                fn.environment[key] = replaceRefs(value, resourceRefs);
            }
            // Update function.events
            for (const event of fn.events || []) {
                if (event.sqs) {
                    event.sqs.arn = replaceRefs(event.sqs.arn, resourceRefs);
                }
            }
        }
    }
}

// return formatted mappings
const createResourceRefsMapping = (parameters, resources) => {
    const resourceRefs = {};
    for (const [key, parameter] of Object.entries(parameters)) {
        resourceRefs[key] = {Ref: parameter.Default};
    }
    for (const [key, resource] of Object.entries(resources)) {
        if (resource.Type === 'AWS::SNS::Topic') {
            resourceRefs[key] = {
                Ref: `arn:aws:sns:us-east-1:000000000000:${resource.Properties.TopicName}`,
            };
        }
        if (resource.Type === 'AWS::SQS::Queue') {
            resourceRefs[key] = {
                Ref: `http://localhost:4566/000000000000/${resource.Properties.QueueName}`,
                Arn: `arn:aws:sqs:us-east-1:000000000000:${resource.Properties.QueueName}`,
            };
        }
        if (resource.Type === 'AWS::S3::Bucket') {
            resourceRefs[key] = {
                Ref: resource.Properties.BucketName,
            };
        }
        if (resource.Type === 'AWS::DynamoDB::Table') {
            resourceRefs[key] = {
                Ref: resource.Properties.TableName,
            };
        }
    }
    return resourceRefs;
};

// replace dynamic references by local values
const replaceRefs = (value, resourceRefs) => {
    const refId = value.Ref;
    const getAttId = value['Fn::GetAtt'];
    if (refId) {
        value = resourceRefs[refId]?.Ref;
        if (!value) throw Error(`${refId}.Ref is undefined`);
    }
    if (getAttId) {
        value = resourceRefs[getAttId[0]]?.Arn;
        if (!value) throw Error(`${refId}.Arn is undefined`);
    }
    return value;
};

module.exports = LocalRefs;
