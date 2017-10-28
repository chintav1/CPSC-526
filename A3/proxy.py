import socketserver
import socket,threading
import sys
import binascii

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


        # replace
        serverLines = dataServerLines[0]
        for i, args in enumerate(sys.argv):
            if args == "-replace":
                replaceFrom = sys.argv[i+1]
                replaceTo = sys.argv[i+2]
                for word in dataServerLines[0].split():
                    if word == replaceFrom:
                        serverLines = serverLines.replace(replaceFrom, replaceTo)
                print(serverLines)
                sys.stdout.flush()


        # raw
        if LOG_OPT == "-raw":
            # print data sent by server
            for dataServerLine in dataServerLines[0].split("\n"):
                print("--> ", dataServerLine)
            # print data received from client
            for dataClientLine in dataClientLines[0].split("\n"):
                print("<-- ", dataClientLine)


        # strip
        # TODO: Please look at the difference when printing server's from printing client's
        if LOG_OPT == "-strip":
            # print out server
            lines = dataServerLines[0]
            dSL = dataServerLines[0].split("\r\n")
            for char in dSL:
                if not char.isprintable():
                    lines = lines.replace(char, ".")
            print(lines)
            sys.stdout.flush()

            # print out client
            lines = dataClientLines[0]
            for char in dataClientLines[0]:
                if not char.isprintable():
                    lines = lines.replace(char, ".")
            print(lines)
            sys.stdout.flush()


        # hex
        if LOG_OPT == "-hex":
            abc = dataClientLines[0].replace("\r\n", "")
            hex(s)

def hex(s):
    i = 0
    j = 0
    ending = ""
    for n, chars in enumerate(s):
        if i == 0:
            # print the number of bytes printed
            print("%010d" % j, end="  ")
            sys.stdout.flush()
        i = i + 1
        # print the hex
        binline = binascii.a2b_qp(chars)
        hexline = binascii.hexlify(binline)
        sys.stdout.buffer.write(hexline)
        sys.stdout.flush()
        # add another character for this line
        ending = ending + chars
        if i == 8:
            # split hexes
            print("  ", end="")
            sys.stdout.flush()
        if i == 16 or n == (len(s)-1):
            # write 3rd part, then new line
            j = j + 16
            ending = "|" + ending + "|"
            if n == (len(s)-1):
                print("%44s" % (ending))
            else:
                print("  " + ending)
            sys.stdout.flush()
            ending = ""        # reset endline for new line
            i = 0
            # 26 + 16 = 42
        else:
            # put space between hexes
            print(" ", end="")
            sys.stdout.flush()





if __name__ == "__main__":

    HOST,SRC_PORT = "localhost", int(sys.argv[len(sys.argv) - 3])
    server = socketserver.ThreadingTCPServer((HOST, SRC_PORT), MyTCPHandler)
    server.serve_forever()
