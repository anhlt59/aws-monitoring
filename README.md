# 📊 AWS Monitoring 🌩️

![banner.png](docs/images/banner.png)

<div align="center">

**A fully serverless application for monitoring AWS resources and applications for performance, availability, and security issues.**

</div>

---

## 📖 Table of Contents

<!-- TOC -->
* [📊 AWS Monitoring 🌩️](#-aws-monitoring-)
  * [📖 Table of Contents](#-table-of-contents)
  * [✨ Features](#-features)
  * [🏗️ Project Overview](#-project-overview)
  * [🏁 Getting Started](#-getting-started)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
  * [🏃‍♀️ Running the project](#-running-the-project)
    * [Local Development](#local-development)
    * [Deployment](#deployment)
  * [🗃️ Database](#-database)
  * [🤝 Contributing](#-contributing)
<!-- TOC -->

---

![Unittest](https://img.shields.io/badge/-passing-brightgreen?style=for-the-badge&logo=github&logoColor=black)
![Coverage Status](https://img.shields.io/badge/Coverage-88%25-blue?style=for-the-badge&logo=codecov&logoColor=white)

---

## ✨ Features

- **Real-time Monitoring:** Monitor your AWS resources and applications in real-time.
- **Custom Alarms:** Create custom alarms to notify you of potential issues.
- **Automated Actions:** Automatically respond to events and alarms.

---

## 🏗️ Project Overview

This project is a fully serverless application built on AWS. It uses a variety of AWS services to provide a comprehensive monitoring solution.

For a detailed explanation of the project's architecture, components, and tech stack, please see the [**Project Overview**](docs/overview.md) documentation.

---

## 🏁 Getting Started

### Prerequisites

- [Python 3.13](https://www.python.org/downloads/)
- [NodeJs 23.0.0](https://nodejs.org/en/download/)
- [Docker](https://docs.docker.com/engine/install/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/anhlt59/aws-monitoring.git
   ```

2. **Install dependencies:**

   ```bash
   make install
   ```

---

## 🏃‍♀️ Running the project

### Local Development

For detailed instructions on how to run the project locally, please see the [**Local Development Guide**](docs/development.md).

### Deployment

For detailed instructions on how to deploy the project to your AWS account, please see the [**Deployment Guide**](docs/deployment.md).

---

## 🗃️ Database

The project uses Amazon DynamoDB as its database. For more information about the database schema, please see the [**Database Schema Documentation**](docs/db.md).

---

## 🤝 Contributing

Contributions are welcome! Please see the [**Contributing Guide**](docs/git/contributing.md) for more information.
