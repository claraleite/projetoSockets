from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from email.utils import formatdate
import os

prefix = {'js': 'text', 'html': 'text', 'plain': 'text', 'css': 'text',
           'png': 'image', 'jpeg': 'image', 'ex-icon': 'image', 'gif': 'image',
           'ogg': 'audio'}

class Request:
    def __init__(self, method, path, contenttype, version):
        self.method = method
        self.path = path
        self.version = version
        self.contenttype = None
        if contenttype:
            try:
                self.contenttype = prefix[contenttype] + '/' + contenttype
            except KeyError:
                self.contenttype = 'application' + '/' + contenttype

class Webserver:
    def __init__(self, address, folder, error) -> None:
        self.server = socket(AF_INET, SOCK_STREAM)
        self.address = address
        self.endereco = address[0]
        self.server.bind(address)
        self.server.listen()
        self.pasta_inspecionada = folder
        self.pasta_erros = error

        try:
            os.mkdir(self.pasta_inspecionada)
        except FileExistsError:
            pass

        self.lista_de_documentos = os.listdir(self.pasta_inspecionada)

    def start(self):
        while True:
            (socketClient, addressClient) = self.server.accept()
            Thread(target=self.listen, args=(socketClient, )).start()
    
    def listen(self, socket):
        while True:
            msg_http = socket.recv(2048).decode()
            if msg_http:
                print(msg_http)
                try:
                    especificacoes = self.formatMessage(msg_http)
                    print(especificacoes)
                    if especificacoes.path == '/':
                        self.returnIndex(socket, self.lista_de_documentos, '')

                    elif especificacoes.path[1:].split('/')[0] not in self.lista_de_documentos:
                        self.returnErro(socket, 404)
                        print('erro 404\n')

                    elif especificacoes.version.split('/')[1] != '1.1':
                        self.returnErro(socket, 505)
                        print('erro 505\n')

                    else:
                        self.returnContent(especificacoes, socket)
                        print('200 ok\n')
                    
                except:
                    print('erro 400\n')
                    try:
                        self.returnIndex(socket,os.listdir(self.pasta_inspecionada[:-1]+especificacoes.path),especificacoes.path[1:]+"/")
                    except:
                        self.returnErro(socket, 400)
                    

    def formatMessage(self,msg_http): #Trata a mensagem recebida e retorna um objetivo do tipo Request
        msg_http_tratada = msg_http.split('\r\n')[0].split(' ') #Cria lista com primeira linha do header
        print(msg_http_tratada)
        if msg_http_tratada[1] == '/' and 'index.html' in self.lista_de_documentos:
            msg_http_tratada[1] = 'index.html'
        cttp = msg_http_tratada[1].split('.')[-1]
        if cttp[0] == '/':
            cttp = None
        if cttp == 'htm':
            cttp = 'html'
        elif cttp == 'jpg':
            cttp = 'jpeg'
        elif cttp == 'ico':
            cttp = 'ex-icon'
        elif cttp == 'txt':
            cttp = 'plain'
        if '%20' in msg_http_tratada[1]:
            msg_http_tratada[1] = msg_http_tratada[1].split('%20')
            msg_http_tratada[1] = ' '.join(msg_http_tratada[1])
        print(msg_http_tratada[0], msg_http_tratada[1], cttp, msg_http_tratada[2])
        return Request(msg_http_tratada[0], msg_http_tratada[1], cttp, msg_http_tratada[2])

    def returnErro(self, socket, statusCode):
        firstLine = f'HTTP/1.1 {statusCode} '
        if statusCode == '400':
            firstLine += 'Bad Request\r\n'
        elif statusCode == '404':
            firstLine += 'Not Found\r\n'
        elif statusCode == '505':
            firstLine += 'HTTP Version Not Supported\r\n'
        file = f'{self.pasta_erros}/html{statusCode}.html'
        response = ''
        response += firstLine
        response += f'Date: {formatdate(localtime=False, usegmt=True)}\r\n'
        response += f'Server: {self.endereco} (Windows)\r\n'
        response += f'Content-Length: {os.path.getsize(file)}'
        response += 'Content-Type: text/html\r\n'
        response += '\r\n'
        arq = open(file, 'r')
        content = arq.read()
        print(content)
        response += content
        socket.send(response.encode())
        print("enviado")


    def returnIndex(self, socket, lista, arquivo):
        resposta = ''
        resposta += 'HTTP/1.1 200 OK\r\n'
        resposta += f'Date: {formatdate(localtime=False, usegmt=True)}\r\n'
        resposta += f'Server: {self.endereco} (Windows)\r\n'
        resposta += 'Content-Type: text/html\r\n'
        resposta += '\r\n'
        socket.send(resposta.encode())
        index_criado = '<!DOCTYPE html>\r\n'
        index_criado += '<html>\r\n'
        index_criado += '<head>\r\n'
        index_criado += '<title> Index ServidorWEB </title>\r\n'
        index_criado += '</head>\r\n'
        index_criado += '\r\n'
        index_criado += '<body>\r\n'
        index_criado += '<h1>Documentos disponiveis <h1>\r\n'
        if lista:
            index_criado += '<ul>\r\n'
            for documento in lista:
                if documento.split(".")[0] != 'favicon':
                    index_criado += f' <li><a href="http://{self.address[0]}:{self.address[1]}/{arquivo}{documento}"' \
                                    f'>{documento.split(".")[0]}</a></li>\r\n'
            index_criado += '<ul>\r\n'
        index_criado += '</body>\r\n'
        index_criado += '</html>\r\n'
        print(resposta, index_criado)
        socket.send(index_criado.encode())


    def returnContent(self, request, socket):
        arquivo = self.pasta_inspecionada + request.path
        if request.contenttype is not None:
            resposta = ''
            resposta += 'HTTP/1.1 200 OK\r\n'
            resposta += f'Date: {formatdate(localtime=False, usegmt=True)}\r\n'
            resposta += f'Server: {self.endereco} (Windows)\r\n'
            resposta += f'Content-Length: {os.path.getsize(arquivo)}\r\n'
            resposta += f'Content-Type: {request.contenttype}\r\n'
            resposta += '\r\n'
            socket.send(resposta.encode())
            print(resposta)
        try:
            arq = open(arquivo, 'rb')
            while True:
                parte = arq.read(1024)
                if len(parte) == 0:
                    break
                socket.send(parte)
        except PermissionError:
            caminho = arquivo
            if self.pasta_inspecionada in caminho:
                caminho = caminho.split(self.pasta_inspecionada + '/')[1]
                caminho += '/'
            if ' ' in caminho:
                caminho = caminho.split(' ')
                caminho = '%20'.join(caminho)
            self.returnIndex(socket, os.listdir(f'{arquivo}'), caminho)

def readConfig(file):
    pathfolder = file.readline().split(":")[1].rstrip()
    patherror = file.readline().split(":")[1].rstrip()
    return pathfolder, patherror

def main():
    try:
        file=open('serverconfig.txt','r')
    except:
        print("Arquivo de configuração do servidor não encontrado.")
    else:
        folder,error = readConfig(file)
        print(folder + "\n" + error)
        address = ("localhost", 4000)
        server = Webserver(address,folder,error)
        server.start()

if __name__ == '__main__':
   main()