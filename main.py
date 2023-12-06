import sqlite3
import socket
from sqlite3 import Error

def remove_Database(db_file):
    """ remove table from the database in the SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("DROP TABLE to_do_list")
        conn.execute("DROP TABLE personnes")
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def create_Database(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.execute("CREATE TABLE to_do_list ("
                     "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "to_do TEXT NOT NULL,"
                     "pers_id  INTEGER NOT NULL"
                     ");")
        conn.execute("CREATE TABLE personnes ("
                     "pers_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "personnes TEXT NOT NULL,"
                     "FOREIGN KEY (pers_id) REFERENCES to_do_list(pers_id)"
                     ");")
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)

        cur = conn.cursor()

        cur.execute("INSERT INTO personnes(personnes) VALUES('damien3')")
        #recuperer le dernier ID
        person_id = cur.lastrowid

        cur.execute(f"INSERT INTO to_do_list(to_do,pers_id) VALUES('test', {person_id})")
        conn.commit()

        cur.execute("SELECT t1.id, t2.pers_id, t2.personnes FROM to_do_list as t1 join personnes as t2 on t1.pers_id = t2.pers_id")
        rows = cur.fetchall()
        for row in rows:
            print(row)

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def execute_sql (db_file, query):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)

        cur = conn.cursor()

        cur.execute(query)
        conn.commit()

        cur.execute("SELECT * FROM to_do_list")
        rows = cur.fetchall()

        for row in rows:
            print(row)

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()



if __name__ == '__main__':
    #remove_Database(r"DB\pythonsqlite.db")
    #create_Database(r"DB\pythonsqlite.db")

    create_connection(r"DB\pythonsqlite.db")
    #execute_sql(r"DB\pythonsqlite.db", "INSERT INTO to_do_list(to_do,pers_id) VALUES('test',1)")
    """
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind(('', 15555))

    while True:
        socket.listen()
        client, address = socket.accept()
        print("{} connected".format(address))

        response = client.recv(1024)

        if response.decode() == "stop SQLite database":
            client.close()
            socket.close()
            print("close")
            break
        if response != "":
            print(response.decode())

    print("close")
    client.close()
    socket.close()"""






