FROM ubuntu:18.04
RUN apt-get update
RUN apt-get install python3 python3-pip git -y
RUN apt-get install nodejs npm git -y
RUN mkdir -p /opt/snet/snet-marketplace-service
WORKDIR /opt/snet/snet-marketplace-service
COPY . .
RUN pip3 install -r requirement.txt
RUN npm install
RUN mv snet-contract-event-consumer /opt/snet/
WORKDIR /opt/snet/snet-contract-event-consumer
RUN npm install
WORKDIR /opt/snet/snet-marketplace-service
CMD ["sh", "parse_events.sh"]
