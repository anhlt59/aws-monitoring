'use strict';

class ValidateDeployment {
    constructor(serverless, options) {
        this.serverless = serverless;
        this.options = options;
        this.provider = serverless.getProvider('aws');
        this.hooks = {
            initialize: async () => await this.validate(),
        };
    }

    async validate() {
        // Ignore if the stage is 'local'
        if (this.options.stage === 'local') return null;

        // Load accountId from local configs
        const accountId = this.serverless.service.custom.default.accountId.toString();

        // Get account id
        const {Account} = await this.provider.request('STS', 'getCallerIdentity', {});
        console.log(`AccountID: ${Account}`);

        // Throw an error if the account id is invalid
        if (Account !==  accountId) {
            throw new Error(`Invalid account id: ${Account} (${accountId})`);
        }
    }
}

module.exports = ValidateDeployment;
