import socketserver
import socket,threading
import sys


class MyTCPHandler(socketserver.BaseRequestHandler):


    LOG_OPT = sys.argv[1]       # options will always be last

    SRC_PORT = int(sys.argv[len(sys.argv) - 3])
    SERVER = sys.argv[len(sys.argv) - 2]
    DST_PORT = int(sys.argv[len(sys.argv) - 1])



    print("Port logger running: srcPort=",SRC_PORT, "host=",SERVER, "dstPort=",DST_PORT)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", SRC_PORT))
    server_socket.listen(0)

    # listen for new connections
    while True:
        connection, s = server_socket.accept()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER, DST_PORT))


        # sending data
        dataServer = connection.recv(1024)
        client_socket.send(dataServer)

        # receiving data
        dataClient = client_socket.recv(1024)
        connection.send(dataClient)

        # decode server data
        dataServerDecoded = dataServer.decode("utf-8")
        dataServerLines = dataServerDecoded.split("\r\n\r\n")

        # decode client data
        dataClientDecoded = dataClient.decode("utf-8")
        dataClientLines = dataClientDecoded.split("\r\n\r\n")

        # print new connection received
        print("New connection: ", end='')
        # get time from client
        # TODO: fix date
        for dataClientLine in dataClientLines[0].split("\n"):
            if dataClientLine.split(None, 1)[0] == "Date:":
                dataClientLine = dataClientLine.split("Date: ", 2)[1]
                print(dataClientLine.split(" GMT", 1)[0], end='')
                break
        print(", from", end='')
        # get the host
        for dataServerLine in dataServerLines[0].split("\n"):
            if dataServerLine.split(None, 1)[0] == "Host:":
                dataServerLine = dataServerLine.split("Host:", 2)[1]
                print(dataServerLine.split(":",1)[0])
                break




        # raw
        if LOG_OPT == "-raw":
            # print data sent by server
            for dataServerLine in dataServerLines[0].split("\n"):
                print("--> ", dataServerLine)

            # print data received from client
            for dataClientLine in dataClientLines[0].split("\n"):
                print("<-- ", dataClientLine)


        # strip
        # TODO: WHAT EXACTLY ARE THE PRINTABLE CHARACTERS? It seems all it shows are printable
        lines = dataClientLines[0]
        if LOG_OPT == "-strip":
            # start with server
            for i, char in enumerate(dataClientLines[0]):
                if not char.isprintable():
                    lines.replace(char, ".")
            print(lines)
            sys.stdout.flush()

            













if __name__ == "__main__":

    HOST,SRC_PORT = "localhost", int(sys.argv[len(sys.argv) - 3])
    server = socketserver.ThreadingTCPServer((HOST, SRC_PORT), MyTCPHandler)
    server.serve_forever()
