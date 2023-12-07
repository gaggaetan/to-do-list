import cmd
import socket
import subprocess
import os
import platform
import threading


class Client(cmd.Cmd) :
    prompt = ">>"

    # ------------- initalisation de l'interpreteur -------------
    def __init__(self):
        super().__init__()
        self.client_name = input("Quel votre nom & prenom :")

        # clear cmd
        if platform.system() == 'Windows':
            subprocess.run("cls", shell=True)
        else:
            subprocess.run("clear", shell=True)

        print(f"Bonjour {self.client_name},\n"
              f"Vous voila connecter au nom de '{self.client_name}' dans la base de données de to_do_list\n"
              f"Vous pouvre executer ces commandes pour interagir avec la base de donnes :\n"
              f"    - new_task arg1       => pour ajouter une nouvelle tache.\n"
              f"    - remove arg1         => pour elever une tache avec son id\n"
              f"    - stop                => pour arreter le programme.\n"
              f"    - new_client          => pour avoir un nouveau client.\n"
              f"    - end_db              => pour arreter la database.\n")

        #création de votre personne dans la base de données
        self.pers_id = self.create_personne

        #afficher la to do list acutelle
        self.show_to_do_list
        pass

    @property
    def emptyline(self):
        print("Veuillez introduire quelque chose :")
    # ------------- conectiion/déconection -------------
    @property
    def create_personne(self):
        self.open_connection

        self.socket.send((f"INSERT INTO personnes(personnes) VALUES('{self.client_name}')").encode())
        pers_id = self.socket.recv(255).decode()
        self.end_connection
        return pers_id
    @property
    def open_connection(self):
        hote = "localhost"
        port = 15555

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((hote, port))
        #print("Connection on {}".format(port))
        pass

    @property
    def end_connection (self):
        #print("Connection Close")
        self.socket.close()

    @property
    def show_to_do_list (self):


        self.open_connection
        self.socket.send(("SELECT t1.to_do, t2.personnes, t1.id FROM to_do_list as t1 join personnes as t2 on t1.pers_id = t2.pers_id").encode())

        print("Votre liste de taches")
        response_str = self.socket.recv(100000).decode()
        response_tab = eval(response_str)
        for i in range(len(response_tab)):
            print(f"{i+1}) {response_tab[i][0]} BY {response_tab[i][1]} (task id = {response_tab[i][2]})")
        self.end_connection



    # ------------- query -------------
    def do_new_task(self, arg):
        def do_new_task_thread(arg):
            self.open_connection
            self.socket.send(f"INSERT INTO to_do_list(to_do, pers_id) VALUES('{arg}', '{self.pers_id}')".encode())
            self.end_connection
            self.show_to_do_list

        thread = threading.Thread(target=do_new_task_thread(arg))
        thread.start()



    def do_remove(self, arg):
        def do_remove_thread(arg):
            self.open_connection
            self.socket.send(f"DELETE FROM to_do_list as t1 WHERE t1.id = {arg}".encode())
            self.end_connection
            self.show_to_do_list
        thread = threading.Thread(target=do_remove_thread(arg))
        thread.start()

    def do_stop (self, arg):
        print("End of client")
        self.socket.close()
        return True
    def do_end_db(self, arg):

        def do_end_db_thread():
            self.open_connection
            self.socket.send(f"stop SQLite database".encode())
            self.end_connection
        thread = threading.Thread(target=do_end_db_thread())
        thread.start()



    def do_new_client(self, arg):
        # Chemin absolu vers le script client_script.py
        client_script_path = os.path.abspath("client.py")

        # Lancer un nouveau terminal avec le script client_script.py
        subprocess.run(["start", "cmd", "/k", "python", client_script_path], shell=True)



if __name__ == '__main__':
    interpreteur = Client()
    interpreteur.cmdloop()

