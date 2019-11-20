set -ex

aws s3 cp ${s3_bucket} wallets/config.py

export PYTHONPATH=$PWD

python wallets/create_channel_event_consumer.py