#!/bin/bash

PRODUCTION=0
if [ "`hostname`" == 'lsf.berea.edu' ]; then
	echo "DO NOT RUN THIS SCRIPT ON PRODUCTION UNLESS YOU REALLY REALLY KNOW WHAT YOU ARE DOING"
	PRODUCTION=1
	exit 1
fi

BACKUP=0
if [ "$1" == "from-backup" ]; then
	BACKUP=1
fi

echo "Dropping databases"
mysql -u root -proot --execute="DROP DATABASE \`lsf\`; DROP USER 'lsf_user';"
mysql -u root -proot --execute="DROP DATABASE \`UTE\`; DROP USER 'tracy_user';"

echo "Recreating databases and users"
mysql -u root -proot --execute="CREATE DATABASE IF NOT EXISTS \`lsf\`; CREATE USER IF NOT EXISTS 'lsf_user'@'%' IDENTIFIED BY 'root'; GRANT ALL PRIVILEGES ON *.* TO 'lsf_user'@'%';"
mysql -u root -proot --execute="CREATE DATABASE IF NOT EXISTS \`UTE\`; CREATE USER IF NOT EXISTS 'tracy_user'@'%' IDENTIFIED BY 'root'; GRANT ALL PRIVILEGES ON *.* TO 'tracy_user'@'%';"


rm -rf lsf_migrations
rm -rf tracy_migrations
rm -rf migrations.json

echo "Creating database objects"
if [ $BACKUP -eq 1 ]; then
    echo "  from backup"
    mysql -u root -proot lsf < prod.sql
else
    echo "  empty"
    ./migrate_db.sh
fi

if [ $PRODUCTION -ne 1 ]; then
	./migrate_db_tracy.sh
fi

rm -rf lsf_migrations
rm -rf tracy_migrations
rm -rf migrations.json

# Adding data we need in all environments, unless we are restoring from backup
if [ $BACKUP -ne 1 ]; then
    python3 base_data.py
else
    echo "You have imported the production DB backup. You probably want to enable real Tracy access as well. Set FLASK_ENV to staging or production."
fi

# Adding fake data for non-prod, set up admins for prod
if [ $PRODUCTION -eq 1 ]; then
	FLASK_ENV=production python3 add_admins.py
elif [ $BACKUP -ne 1 ]; then
	python3 demo_data.py
fi
