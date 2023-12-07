import sqlite3
from sqlite3 import Error
from libs.Class_client import *
import threading
import os

class To_do_list_DB:
    def __init__(self, db_file: str):
        self._db_file = db_file

    def delete_all_table_in_db(self):
        conn = None
        try:
            #connect to the server
            conn = sqlite3.connect(self._db_file)

            #delete the table
            conn.execute("DROP TABLE to_do_list")
            conn.execute("DROP TABLE personnes")
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    def create_all_table_in_db(self):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            #connect to the server
            conn = sqlite3.connect(self._db_file)

            #create the table in the database
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
                conn.close()

    def reset_db(self):
        # ajouter des try except
        self.delete_all_table_in_db()
        self.create_all_table_in_db()
        pass

    def execute_sql_insert(self, query):
        conn = None
        try:
            #connect to the server
            conn = sqlite3.connect(self._db_file)

            cur = conn.cursor()

            #execute the query
            cur.execute(query)

            # teste si il y a un id autoincrément avec "cur.lastrowid" pour le retourner apres, aussinon il pass
            try :
                #find the last autoincrément id
                last_id_auto_increment = cur.lastrowid

                #commit the sql instruction
                conn.commit()

                return last_id_auto_increment
            finally:
                pass

            conn.commit()
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    def execute_sql_select(self, query):
        conn = None
        try:
            # connect to the server
            conn = sqlite3.connect(self._db_file)

            cur = conn.cursor()

            # execute the query
            cur.execute(query)

            # return the result
            return cur.fetchall()

        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()


    def execute_sql_delete(self, query):
        print(query)
        conn = None
        try:
            # connect to the server
            conn = sqlite3.connect(self._db_file)

            cur = conn.cursor()

            # execute the query
            cur.execute(query)
            conn.commit()


        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
