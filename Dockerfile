FROM python:3.6-slim

WORKDIR /usr/src/app
RUN apt-get update && \
    apt-get -y install bash gcc
COPY wallets/requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt
COPY wallets/ wallets/
COPY common/ common/

ENTRYPOINT bash wallets/bootstrap.sh