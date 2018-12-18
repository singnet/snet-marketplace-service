# snet-marketplace-service

[![CircleCI](https://circleci.com/gh/singnet/snet-cli.svg?style=svg)](https://circleci.com/gh/singnet/snet-marketplace-service)
  
## Getting Started  
#### SingularityNET Marketplace Service  
The Marketplace Service serves as an index to display curated services on the SingularityNet DApp.
### Development
These instructions are intended to facilitate the development and testing of SingularityNET Marketplace Service.

### Prerequisites

* [python 3.6.5+](https://www.python.org/downloads/)
* pip 9.0.1+
* Additionally you should install the following dependency package present in requirement.txt.

### Installation
If you use Ubuntu (or any Linux distribution with APT package support) you should do the following:

#### Clone the git repository
```bash
$ git clone git@github.com:singnet/snet-marketplace-service.git
$ cd snet-marketplace-service
```

#### Install snet-marketplace-service dependency using pip
```bash
$ pip install -r requirements.txt
```
#### Environment variables
Provide following environment variable in repository.py

environment variables|value
-----|-----
DB_HOST|
DB_USER|
DB_PASSWORD|
DB_NAME|
DB_PORT|

#### Deployment
We use AWS Lambda(serverless architecture) for deployment.
