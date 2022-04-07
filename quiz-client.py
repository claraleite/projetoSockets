from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from time import sleep

def listen(socket, quiz, addressServer):
    while quiz.gameIsOn:
        msg, address = socket.recvfrom(1024)
        if address == addressServer:
            cod, message = msg.decode().split(":")
            if int(cod) == 200:
                print()
                print(message)
                quiz.gameIsWaiting = False
            elif int(cod) == 500:
                print(message)
                endCode = "500:FIN"
                socket.sendto(endCode.encode(), addressServer)
                quiz.gameIsOn = False
                
class Game:
    def __init__(self, socket, addressServer) -> None:
        self.socket = socket
        self.addressServer = addressServer
        self.gameIsWaiting = True
        self.gameIsOn = False

    def answerQuest(self):
        while self.gameIsWaiting:
            sleep(0.1)
        while self.gameIsOn:
            mensagem = input("\n>>> ")
            mensagem = "200:" + mensagem
            self.socket.sendto(mensagem.encode(), self.addressServer)

    def startGame(self):
        serverReturn = True
        playerEnter = True
        while(playerEnter):
            mensagem = input("Digite seu nome para entrar no jogo: ")
            mensagem = "100:" + mensagem
            self.socket.sendto(mensagem.encode(), self.addressServer)
            while(serverReturn):
                print("entrou1")
                msg, address = self.socket.recvfrom(1024)
                print(msg)
                print(address)

                if address == self.addressServer:
                    print("entrou")
                    serverReturn = False
                    cod, message = msg.decode().split(":")
                    if int(cod) == 100:
                        playerEnter=False
                        self.gameIsOn = True
                        print()
                        print(message)
                    elif int(cod) == 400:
                        print()
                        print(message)
                        print("Em 1 minuto tentaremos conectar novamente!\n\n")
                        sleep(60)                     



def main():
    UDPSocket = socket(AF_INET, SOCK_DGRAM)
    addressServer = ('127.0.0.1',9500)
    print("Bem vindo ao jogo Quiz:\n")
    newGame = input("Deseja iniciar o jogo?(S/N)")
    quiz = []
    index=0
    while newGame.lower() == "s":
        quiz.append(Game(UDPSocket, addressServer))
        quiz[index].startGame()
        Thread(target=listen, args=(UDPSocket,quiz[index],addressServer,)).start()
        quiz[index].answerQuest()
        newGame = input("Deseja iniciar um novo jogo?(S/N)")


if __name__ == '__main__':
   main()

