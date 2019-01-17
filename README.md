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
* Additionally you should install the python dependency package present in requirement.txt.
* [npm 3.5.2+](#)
* Additionally you should install the external dependency package present in package.json.

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
$ npm install
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

### Using the Service with Docker

#### Installation
In order to use the service with docker, the docker should be up and running in the host.
Please follow the instruction from the [docker link](https://docs.docker.com/install/linux/docker-ce/ubuntu/) for installation.

#### Prerequisites
1. Download the snet-marketplace-service and then snet-contract-event-consumer in the root directory.
```bash
$ git clone https://github.com/singnet/snet-marketplace-service.git
$ cd snet-marketplace-service
$ git clone https://github.com/singnet/snet-contract-event-consumer.git
```

2. Fill up the DB values in the### Installation    ```snet-marketplace-service/snet-contract-event-consumer/config.js``` and ```snet-marketplace-service/common/constant.py```

#### Building the Docker Image and Running the Container
 1. Build the Docker image.
 ```bash
 $ cd snet-marketplace-service
 $ docker build -t marketplace-event-consumer .
 ```

 2. Once the image is built, run the container with the below command.
 ```bash
 $ docker run marketplace-event-consumer:latest
 ```
