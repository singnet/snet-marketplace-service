ARG BASE_IMAGE=ubuntu:18.04
FROM $BASE_IMAGE
RUN apt-get update
RUN apt-get install python3 python3-pip git logrotate -y
RUN apt-get install nodejs npm git -y
RUN mkdir -p /opt/snet/snet-marketplace-service
RUN mkdir -p /var/log/snet-marketplace-service
RUN mkdir -p /var/log/snet-contract-event-consumer
RUN mkdir -p  /var/log/marketplace
WORKDIR /opt/snet/snet-marketplace-service
COPY . .
RUN pip3 install -r parse_events/requirement.txt
RUN npm install
RUN mv snet-contract-event-consumer /opt/snet/
RUN mv marketplace.conf contract_event.conf /etc/logrotate.d/
WORKDIR /opt/snet/snet-contract-event-consumer
RUN npm install
WORKDIR /opt/snet/snet-marketplace-service
CMD ["sh", "parse_events.sh"]
