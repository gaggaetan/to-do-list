"""
Ceci est le module principal de l'application To-do List.

Il permet de lancer la DB et ses clients si demandé
"""

import platform
import socket
import re
import subprocess

from libs.class_db import ToDoListDB

if __name__ == '__main__':
    #initialise le nbr de clients besoin
    nbr_client: int = input("Combien de clients avez vous besoin au début : ")

    #regarde si le nombre de clients est bien un nombre et non autre chose
    nbr_client_verification_number = re.search(r'\b\d+\b', nbr_client)
    while nbr_client_verification_number is None :
        nbr_client: int = input("Veuillez introduire un nombre : ")
        nbr_client_verification_number = re.search(r'\b\d+\b', nbr_client)

    #clear cmd
    if platform.system() == 'Windows':
        subprocess.run("cls", shell=True, check=True)
    else:
        subprocess.run("clear", shell=True, check=True)


    #initialise la db et les clients
    db = ToDoListDB(r"DB\pythonsqlite.db")
    db.new_clients(nbr_client)
    #db.reset_db()

    #initialise l'écoute des clients
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind(('', 15555))
    socket.listen()

    #écoute le port 15555 sans fin
    while True:
        client, address = socket.accept()
        print(f"{address} est connecté")

        response = client.recv(100000).decode()

        if response == "stop SQLite database":
            client.close()
            socket.close()
            print("close db")
            db.update_client_end_db()
            break

        #selectione quelque chose dans la db pour ensuite l'affichier chez le client
        if response.split(" ")[0] == "SELECT":
            result = db.execute_sql_select(response)
            client.send(str(result).encode())

        #insert quelque chose dans la db
        elif response.split(" ")[0] == "INSERT":
            result = db.execute_sql_insert(response)
            client.send(str(result).encode())
            db.update_client_new_task()

        #nouveau client
        elif response.split(" ")[0] == "NEW_CLIENT":
            db.new_clients() #crée un client par défaut
            db.update_client_new_task()

        #suprimer quelque chose de la db
        elif response.split(" ")[0] == "DELETE":
            db.execute_sql_delete(response)
            db.update_client_new_task()

        #si ce n'est pas une requete connue
        else:
            print(f"Une requete SQL à été fait avec autre chose que INSERT/SELECT/DELETE, "
                  f"la voici :\n{response}")

    print("close")
    client.close()
    socket.close()
