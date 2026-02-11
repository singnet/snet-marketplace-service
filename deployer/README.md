# Deployer Service

## Overview

This service is responsible for four primary workflows:

1. **Demon Management**

    Handles lifecycle of AI daemon containers (deploy, update, stop, etc.) based on smart contract events and platform integration.

2. **Payment Logic for HaaS**
   
    Validates and processes on-chain payments related to hosting AI daemon containers.

3. **Proxying Pod Information from HaaS**
   
    Provides internal APIs or event propagation for fetching and exposing pod/container status, logs, or resource metrics from infrastructure.

4. **Billing Logic for Serverless GPU (Future)**
   
    (Under development) Tracks invocation and GPU usage on serverless endpoints, integrates with billing subsystem.

5. **Metrics providing (Future)**

    (Under development) Exposes metrics for pod/container status, logs, or resource metrics from infrastructure.

---

