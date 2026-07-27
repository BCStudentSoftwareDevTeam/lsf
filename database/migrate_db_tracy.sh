
export FLASK_APP="$(cd "$(dirname "$0")/.." && pwd)/app.py"

DB_DIR=tracy_migrations
flask db init -d $DB_DIR

flask db upgrade -d $DB_DIR
flask db migrate -m "Initial migration." -d $DB_DIR
flask db upgrade -d $DB_DIR
