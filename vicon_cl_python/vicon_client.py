import socket


class ViconObject():

    def __init__(self, message):

       splited = message.split(' ')
       self.frameNumber = splited[0]
       self.frameRate = splited[1]
       self.name = splited[2]

       self.translation = [x for x in splited[4:7]]
       self.rotation = [x for x in splited[7:]]

    def get_properties(self):

        text = [self.name]
        text += self.translation
        text += self.rotation
        return text


class ViconClient():
    def __init__(self, hostname, serverPort):
        self.hostname = hostname
        self.serverPort = serverPort
        self.server = None

    def connect(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.connect((self.hostname, self.serverPort))
            return True
        except:
            return False

    def read_message(self):
        message = ''
        char = self.server.recv(1).decode('utf-8')

        while True:
            if char != '\n':
                message += char
            elif len(message) == 0:
                continue
            else:
                break
            char = self.server.recv(1).decode('utf-8')

        return message

    def check_connection(self):

        try:
            self.server.send("random".encode())
            return True
        except:
            return False