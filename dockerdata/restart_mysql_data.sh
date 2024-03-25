#!/bin/bash
rm -rf  /root/pear-admin-flask/dockerdata/mysql/data/
docker exec mysql /bin/bash -c "mysql -uroot -p335060 -e 'drop database IF EXISTS zyr_ctc_speech;CREATE DATABASE zyr_ctc_speech DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci;'"
docker exec flask /bin/sh -c "rm -rf migrations ; sh /app/start.sh"
