#!/bin/bash

MYSQL_BOOT_WAIT_TIMEOUT=30
MYSQL_USER=unittest_root
MYSQL_PASS=unittest_pwd
MYSQL_DB=unittest_db
MYSQL_HOST=127.0.0.1
SCRIPTS=./sql_script/*

function mysqlRunning() {
  # Make sure that user, pass, and testdb are stored somewhere else such as env variables.
  mysql -h ${MYSQL_HOST} -u ${MYSQL_USER} -p${MYSQL_PASS} -e "SHOW TABLES;" ${MYSQL_DB} > /dev/null 2>&1
  echo $?
};

printf "waiting for mysql"
for i in $(seq 0 ${MYSQL_BOOT_WAIT_TIMEOUT})
do
    if [[ $(mysqlRunning) -eq 1 ]]
    then
      printf "."
      if [[ ${i} -eq ${MYSQL_BOOT_WAIT_TIMEOUT} ]]
      then
        echo "mysql boot timeout"
        exit 1
      fi
      sleep 1
    else
      echo "mysql running"
      break
    fi
done

mysql -h ${MYSQL_HOST} -u ${MYSQL_USER} -p${MYSQL_PASS} ${MYSQL_DB} < ./sql_script/unittest_contract_api.sql
mysql -h ${MYSQL_HOST} -u ${MYSQL_USER} -p${MYSQL_PASS} -e "SHOW TABLES;" ${MYSQL_DB}
