import sys
from libs.Class_client import Client

if __name__ == '__main__':
    script_arguments = sys.argv[1]
    print(script_arguments)

    interpreteur = Client(script_arguments)
    interpreteur.cmdloop()
