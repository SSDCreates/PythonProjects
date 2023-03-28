import threading
import socket

#define host and port for server
host = '127.0.0.1'

port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port)) # bind server to host and port

server.listen()#puts server into listening mode for new connections


clients = []
nicknames = []

#broadcast method - sends message to all connected clients
def broadcast(message):
    for client in clients:
        client.send(message)

#handle method for client connections
def handle(client):
    while True:
        try:
            message = client.recv(1024) # Try to receive message from client
            broadcast(message) # send message to all clients
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat'.encode('ascii'))
            nicknames.remove(nickname)
            break

#recieve method - combines methods
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('ascii'))

        nickname = client.recv(1024).decode('ascii')

        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname of the client is {nickname}')
        broadcast(f'{nickname} has joined the chat'.encode('ascii'))
        client.send('Connected to the server'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print("Server is listening....")
receive()

