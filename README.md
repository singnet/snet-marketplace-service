# snet-marketplace-service

[![CircleCI](https://circleci.com/gh/singnet/snet-cli.svg?style=svg)](https://circleci.com/gh/singnet/snet-marketplace-service)
[![Coverage Status](https://coveralls.io/repos/github/singnet/snet-marketplace-service/badge.svg?branch=master)](https://coveralls.io/github/singnet/snet-marketplace-service?branch=master)
## Getting Started  
### SingularityNET Marketplace Services
The best way to get started is by understanding the marketplace services that powers the decentralized Blockchain marketplace. Here is a high level view on how SingularityNet's services works.
#### Event Publisher Subscriber
This service reads all actionable events i.e events from Registry/MPE/RFAI/TokenStake contract deployed on the blockchain on near real time basis, persist event data into the mysql database and invokes all the subscribers of the event.
#### DApp User
This is a central service which stores user information across all the DApp.
#### Registry
The Registry service helps service developers in publishing the service on the snet platform and mainly interacts with Publisher Portal DApp. All the interactions right from when organization/individual is registered to the time it is published are handled by this service.
This service subscribes to Event Pub Sub for events and parses event data in structured format.
#### Contract API
The Contract API service handles all the general service consumer task. It helps to display and access curated service data in Marketplace DApp.
This service subscribes to Event Pub Sub for events and parses event data in structured format.
#### Service Status
This service keeps track of service status and service certificate. It also alerts service provider in case service is down or service certificate is expired. 
#### Signer
This is a central service which handles signature across all the DApp. In case of new signature, we have to define the signature format in signer service.
#### Payment
This is a central payment service which can handle payment via paypal across all the DApp. Currently it caters only to Marketplace DApp.
#### Wallets
This is a central  service which can handle blockchain operation like wallet creation, channel creation and funding channel.
#### Orchestrator
This service helps to orchestrate the response from multiple service. Currently we are using for orchestrator for 
### Development
These instructions are intended to facilitate the development and testing of SingularityNET Marketplace Service.

### Prerequisites

* [python 3.7+](https://www.python.org/downloads/)
* pip 20.3.3+
* Additionally you should install the python dependency package present in requirements.txt.
* [npm 6.14.6+](#)
* Additionally you should install the external dependency package present in package.json.

### Installation
If you use Ubuntu (or any Linux distribution with APT package support) you should do the following:

#### Clone the git repository
```bash
$ git clone git@github.com:singnet/snet-marketplace-service.git
$ cd snet-marketplace-service
```
#### Install service dependency using pip
```bash
$ cd <service-name>
$ pip install -r requirements.txt
$ npm install
```
#### Install alembic
```bash
$ pip install alembic
$ cd <service-name>
$ alembic init alembic
$ alembic upgrade head
```
#### Configuration
We are maintaining service configuration file in S3 bucket. During code build when the service is getting deployed it get picked based on service name and environment.
#### Deployment
We use AWS Lambda(serverless architecture) for deployment.
