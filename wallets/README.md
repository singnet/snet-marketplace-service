# Wallet Service

We support two types of wallet
* General Wallet
	* Wallet created using DApp.
* MetaMask Wallet
	* Wallet created using MetaMask.

It consist of following components

**User**  &rarr;* **Wallet**

**Wallet**  &rarr;* **Channel**

Wallet Creation, View and Register Wallet, Channel Creation For Third Party and Update Channel Transaction

### Wallet Creation

Creates wallet on Ethereum platform. Multiple wallet can be created by user. A wallet cannot be shared by two or more user.

### View and Register Wallet

View and Register wallet for a user.

### Channel Creation for third party and Add funds to channel.

Channel with funds is needed to use AI service in DApp. This component helps to create channel for third party and has capability to add funds to a channel.

### Update Channel Transaction

Once Blockchain Transaction is submitted successfully. It is in "*PENDING*" state. When it will get mined, is not certain. This component continuously check for transaction status("*FAILED*" or "*SUCCESS*") and updates in the database.
### Development
These instructions are intended to facilitate the development and testing of Wallet Service.

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
$ pip install -r wallets/requirements.txt
$ export PYTHONPATH=`pwd`
$ npm install
$ cd wallets
```
#### Configuration Variables
Provide necessary configuration in config.py

#### Deploy
```sls offline start -r us-east-1 --noTimeout```
