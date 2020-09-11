# snet-marketplace-service

[![CircleCI](https://circleci.com/gh/singnet/snet-cli.svg?style=svg)](https://circleci.com/gh/singnet/snet-marketplace-service)
[![Coverage Status](https://coveralls.io/repos/github/singnet/snet-marketplace-service/badge.svg?branch=master)](https://coveralls.io/github/singnet/snet-marketplace-service?branch=master)

This is the mono-repo for services of DApps, SingularityNET Marketplace and SingularityNET Publisher Portal.

Consists of following services:

#### Marketplace Services
* [Contract API Service](contract_api)
* [Signer Service](signer)
* [Service Status](service_status)
* [Payment Service](payments)
* [Wallet Service](wallets)
* [Orchestrator Service](orchestrator)

#### Publisher Portal Services
* [Registry Service](registry)
* [Verification Service](verification)
* [Utility Service](utility)

#### Common Services
Services which are part of both DApps
* [DApp User Service](dapp_user)
* [Notification Service](notification)
* [Event PubSub Service](event_pubsub)


### Service Architecture
Service is divided into mainly three parts
* <b>Application</b>: Contains the interface for clients to communicate with service.
* <b>Domain</b>: Contains core logic of service, and interacts with other services.
* <b>Infrastructure</b>: Contains the interface for clients to communicate with services.

#### Database management
[Alembic](https://github.com/alembic/alembic) is being used to maintain the database versions and automate the database upgrade process.

#### Application infrastructure:
All services are serverless applications compatible with AWS serverless architecture.


### Development
These instructions are intended to facilitate the development and testing of services.

### Prerequisites

* [python 3.6.5+](https://www.python.org/downloads) and [python-pip](https://www.python.org/downloads)
* Additionally you should install the python dependency packages present in requirements.txt per service
* nodejs's npm 3.5.2+
* Additionally you should install the external dependency packages present in package.json per service.


#### Clone the git repository
```bash
$ git clone git@github.com:singnet/snet-marketplace-service.git
$ cd snet-marketplace-service
```

#### Install snet-marketplace-service dependency using pip
```bash
$ cd <service_name>
$ pip install -r requirements.txt
$ npm install
```

#### Deployment Configuration
Need to fill up all appropriate variables in `<service>/config.py`
