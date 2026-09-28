#!/bin/bash

## Check if argument was passed in
if [ "$1" != "test" ] && [ "$1" != "from-backup" ]; then
	echo "You must specify which data set you want to restore"
    echo "Usage: ./reset_database.sh [test|from-backup]"
	exit 1;
fi

cd database;

PRIVATE_DATA_REPO="git@github.com:BCStudentSoftwareDevTeam/prod-data.git"
DATA_DEST_DIR="prod-data"
APP="lsf"
BACKUP_FILE="$DATA_DEST_DIR/$APP/prod-backup.sql"

fetch_backup() {
    if [ -d "$DATA_DEST_DIR/.git" ]; then
        git -C "$DATA_DEST_DIR" fetch --quiet --depth 1 origin main &&
        git -C "$DATA_DEST_DIR" reset --quiet --hard FETCH_HEAD
    else
        git clone --quiet --depth 1 --filter=blob:none --sparse "$PRIVATE_DATA_REPO" "$DATA_DEST_DIR" &&
        git -C "$DATA_DEST_DIR" sparse-checkout set "$APP"
    fi
}

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
mysql -u root -proot --execute="CREATE DATABASE IF NOT EXISTS \`lsf\`; CREATE USER IF NOT EXISTS 'lsf_user'@'%' IDENTIFIED BY 'password'; GRANT ALL PRIVILEGES ON *.* TO 'lsf_user'@'%';"
mysql -u root -proot --execute="CREATE DATABASE IF NOT EXISTS \`UTE\`; CREATE USER IF NOT EXISTS 'tracy_user'@'%' IDENTIFIED BY 'password'; GRANT ALL PRIVILEGES ON *.* TO 'tracy_user'@'%';"

cd database

rm -rf lsf_migrations
rm -rf tracy_migrations
rm -rf migrations.json


if [ $BACKUP -eq 1 ]; then
    echo "Retrieving latest backup"

    if ! fetch_backup 2>/dev/null; then
        if [ -f "$BACKUP_FILE" ]; then
            echo "Warning: couldn't update backup from private repo; using existing local copy."
        else
            echo "Warning: couldn't access $PRIVATE_DATA_REPO (do you have access?)."
            echo "Falling back to an empty database."
            BACKUP=0
        fi
    fi
fi

echo "Creating database objects"
if [ $BACKUP -eq 1 ]; then
    echo "  from backup"
    mysql -u root -proot lsf < $BACKUP_FILE

    echo "Running in-progress.sql"
    mysql -u root -proot lsf < in-progress.sql
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
