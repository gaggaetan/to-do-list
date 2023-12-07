import sqlite3
from sqlite3 import Error
import os
import subprocess
import threading


class To_do_list_DB:
    """ Class pour la DB """
    def __init__(self, db_file: str):
        """ Initialise les variables de la DB """
        self._db_file = db_file #dosier avec la DB
        self.nbr_client = 0 #nombre de client qui sont connectrer à la DB

    def delete_all_table_in_db(self):
        """ Supprimer les 2 tables dans la DB """

        conn = None
        try:
            #connection au serveur
            conn = sqlite3.connect(self._db_file)

            #suprimer les 2 tables
            conn.execute("DROP TABLE to_do_list")
            conn.execute("DROP TABLE personnes")
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    def create_all_table_in_db(self):
        """ Crée les tables de la DB """

        conn = None
        try:
            #connection au serveur
            conn = sqlite3.connect(self._db_file)

            #création de la DB
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
        except Error as e:
            print(e)
        finally:
            if conn:
                # ferme la connection avec la DB
                conn.close()

    def reset_db(self):
        """ Reset les tables de la DB """

        self.delete_all_table_in_db()
        self.create_all_table_in_db()
        pass

    def execute_sql_insert(self, query):
        """ Execute la requete SQL INSERT dans la DB et retourne id de l'auto incrémentation dans la DB """

        conn = None
        try:
            #connection au serveur
            conn = sqlite3.connect(self._db_file)

            cur = conn.cursor()

            #execute le code SQL dans la DB
            cur.execute(query)

            #teste si il y a un id autoincrément avec "cur.lastrowid" pour le retourner apres, aussinon il passe à la suite
            try:
                #trouver le dernier identifiant d'autoincrément
                last_id_auto_increment = cur.lastrowid

                return last_id_auto_increment
            finally:
                #commit l'instruction SQL
                conn.commit()
                pass

        except Error as e:
            print(e)
        finally:
            if conn:
                #ferme la connection avec la DB
                conn.close()

    def execute_sql_select(self, query):
        """ Execute la requete SQL SELECT dans la DB et retourne le résultat du select dans la DB """

        conn = None
        try:
            #connection au serveur
            conn = sqlite3.connect(self._db_file)

            cur = conn.cursor()

            #execute le code SQL dans la DB
            cur.execute(query)

            #retourne le résultat de la requete SLQ select
            return cur.fetchall()

        except Error as e:
            print(e)
        finally:
            if conn:
                # ferme la connection avec la DB
                conn.close()

    def execute_sql_delete(self, query):
        """ Execute la requete SQL DELETE dans la DB """

        conn = None
        try:
            #connection au serveur
            conn = sqlite3.connect(self._db_file)

            cur = conn.cursor()

            #execute le code SQL dans la DB
            cur.execute(query)
            # commit l'instruction SQL
            conn.commit()

        except Error as e:
            print(e)
        finally:
            if conn:
                # ferme la connection avec la DB
                conn.close()

    def new_clients(self, nbr_new_clients):
        """ Crée un certain nombre de nouveau client dans des nouvelle ligne de commande (cmd) """

        for i in range(int(nbr_new_clients)):

            # Chemin absolu vers le script client.py
            client_script_path = os.path.abspath("client.py")

            #Lancer un nouveau terminal avec le script client.py qui va créer un nouveau client
            subprocess.run(["start", "cmd", "/k", "python", client_script_path] + [f"{15600 + self.nbr_client}"],shell=True)
            self.nbr_client += 1

    def update_client_new_task(self):
        """ Envois une requete à tout les clients pour prévenir  qu'un nouvelle tache à été ajouter à la DB """

        def update_client_new_task_thread():
            import socket

            #envois une requete sur tout les port ou les clients sont à l'écoute
            for i in range(self.nbr_client):
                try:
                    hote = "localhost"
                    port = 15600 + i

                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.connect((hote, port))
                    server_socket.send(f"update".encode())
                    server_socket.close()
                except:
                    pass

        #utilise un thread pour éviter que le porgramme pricipale doivent attendre la fin des socket => et peut donc causer des bug
        thread = threading.Thread(target=update_client_new_task_thread)
        thread.start()

    def update_client_end_db(self):
        """ Envois une requete à tout les clients pour prévenir que la DB à été arrêter """

        def update_client_end_db_thread():
            import socket

            #envois une requete sur tout les port ou les clients sont à l'écoute
            for i in range(self.nbr_client):
                try:
                    hote = "localhost"
                    port = 15600 + i

                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.connect((hote, port))
                    server_socket.send(f"end_db".encode())
                    server_socket.close()
                except:
                    pass

        #utilise un thread pour éviter que le porgramme pricipale doivent attendre la fin des socket => et peut donc causer des bug
        thread = threading.Thread(target=update_client_end_db_thread)
        thread.start()
