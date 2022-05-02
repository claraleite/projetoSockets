from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread

def receive():
    while True:
        msg, end = UDPSocket.recvfrom(1024)
        print()
        print(msg.decode())



UDPSocket = socket(AF_INET, SOCK_DGRAM)
print("Eu sou o cliente!")

Thread(target=receive, args=()).start()
while True:
    mensagem = input("\n>>>")

    mensagem_codificada = mensagem.encode()
    UDPSocket.sendto(mensagem_codificada, ('localhost', 9500))

