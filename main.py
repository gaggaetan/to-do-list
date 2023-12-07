import sqlite3
import socket
import subprocess

from sqlite3 import Error
from libs.Class_db import *
import subprocess
import os
import platform




if __name__ == '__main__':
    nbr_client : int = input("Combien de client avez vous besoin au début : ")


    #clear cmd
    if platform.system() == 'Windows':
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)


    db = To_do_list_DB("DB\pythonsqlite.db")

    db.new_clients(nbr_client)


    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind(('', 15555))
    socket.listen()


    while True:

        client, address = socket.accept()
        print("{} connected".format(address))

        response = client.recv(100000).decode()

        if response == "stop SQLite database":
            client.close()
            socket.close()
            print("close db")
            db.update_client_end_db()
            print("close clients")
            break
        if response.split(" ")[0] == "SELECT":
            result = db.execute_sql_select(response)
            client.send(str(result).encode())
        elif response.split(" ")[0] == "INSERT":
            result = db.execute_sql_insert(response)
            client.send(str(result).encode())
            db.update_client_new_task()
        elif response.split(" ")[0] == "DELETE":
            result = db.execute_sql_delete(response)
            db.update_client_new_task()
        else :
            print(f"Une requete SQL à été fait avec autre chose que INSERT/SELECT/DELETE, la voici :\n{response}")


    print("close")
    client.close()
    socket.close()






