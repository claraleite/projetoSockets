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
        self.server.bind(address)
        self.server.listen()
        self.pasta_inspecionada = folder
        self.pasta_erros = error

        try:
            os.mkdir(self.pasta_inspecionada)
        except FileExistsError:
            pass
        idx=0
        self.lista_de_documentos = os.listdir(self.pasta_inspecionada)
        for item in self.lista_de_documentos:
            if item[0]==".":
                del(self.lista_de_documentos[idx])
            idx+=1
                
        print(self.lista_de_documentos)

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
                    request = self.formatMessage(msg_http)
                    print(request)
                    if request.path == '/':
                        self.returnIndex(socket, self.lista_de_documentos, '')

                    elif request.path[1:].split('/')[0] not in self.lista_de_documentos:
                        self.returnErro(socket, 404)
                        print('erro 404\n')

                    elif request.version.split('/')[1] != '1.1':
                        self.returnErro(socket, 505)
                        print('erro 505\n')

                    else:
                        self.returnContent(request, socket)
                        print('200 ok\n')
                    
                except:
                    print('erro 400\n')
                    self.returnErro(socket, 400)             

    def formatMessage(self,msg_http): #Trata a message recebida e retorna um objetivo do tipo Request
        msg_http_tratada = msg_http.split('\r\n')[0].split(' ') #Cria fileList com primeira linha do header
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
        response += f'Server: {self.address[0]} (Windows)\r\n'
        response += f'Content-Length: {os.path.getsize(file)}'
        response += 'Content-Type: text/html\r\n'
        response += '\r\n'
        arq = open(file, 'r')
        content = arq.read()
        print(content)
        response += content
        socket.send(response.encode())
        print("enviado")

    def returnIndex(self, socket, fileList, file):
        header = ''
        header += 'HTTP/1.1 200 OK\r\n'
        header += f'Date: {formatdate(localtime=False, usegmt=True)}\r\n'
        header += f'Server: {self.address[0]} (Windows)\r\n'
        header += 'Content-Type: text/html\r\n'
        header += '\r\n'
        payload = '<!DOCTYPE html>\r\n'
        payload += '<html>\r\n'
        payload += '<head>\r\n'
        payload += '<title> Index ServidorWEB </title>\r\n'
        payload += '<meta charset="UTF-8">\r\n'
        payload += '</head>\r\n'
        payload += '\r\n'
        payload += '<body>\r\n'
        payload += '<h1>Documentos disponiveis <h1>\r\n'
        if fileList:
            payload += '<ul>\r\n'
            for item in fileList:
                if item.split(".")[0] != 'favicon':
                    payload += f' <li><a href="http://{self.address[0]}:{self.address[1]}/{file}{item}"' \
                                    f'>{item.split(".")[0]}</a></li>\r\n'
            payload += '<ul>\r\n'
        payload += '</body>\r\n'
        payload += '</html>\r\n'
        print(header, payload)
        message = header+payload
        socket.send(message.encode())

    def returnContent(self, request, socket):
        file = self.pasta_inspecionada + request.path
        if request.contenttype != None:
            header = ''
            header += 'HTTP/1.1 200 OK\r\n'
            header += f'Date: {formatdate(localtime=False, usegmt=True)}\r\n'
            header += f'Server: {self.address[0]} (Windows)\r\n'
            header += f'Content-Length: {os.path.getsize(file)}\r\n'
            header += f'Content-Type: {request.contenttype}\r\n'
            header += '\r\n'
            socket.send(header.encode())
            print(header)
        try:
            arq = open(file, 'rb')
            while True:
                packet = arq.read(1024)
                if len(packet) == 0:
                    break
                socket.send(packet)
        except:
            path = file
            if self.pasta_inspecionada in path:
                path = path.split(self.pasta_inspecionada + '/')[1]
                path += '/'
            if ' ' in path:
                path = path.split(' ')
                path = '%20'.join(path)
            fileList=os.listdir(f'{file}')
            idx=0
            for item in fileList:
                if item[0]==".":
                    del(fileList[idx])
                idx+=1
            print(fileList)
            self.returnIndex(socket, fileList, path)

def readConfig(file):
    pathfolder = file.readline().split(":")[1].rstrip()
    patherror = file.readline().split(":")[1].rstrip()
    return pathfolder, patherror

def main():
    try:
        file=open('serverconfig.txt','r')
    except:
        check = False
        try:
            file=open('webserver/serverconfig.txt','r')
        except:
            print("Arquivo de configuração do servidor não encontrado.")
        else:
            check = True
    if check:
        folder,error = readConfig(file)
        address = ("localhost", 4001)
        server = Webserver(address,folder,error)
        server.start()

if __name__ == '__main__':
   main()