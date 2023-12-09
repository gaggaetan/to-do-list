"""
Ce fichier contient la class client.

Elle permet de faire toutes les actions qu'un client doit s'avoir faire

# pylint: disable=C0103
"""


import cmd
import socket
import threading
import subprocess
import platform
import re
import ast

from colorama import Fore, Style, init



def l_bright(value):
    """
    Met le texte en lumineux
    """
    return f"{Style.BRIGHT}{value}{Style.NORMAL}"

def l_cyan(value):
    """
    Met le texte avec la couleur cyan
    """
    return f"{Fore.CYAN}{value}{Style.RESET_ALL}"

def l_red(value):
    """
    Met le texte avec la couleur rouge
    """
    return f"{Fore.RED}{value}{Style.RESET_ALL}"

def l_underline(value):
    """
    Souligne le texte
    """
    return f"\033[4m{value}\033[0m"



#reset/initialiser colerma
init(autoreset=True)

class Client(cmd.Cmd):
    """
    Class pour la DB
    """

    prompt = ">>"

    # ------------- initalisation de l'interpreteur -------------
    def __init__(self, port_id_to_update):
        """
        initialise le client dans la DB et le met à l'écoute en cas de changement
        dans la DB
        """

        super().__init__()
        self.socket = None
        self.pers_id = None

        #récupere le nom du client
        self.client_name = input("Quel votre nom & prenom :")

        #dit si il y a un caractere spécial dans le nom (none = pas de caractères spécial)
        name_validation_special_characters = re.search(r'["\'!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]',
                                                       self.client_name)


        #met dans un tableau les liste de caractrers ou il y a :
        #un ou plusieurs caractères puis un espace puis un ou plusieurs caractères
        name_validation_one_space_at_least = re.findall(r'\w+\s\w+', self.client_name)
        while (name_validation_special_characters is not None
               or len(name_validation_one_space_at_least) == 0)  :

            #afficher les erreurs de nom
            if name_validation_special_characters is not None :
                print(l_red('Veuillez écrire votre nom et prenom sans aucun caractère spéciaux !'))
            if len(name_validation_one_space_at_least) == 0 :
                print(l_red('Veuillez écrire votre nom et prenom avec un espace entre les deux !'))

            self.client_name = input("Veuillez réintroduite votre nom & prenom :")
            name_validation_special_characters = re.search(r'["\'!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]',
                                                           self.client_name)
            name_validation_one_space_at_least = re.findall(r'\w+\s\w+', self.client_name)


        #Récupere le numéro du port qui va devoir écouter pour savoir s'il y a une changemt
        #fait par la DB, et il envois donc un socket
        self.port_id_to_update = int(port_id_to_update)


        #écouter la db pour savoir q'il ya une un changement avec le numero de port
        self.listen_to_change_in_db()

        #création de la personne dans la base de données
        self.create_client()

    def emptyline(self):
        """
        Dit ce qu'il se passe si le client introduit rien dans son interpreteur
        """

        print("Veuillez introduire quelque chose :")

    # ------------- conectiion/déconection -------------


    def open_connection(self):
        """
        Initialise la connection vers le main
        """

        hote = "localhost"
        port = 15555

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((hote, port))


    def end_connection(self):
        """
        Ferme la connection vers le main
        """

        self.socket.close()

    # ------------- utilities -------------
    def create_client(self):
        """
        Crée le client dans le DB
        """

        #ouvre la connection de socket
        self.open_connection()
        #envois la requete sql pour ajouter le client dans la DB
        self.socket.send(f"INSERT INTO personnes(personnes) VALUES('{self.client_name}')".encode())

        #recupere id du client dans la DB et la sauve dans le client
        self.pers_id = self.socket.recv(255).decode()

        #ferme la connection de socket
        self.end_connection()


    def show_to_do_list(self):
        """
        Crée le client dans le DB
        """

        #ouvre la connection de socket
        self.open_connection()

        #envois la requete sql
        self.socket.send("SELECT t1.to_do, t2.personnes, t1.id FROM to_do_list as t1 join"
                         " personnes as t2 on t1.pers_id = t2.pers_id".encode())

        self.clear_screen()

        print("Vous etes bien connecter à la base de données 'To-do list',"
              "vous pouvez executer ces commandes pour interagir avec la base de donnes :\n"
              f"    - {l_cyan('new_task arg1')}       => pour ajouter une nouvelle tache.\n"
              f"    - {l_cyan('remove arg1')}         => pour elever une tache avec son id\n"
              f"    - {l_cyan('stop')}                => pour arreter le programme.\n"
              f"    - {l_cyan('new_client')}          => pour avoir un nouveau client.\n"
              f"    - {l_cyan('end_db')}              => pour arreter la database.\n")

        #print les taches qu ela db contient suite à la réponse de la requete
        print(l_underline("Votre liste de taches :"))
        response_str = self.socket.recv(100000).decode()
        response_tab = ast.literal_eval(response_str)
        for i, task_info in enumerate(response_tab, start=1):
            print(f"{i}) {task_info[0]} BY {task_info[1]} (task id = {task_info[2]})")

        #ferme la connection du socket
        self.end_connection()

    def clear_screen(self):
        """
        Clear the cmd screen
        """
        # clear cmd
        if platform.system() == 'Windows':
            subprocess.run("cls", shell=True, check=True)
        else:
            subprocess.run("clear", shell=True, check=True)

    # ------------- écoute le changement dans la DB -------------
    def listen_to_change_in_db(self):
        """
        Crée le thread qui : écoute le port sur lequel la base de données pourrait envoyer un signal
        indiquant qu'il y a des changements de son côté
        """

        def listen_to_change_in_db_thread():
            """ Thread qui : écoute le port sur lequel la base de données pourrait envoyer un signal
            indiquant qu'il y a des changements de son côté
            """

            #initialise l'écoute du serveur
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('', self.port_id_to_update))
            server_socket.listen()

            #écoute le port sans fin
            while True:
                client, _ = server_socket.accept()

                response = client.recv(100000).decode()

                #en cas de update de la liste de taches, on l'update sur l'interface client
                if response == "update":
                    self.show_to_do_list()

                #si un client à éteint la db, cela ferme les socket du client et préveint le client
                if response == "end_db":
                    print("the db has shut down")

        #utilise un thread pour éviter que le client ne puisse plus interagir avec
        #le porgramme interactif pricipal (car quand on écoute sur un port on ne peut plus rien
        # faire d'autre du au while)
        thread = threading.Thread(target=listen_to_change_in_db_thread, daemon=True)
        thread.start()

    # ------------- methodes que le client peut lancer par le porgramme interactif -------------

    def do_new_task(self, arg): # pylint: disable=unused-argument
        """
        Crée le thread qui : envois une nouvelle taches que la DB doit rajouter
        """

        def do_new_task_thread(arg_thread):
            """
            Thread qui : envois une nouvelle taches que la DB doit rajouter
            """
            #ouvre la connection de socket
            self.open_connection()
            #envois la requete sql
            self.socket.send(f"INSERT INTO to_do_list(to_do, pers_id) VALUES('{arg_thread}',"
                             f"'{self.pers_id}')".encode())

            #ferme la connection du socket
            self.end_connection()

        if re.search(r"[']", arg) is None :
            #utilise un thread pour que le client puisse continuer à interagir avec le porgramme
            # sans devoir attendre la fin de la requete
            thread = threading.Thread(target=do_new_task_thread, args=(arg,), daemon=True)
            thread.start()
        print(l_red('Veuillez ne pas utiliser de \' dans votre commande.'))

    def do_remove(self, arg): # pylint: disable=unused-argument
        """
        Crée le thread qui : supprime une tache de la DB à partir de son id
        """
        def do_remove_thread(arg_thread):
            """
            Thread qui : supprime une tache de la DB à partir de son id
            """

            #ouvre la connection de socket
            self.open_connection()

            #envois la requete sql
            self.socket.send(f"DELETE FROM to_do_list as t1 WHERE t1.id = {arg_thread}".encode())

            #ferme la connection du socket
            self.end_connection()

        if re.search(r"[']", arg) is None :
            #Utilise un thread pour que le client puisse continuer à interagir avec le porgramme
            # sans devoir attendre la fin de la requete
            thread = threading.Thread(target=do_remove_thread, args=(arg,), daemon=True)
            thread.start()

        print(l_red('Veuillez ne pas utiliser de \' dans votre commande.'))


    def do_end_db(self, arg): # pylint: disable=unused-argument
        """
        Crée le thread qui : dit à la DB de s'éteindre
        """

        def do_end_db_thread():
            """
            Thread qui : dit à la DB de s'éteindre
            """


            #ouvre la connection de socket
            self.open_connection()

            #envois la requete sql
            self.socket.send("stop SQLite database".encode())

            #ferme la connection du socket
            self.end_connection()

        #Utilise un thread pour que le client puisse continuer à interagir avec le porgramme
        # sans devoir attendre la fin de la requete
        thread = threading.Thread(target=do_end_db_thread, daemon=True)
        thread.start()


    def do_stop(self, arg): # pylint: disable=unused-argument
        """
        Ferme le porgrame interactif du client (en retournant True)
        """

        print("End of client")
        return True

    def do_new_client(self, arg): # pylint: disable=unused-argument
        """
        Crée le thread qui : envois un socket à la db demandantde créer un nouveau client
        """

        def do_new_client_thread():
            """
            Thread qui : envois un socket à la db demandantde créer un nouveau client
            """

            #ouvre la connection de socket
            self.open_connection()

            #envois la requete sql
            self.socket.send("NEW_CLIENT".encode())

            #ferme la connection du socket
            self.end_connection()

        #Utilise un thread pour que le client puisse continuer à interagir avec le porgramme
        # sans devoir attendre la fin de la requete
        thread = threading.Thread(target=do_new_client_thread, daemon=True)
        thread.start()



if __name__ == '__main__':
    interpreteur = Client(15600)
    interpreteur.cmdloop()
