#! /bin/sh

if ps -ef | grep node | grep -v 'grep --color=auto node';
then
	echo "Event Contracts Service is Running"
else
	echo "Event Contracts Service is not Running"
	exit 1
fi

if ps -ef | grep python3 | grep -v 'grep --color=auto python3';
then
        echo "Parser Handler Service is Running"
else
        echo "Parser Handler Service is not Running"
        exit 1
fi
