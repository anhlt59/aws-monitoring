# 📊 AWS Monitoring 🌩️

![banner.png](docs/images/banner.png)

🔹 Architecture: Fully serverless (AWS Lambda, API Gateway, DynamoDB, EventBridge, SNS, S3, CloudWatch)<br>
🔹 Purpose: Monitors AWS resources and applications for performance, availability, and security issues.<br>

<!-- TOC -->
* [📊 AWS Monitoring 🌩️](#-aws-monitoring-)
  * [💻 Tech Stack](#-tech-stack)
  * [🧪 Testing](#-testing)
  * [🏗️ Infrastructure](#-infrastructure)
  * [📦 Framework](#-framework)
  * [🛠️ Development](#-development)
  * [🚀 Deployment](#-deployment)
  * [🤝 Contributing](#-contributing)
<!-- TOC -->

## 💻 Tech Stack

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Poetry](https://img.shields.io/badge/Poetry-%233B82F6.svg?style=for-the-badge&logo=poetry&logoColor=0B3D8D)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Serverless Framework](https://img.shields.io/badge/serverless%20framework-8A2BE2?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)
![AmazonDynamoDB](https://img.shields.io/badge/Amazon%20DynamoDB-4053D6?style=for-the-badge&logo=Amazon%20DynamoDB&logoColor=white)
![Amazon S3](https://img.shields.io/badge/Amazon%20S3-FF9900?style=for-the-badge&logo=amazons3&logoColor=white&color=green)
![Amazon Lambda](https://img.shields.io/badge/Amazon%20lambda-8A2BE2?style=for-the-badge&color=FF9933)
![LocalStack](https://img.shields.io/badge/local%20stack-8A2BE2?style=for-the-badge&color=blue)
![Bash Script](https://img.shields.io/badge/bash_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white)

## 🧪 [Testing](tests)

![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)
![Coverage Status](https://img.shields.io/badge/Coverage-88%25-blue?style=for-the-badge&logo=codecov&logoColor=white)

## 🏗️ Infrastructure

![infra](docs/images/infra.png)

## 📦 Framework

This application is constructed using the Serverless Framework.

- [Serverless Framework](https://www.serverless.com/)

## 🛠️ Development

- [Development](docs/development.md)
- [Folder Structure](docs/folder_structure.md)
- [Database](docs/db.md)
- [API GW](docs/aws-api-gw.md)
- Lambda Functions:
  - [Master-HandleMonitoringEvent](infra/master/functions/HandleMonitoringEvents.yml)
  - [Master-DailyReport](infra/master/functions/DailyReport.yml)
  - [Master-GetEvent](infra/master/functions/api/GetEvent.yml)
  - [Master-ListEvent](infra/master/functions/api/ListEvents.yml)
  - [Master-UpdateEvent](infra/master/functions/api/UpdateEvent.yml)
  - [Agent-DailyReport](infra/agent/functions/QueryErrorLogs.yml)

## 🚀 Deployment

- AWS
  - [Prerequisite Resources](docs/aws-prerequisite-resources.md)
  - [Environment Configs](docs/aws-environment-configs.md)
  - [Deployment](docs/aws-deployment.md)

## 🤝 [Contributing](docs/git/contributing.md)
