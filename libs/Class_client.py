import cmd
import socket
import threading


class Client(cmd.Cmd) :
    prompt = ">>"

    # ------------- initalisation de l'interpreteur -------------
    def __init__(self, port_id_to_update):
        super().__init__()
        self.client_name = input("Quel votre nom & prenom :")
        self.port_id_to_update = int(port_id_to_update)


        print(f"Bonjour {self.client_name},\n"
              f"Vous voila connecter au nom de '{self.client_name}' dans la base de données de to_do_list\n"
              f"Vous pouvre executer ces commandes pour interagir avec la base de donnes :\n"
              f"    - new_task arg1       => pour ajouter une nouvelle tache.\n"
              f"    - remove arg1         => pour elever une tache avec son id\n"
              f"    - stop                => pour arreter le programme.\n"
              f"    - new_client          => pour avoir un nouveau client.\n"
              f"    - end_db              => pour arreter la database.\n")

        #écouter la db pour savoir q'il ya une un changement
        self.listen_to_change_in_db

        #création de votre personne dans la base de données
        self.pers_id = self.create_personne
        pass


    def emptyline(self):
        print("Veuillez introduire quelque chose :")
        return None
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



    @property
    def listen_to_change_in_db(self):
        def listen_to_change_in_db_thread():
            import socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('', self.port_id_to_update))
            server_socket.listen()

            while True:
                client, address = server_socket.accept()

                response = client.recv(100000).decode()

                if response == "update":
                    self.show_to_do_list
                if response == "end_db":
                    server_socket.close
                    print("the db has shut down")

        thread = threading.Thread(target=listen_to_change_in_db_thread, daemon=True)
        thread.start()

    # ------------- query -------------
    def do_new_task(self, arg):
        def do_new_task_thread(arg):
            self.open_connection
            self.socket.send(f"INSERT INTO to_do_list(to_do, pers_id) VALUES('{arg}', '{self.pers_id}')".encode())
            self.end_connection

        thread = threading.Thread(target=do_new_task_thread, args=(arg,))
        thread.start()



    def do_remove(self, arg):
        def do_remove_thread(arg):
            self.open_connection
            self.socket.send(f"DELETE FROM to_do_list as t1 WHERE t1.id = {arg}".encode())
            self.end_connection
        thread = threading.Thread(target=do_remove_thread, args=(arg,))
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
        thread = threading.Thread(target=do_end_db_thread)
        thread.start()



    def do_new_client(self, arg):
        def do_new_client_thread():
            self.open_connection
            self.socket.send(f"NEW_CLIENT".encode())
            self.end_connection
        thread = threading.Thread(target=do_new_client_thread)
        thread.start()



if __name__ == '__main__':
    interpreteur = Client()
    interpreteur.cmdloop()

