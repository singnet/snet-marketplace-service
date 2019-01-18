#! /bin/bash

. ./config.sh

cd /opt/snet/snet-contract-event-consumer/
nohup node contractevents.js 42 > /var/log/snet-contract-event-consumer/contract.log 2>&1 &
cd -
export PYTHONPATH=/opt/snet/snet-marketplace-service
nohup python3 -u parse_events/handle_contracts.py 42 > /var/log/snet-marketplace-service/handler.log 2>&1 &
sleep infinity
