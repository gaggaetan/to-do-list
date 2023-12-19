# pylint: disable=C0103
"""
Ce fichier contient la class ToDoListDB.

Elle permet de de lancer toutes les actions que la DB doit faire,
de la création à la mise à jour de celle ci
"""


import sqlite3
from sqlite3 import Error
import os
import subprocess
import threading
import socket
import logging

class ToDoListDB:
    """
    Class pour la DB
    """

    def __init__(self, db_file: str):
        """
        Initialise les variables de la DB
        """
        self._db_file = db_file #dosier avec la DB
        self.nbr_client = 0 #nombre de client qui sont connectrer à la DB


        logging.basicConfig(filename=r'logs\db_logs.log', level=logging.INFO,
                            format='%(asctime)s %(levelname)s : %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p')
        logging.info('The DB has started')

    def delete_all_table_in_db(self):
        """
        Supprimer les 2 tables dans la DB
        """

        conn = None
        try:
            #connection au serveur
            conn = sqlite3.connect(self._db_file)

            #suprimer les 2 tables
            conn.execute("DROP TABLE to_do_list")
            conn.execute("DROP TABLE personnes")

            logging.info('The tables of the DB have been drop correctly')
        except Error as e:
            logging.warning('The tables of the DB have not been drop correctly : %s', e)
        finally:
            if conn:
                conn.close()

    def create_all_table_in_db(self):
        """
        Crée les tables de la DB
        """

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
            logging.info('The tables of the DB have been created correctly')
        except Error as e:
            logging.warning('The table of the DB have not been created correctly : %s', e)
        finally:
            if conn:
                #ferme la connection avec la DB
                conn.close()

    def reset_db(self):
        """
        Reset les tables de la DB
        """

        self.delete_all_table_in_db()
        self.create_all_table_in_db()
        logging.info('The information in the DB have been reset correctly')

    def execute_sql_insert(self, query):
        """
        Execute la requete SQL INSERT dans la DB et retourne id de l'auto incrémentation dans la DB
        """

        conn = None
        try:
            #connection au serveur
            conn = sqlite3.connect(self._db_file)

            cur = conn.cursor()

            #execute le code SQL dans la DB
            cur.execute(query)

            logging.info('The insert statement in the DB  have workt')

            #teste si il y a un id autoincrément avec "cur.lastrowid" pour le retourner apres,
            # aussi non il passe à la suite
            try:
                #trouver le dernier identifiant d'autoincrément
                last_id_auto_increment = cur.lastrowid

                return last_id_auto_increment
            finally:
                #commit l'instruction SQL
                conn.commit()


        except Error as e:
            logging.error('The insert statement in the DB  have fail : %s', e)
            return None
        finally:
            if conn:
                #ferme la connection avec la DB
                conn.close()

    def execute_sql_select(self, query):
        """
        Execute la requete SQL SELECT dans la DB et retourne le résultat du select de la DB
        """

        conn = None
        try:
            #connection au serveur
            conn = sqlite3.connect(self._db_file)

            cur = conn.cursor()

            #execute le code SQL dans la DB
            cur.execute(query)

            logging.info('The select statement in the DB  have workt')

            #retourne le résultat de la requete SLQ select
            return cur.fetchall()


        except Error as e:
            logging.error('The select statement in the DB  have fail : %s', e)
            return None
        finally:
            if conn:
                #ferme la connection avec la DB
                conn.close()

    def execute_sql_delete(self, query):
        """
        Execute la requete SQL DELETE dans la DB
        """

        conn = None
        try:
            #connection au serveur
            conn = sqlite3.connect(self._db_file)

            cur = conn.cursor()

            #execute le code SQL dans la DB
            cur.execute(query)
            #commit l'instruction SQL
            conn.commit()

            logging.info('The delete statement in the DB have workt')

        except Error as e:
            logging.error('The delete statement in the DB  have fail : %s', e)
        finally:
            if conn:
                #ferme la connection avec la DB
                conn.close()

    def new_clients(self, nbr_new_clients = 1):
        """
        Crée un certain nombre de nouveau client dans des nouvelle ligne de commande (cmd)
        """

        for _ in range(int(nbr_new_clients)):

            #chemin absolu vers le script client.py
            client_script_path = os.path.abspath("client.py")

            #lancer un nouveau terminal avec le script client.py qui va créer un nouveau client
            subprocess.run(["start", "cmd", "/k", "python", client_script_path] +
                           [f"{15600 + self.nbr_client}"],shell=True, check=True)

            logging.info('A new client has been added: N°%s', self.nbr_client)


            self.nbr_client += 1



    def update_client_new_task(self):
        """
        Envois une requete à tout les clients pour prévenir  qu'un nouvelle tache à
        été ajouter à la DB
        """

        def update_client_new_task_thread(index):
            try:
                hote = "localhost"
                port = 15600 + index

                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((hote, port))
                server_socket.send("update".encode())
                server_socket.close()
            except socket.error:
                logging.debug('A client may have not receiv the update of the DB '
                              'or he is already gone')

        #envoie une requête sur tous les ports où les clients sont à l'écoute
        for i in range(self.nbr_client):

            #utilise un thread pour éviter que le programme principal doive attendre
            # la fin des sockets
            thread = threading.Thread(target=update_client_new_task_thread, args=(i,), daemon=True)
            thread.start()

        logging.info('All the clients have been notify that the db have be update')



    def update_client_end_db(self):
        """
        Envois une requete à tous les clients pour prévenir que la DB à été arrêter
        """

        def update_client_end_db_thread(index):
            try:
                hote = "localhost"
                port = 15600 + index

                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((hote, port))
                server_socket.send("end_db".encode())
                server_socket.close()
            except socket.error:
                logging.debug('A client may have not receiv that the DB has end '
                              'or he is already gone')


        # envoie une requête sur tous les ports où les clients sont à l'écoute
        for i in range(self.nbr_client):
            # utilise un thread pour éviter que le programme principal doive attendre
            # la fin des sockets
            thread = threading.Thread(target=update_client_end_db_thread, args=(i,))
            thread.start()

        logging.info('All the clients have been notify that the db has end')
