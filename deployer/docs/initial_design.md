# Deployer Service — Design Document

## Overview

This service is responsible for four primary workflows:

1. **Demon Management**
   Handles lifecycle of AI daemon containers (deploy, update, stop, etc.) based on smart contract events and platform integration.

2. **Payment Logic for HaaS**
   Validates and processes on-chain payments related to hosting AI daemon containers.

3. **Proxying Pod Information from HaaS**
   Provides internal APIs or event propagation for fetching and exposing pod/container status, logs, or resource metrics from infrastructure.

4. **Billing Logic for Serverless GPU (Future)**
   (Planned) Tracks invocation and GPU usage on serverless endpoints , integrates with billing subsystem.

---

## Motivation

While some logic exists in `payments` and `orchestration`, it’s currently difficult to maintain due to legacy decisions and tightly coupled code.  
This service aims to encapsulate **all HaaS-related lifecycle and billing logic** in a clean and maintainable way.
Also another main reason - we need to create service that can work with multiple networks and tokens.
---

## Storage Model

We define three core entities in the storage layer:

### `daemon`

Represents a deployed daemon instance tied to a user’s published AI service.

| Field           | Type     | Notes                                       |
|-----------------|----------|---------------------------------------------|
| `id`            | UUID     | Primary key                                 |
| `account_id`    | UUID     | Cognito id from dapp_user service           |
| `service_id`    | string   | Indexed, unique per service                 |
| `status`        | enum     | `init`, `starting`, `deleting`, `up`, `down`|
| `from_date`     | datetime |                                             |
| `end_date`      | datetime |                                             |
| `daemon_config` | JSON     |                                             |
| `created_at`    | datetime |                                             |
| `updated_at`    | datetime |                                             |


### `order`

Represents a payment order for provisioning a daemon or GPU serverless container.

| Field              | Type     | Notes                                   |
|--------------------|----------|-----------------------------------------|
| `id`               | UUID     | Primary key                             |
| `daemon_id`        | UUID     | Foreign key                             |
| `status`           | enum     | `init`, `processing`, `success`, `fail` |
| `created_at`       | datetime |                                         |
| `updated_at`       | datetime |                                         |


### `evm_transaction`

Describes a chain transaction related to a payment order.

| Field              | Type     | Notes                                |
|--------------------|----------|--------------------------------------|
| `id`               | UUID     | Primary key                          |
| `order_id`         | UUID     | FK to `order`                        |
| `block_number`     | int      |                                      |
| `status`           | enum     | `pending`, `confirmed`, `reverted`  |
| `raw_data`         | JSON     | Optional metadata from chain         |
| `created_at`       | datetime |                                      |

---

We define **order** and **evm_transaction** to implement more flexible payment workflow in which we can use different payment strategies around one core entity **order**.

## API (Draft)

### 🔐 All routes are Authenticated 

#### `GET /deployer/initiate-payment`

#### `POST /deployer/transaction`

#### `GET /deployer/order/status?order_id=<uuid>`

#### `GET /deployer/daemon/:orgId/:serviceId`

#### `GET /deployer/daemons/:userId`

#### `DELETE /deployer/daemon:orgId/:servicId`


### Lambas

As HaaS api for managing daemons is async, we need to implement additional lambas for handling async invocations.

#### stop-haas-daemon

#### start-haas-daemon (deployer consumer lambda)

#### cron-daemon-checker (used for checking daemon pods status and updating it in hosted_daemon table) 



