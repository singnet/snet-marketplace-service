ARG BASE_IMAGE=ubuntu:18.04
FROM $BASE_IMAGE

WORKDIR /usr/src/app
COPY wallets/requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt
COPY wallets/ wallets/
COPY common/ common/

ENTRYPOINT bash wallets/bootstrap.sh