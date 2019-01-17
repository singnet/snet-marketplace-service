#! /bin/bash

. ./config.sh

cd /opt/snet/snet-contract-event-consumer/
nohup node contractevents.js 42 &
cd -
export PYTHONPATH=/opt/snet/snet-marketplace-service
python3 parse_events/handle_contracts.py
sleep infinity
