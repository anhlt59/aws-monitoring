# Local Development Guide

This guide provides instructions for setting up and running the AWS Monitoring project on your local machine.

## Prerequisites

Before you can run the project locally, you need to have the following prerequisites installed:

- [Python 3.12](https://www.python.org/downloads/)
- [NodeJs 23.0.0](https://nodejs.org/en/download/)
- [Docker](https://docs.docker.com/engine/install/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## Installation

1.  **Install dependencies:** Run `make install` to install all the required dependencies.
2.  **Activate the virtual environment:** Run `make activate` to activate the virtual environment.

## Running the Local Environment

1.  **Start LocalStack:** Run `make start` to start the LocalStack container. This will create a local AWS environment on your machine.
2.  **Deploy the stacks:** Run `make deploy-local` to deploy the master and agent stacks to the local environment.

## Available Commands

The following `make` commands are available for local development:

- `make install`: Install all dependencies.
- `make activate`: Activate the virtual environment.
- `make start`: Start the LocalStack container.
- `make deploy-local`: Deploy the stacks to the local environment.
- `make delete-local`: Delete the local deployment.
- `make test`: Run the tests.
- `make coverage`: Check code coverage.
