'use strict';


class JsonUtilPlugin {
  constructor(serverless, options) {
    this.serverless = serverless;
    this.options = options;
    this.configurationVariablesSources = {json: obj => JSON.stringify(obj)}
  }
}

module.exports = JsonUtilPlugin;
