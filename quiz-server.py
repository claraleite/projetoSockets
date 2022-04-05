from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from time import sleep
import random

def read_file(nameFile):
    file = open(nameFile,'r')
    quizQuest = []
    for line in file:
        quest, answer = line.split(",")
        quizQuest.append((quest,answer.rstrip().lower()))
    return quizQuest

def init_server(address):
    UDPServerSocket = socket(AF_INET, SOCK_DGRAM)
    UDPServerSocket.bind((address))
    return UDPServerSocket

def listen(socket, game):
    print("Aguardando mensagem...")
    while game.isRolling:
        msg, end = socket.recvfrom(1024)
        print(f'{msg.decode()} de {end}',end= '\n\n')
        if end in game.players and game.isRolling:
            if game.isOpen:
                game.checkAnswer(msg.decode().lower(), end)
        else:
            game.newPlayer(end,msg.decode())  


def send_message(socket,address, message):
    socket.sendto(message.encode(), (address))

class Game:
    def __init__(self, socket, dataQuest) -> None:
        self.socket = socket
        self.dataQuest = dataQuest
        self.isRolling = True
        self.isFull = False
        self.isOpen = False
        self.players = {}
        self.currentRound = 0
        self.listQuest = []
        self.numPlayers = 0
        self.maxPlayers = 2
        self.numQuest = 3
        self.timeLimit = 10

    def start(self):
        self.selectQuest()
        for i in range(self.numQuest):
            self.round(i)

    def newPlayer(self, address, name):
        if self.numPlayers < self.maxPlayers:
            self.players[address] = [name,{},0]
            self.numPlayers += 1
            send_message(self.socket,address, "\nVocê entrou no jogo!")
            if self.numPlayers >= self.maxPlayers:
                self.isFull = True
        else:
            self.isFull = True
            send_message(self.socket,address, "\nEssa rodada já está cheia")

    def ranking(self):
        ranking=[]
        for key in self.players:
            ranking.append((self.players[key][0],self.players[key][2]))
        ranking.sort(key = lambda x: x[1],reverse=True)
        for line in ranking:
            print(line)

    def selectQuest(self):
        randomlist = random.sample(range(0,len(self.dataQuest)), self.numQuest)
        for i in randomlist:
            self.listQuest.append(self.dataQuest[i])
        print(self.listQuest)

    def round(self, round):
        self.isOpen = True
        for key in self.players:
            quest, ans = self.listQuest[round]
            send_message(self.socket,key, quest)
            self.players[key][1][self.currentRound] = [0]
        self.timer()
        self.currentRound+=1

    def checkAnswer(self, answer, playerKey):
        self.players[playerKey][1][self.currentRound].append(answer)
        if answer == self.listQuest[self.currentRound][1]:
            self.players[playerKey][2] += 25
            self.isOpen = False
        else:
            self.players[playerKey][2] -= 5
    
    def timer(self):
        cycles=0
        while self.isOpen:
            sleep(1)
            cycles+=1
            if cycles>=self.timeLimit:
                self.isOpen = False
        self.isOpen = False    
        for key in self.players:
            if len(self.players[key][1][self.currentRound]) == 1:
                self.players[key][2] -= 1
        

def main():
    questData = read_file('perguntas.txt')
    address = ('localhost',9500)
    socket = init_server(address) 
    index = 0 
    quiz = []
    quiz.append(Game(socket, questData))
    Thread(target=listen, args=(socket,quiz[index],)).start()

    while quiz[index].isFull == False:
        sleep(2)

    #quiz[index].ranking()
    quiz[index].start()
    #sleep(120)
    quiz[index].ranking()
    quiz[index].isRolling = False
    index+=1
    

if __name__ == '__main__':
   main()