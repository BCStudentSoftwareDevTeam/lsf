#!/bin/bash

mysqldump -u root -p lsf > `date +%F`-backup.sql
