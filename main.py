import sqlite3
import socket
from sqlite3 import Error
from libs.Class_db import *




if __name__ == '__main__':

    db = To_do_list_DB("DB\pythonsqlite.db")
    last_id_auto_increment = db.execute_sql_insert("INSERT INTO personnes(personnes) VALUES('damien3')")
    db.execute_sql_insert(f"INSERT INTO to_do_list(to_do,pers_id) VALUES('test', {last_id_auto_increment})")
    result = db.execute_sql_select("SELECT t1.id, t2.pers_id, t2.personnes FROM to_do_list as t1 join personnes as t2 on t1.pers_id = t2.pers_id")

    """
    for row in result:
        print(row)
    """

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind(('', 15555))
    socket.listen()

    while True:

        client, address = socket.accept()
        print("{} connected".format(address))

        response = client.recv(1024)

        if response.decode() == "stop SQLite database":
            client.close()
            socket.close()
            print("close")
            break
        if response != "":
            result = db.execute_sql_select(response.decode())
            client.send(str(result).encode())
            for row in result:
                print(row)

    print("close")
    client.close()
    socket.close()






