import socket

hote = "localhost"
port = 15555

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((hote, port))
print("Connection on {}".format(port))

socket.send(("SELECT t1.id, t2.pers_id, t2.personnes FROM to_do_list as t1 join personnes as t2 on t1.pers_id = t2.pers_id").encode())

response_str = socket.recv(1024).decode()
for i in eval(response_str) :
    print(i)



print("Close")
socket.close()