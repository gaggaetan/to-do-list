import platform
import socket
from libs.Class_db import *

if __name__ == '__main__':
    #initialise le nbr de client besoin
    nbr_client: int = input("Combien de client avez vous besoin au début : ")

    #clear cmd
    if platform.system() == 'Windows':
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)

    #initialise la db et les clients
    db = To_do_list_DB("DB\pythonsqlite.db")
    db.new_clients(nbr_client)

    #initialise l'écoute des client
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind(('', 15555))
    socket.listen()

    #écoute le port sans fin
    while True:
        client, address = socket.accept()
        print("{} est connecté".format(address))

        response = client.recv(100000).decode()

        if response == "stop SQLite database":
            client.close()
            socket.close()
            print("close db")
            db.update_client_end_db()
            print("close clients")
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
            db.new_clients(1)
            db.update_client_new_task()

        #suprimer quelque chose de la db
        elif response.split(" ")[0] == "DELETE":
            result = db.execute_sql_delete(response)
            db.update_client_new_task()

        #pas une requete connue
        else:
            print(f"Une requete SQL à été fait avec autre chose que INSERT/SELECT/DELETE, la voici :\n{response}")

    print("close")
    client.close()
    socket.close()
