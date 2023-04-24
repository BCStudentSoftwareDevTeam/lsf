from ldap3 import Server, Connection, ALL
import argparse
from peewee import DoesNotExist

from app.models.student import Student
from app.models.supervisor import Supervisor

def connect_to_server(user,password):
    server = Server ('berea.edu', port=389, use_ssl=False, get_info='ALL')
    conn   = Connection (server, user=user, password=password)
    if not conn.bind():
        print(conn.result)
        raise Exception("BindError")

    return conn

# Return the value for a key or None
# Can't use .get() because it's a ldap3.abstract.entry.Entry instead of a Dict
def get_key(entry, key):
    if key in entry:
        return entry[key]
    else:
        return None

def update_records(table, people):
    for person in people:
        bnumber = str(get_key(person, 'employeeid')).strip()
        preferred = str(get_key(person, 'givenname')).strip()

        count = table.update(preferred_name=preferred).where(table.ID == bnumber).execute()
        if count:
            print("Updating",bnumber,"name to",preferred)

def fetch_descriptions(conn, descriptions):
    conn.search('dc=berea,dc=edu',
      f"(|" + "".join(map(lambda s: f"(description=*{s}*)", descriptions)) + ")",
      attributes = ['samaccountname', 'givenname', 'sn', 'employeeid']
      )
    print(f"Found {len(conn.entries)} {descriptions} in the AD");
    return conn.entries

def main(user, password):
    connection = connect_to_server(user, password)

    staff = fetch_descriptions(connection, ['Faculty','Staff'])
    update_records(Supervisor, staff)

    students = fetch_descriptions(connection, ['Student','Pre-Student'])
    update_records(Student, students)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sync Preferred Name from LDAP')
    parser.add_argument('--user', required=True, help='LDAP Username')
    parser.add_argument('--password', required=True, help="LDAP Password")
    args = parser.parse_args()

    main(args.user, args.password)
