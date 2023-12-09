"""
Ce fichier permet de créer un client et le jouer si appelé.

"""

import sys
from libs.Class_client import Client

if __name__ == '__main__':
    """ permet de creér un nouveau client """
    script_arguments = sys.argv[1]
    print(script_arguments)

    interpreter = Client(script_arguments)
    interpreter.cmdloop()
