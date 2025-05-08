const path = require("path");

/**
 * Plugin to modify the root directory
 */
class FuncRootDir {
  constructor(serverless, options) {
    this.serverless = serverless;
    this.options = options;
    this.rootDir =
      typeof this.serverless.service.custom.functionRootDir === "string"
        ? this.serverless.service.custom.functionRootDir
        : "";

    this.hooks = {
      "before:run:run": this.resolve.bind(this),
      "before:offline:start": this.resolve.bind(this),
      "before:offline:start:init": this.resolve.bind(this),
      "before:package:initialize": this.resolve.bind(this),
      "before:deploy:function:packageFunction": this.resolve.bind(this),
      "before:invoke:local:invoke": this.resolve.bind(this),
    };
  }

  resolve() {
    if (this.rootDir) {
      const { functions } = this.serverless.service;

      this.serverless.cli.log("rootDir", this.serverless.rootDir);
      this.serverless.cli.log(
        "FunctionRootDir",
        this.serverless.FunctionRootDir
      );
      this.serverless.cli.log("package", this.serverless.service.package);

      Object.keys(functions).forEach((functionName) => {
        // Warn if package.include or package.exclude is used
        const packageObj = functions[functionName].package;
        if (
          Array.isArray(packageObj.include) ||
          Array.isArray(packageObj.exclude)
        ) {
          throw new Error(
            `Error: "${functionName}" 'package.include' and 'package.exclude' are deprecated. Use 'package.patterns' instead.`
          );
        }

        // Rewrite Function.package.patterns
        if (Array.isArray(packageObj.patterns)) {
          functions[functionName].package.patterns = packageObj.patterns.map(
            (pattern) => this.rewriteFilePath(pattern)
          );
        }

        // Rewrite Function.handler
        const handlerPath = functions[functionName].handler;
        functions[functionName].handler = this.rewriteFilePath(handlerPath);
      });
    }
  }

  rewriteFilePath(filePath) {
    if (filePath) {
      if (typeof filePath !== "string") {
        throw new Error(
          `file path must be a string for function "${functionName}"`
        );
      }
      if (filePath.startsWith("!")) {
        return "!" + path.posix.join(this.rootDir, filePath.slice(1));
      }
      return path.posix.join(this.rootDir, filePath);
    }
  }
}

module.exports = FuncRootDir;
