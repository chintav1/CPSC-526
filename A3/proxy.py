import socketserver
import socket,threading
import sys, os
import binascii
import time

def hexOption(s, arrows):
    i = 0
    j = 0
    ending = ""
    for n, chars in enumerate(s):
        if i == 0:
            # print the number of bytes printed
            print(arrows, "%010d" % j, end="  ")
            sys.stdout.flush()
        i = i + 1
        # print the hex
        binline = binascii.a2b_qp(chars)
        hexline = binascii.hexlify(binline)
        if chars == "=":
            print("3D", end="")
        else:
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
            ending = "  |" + ending + "|"
            # check if hex ends when i is not 16, if it does then extra padding
            if n == (len(s)-1):
                align = 70 - ((i*2) + ((i-1)*2) + 16)
                m = 0
                while m < align:
                    print(" ", end="")
                    m = m + 1
                print(ending)
            else:
                print(ending)
            sys.stdout.flush()
            ending = ""        # reset endline for new line
            i = 0
            # 32+14+4+10+5
        else:
            # put space between hexes
            print(" ", end="")
            sys.stdout.flush()

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
        # get time
        dt = time.localtime()
        year = str(dt[0])
        monthDict = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun", 7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}
        month = monthDict[dt[1]]
        day = str(dt[2])
        hour = str(dt[3])
        minute = str(dt[4])
        sec = str(dt[5])
        wdayDict = {0:"Mon", 1:"Tue", 2:"Wed", 3:"Thur", 4:"Fri", 5:"Sat", 6:"Sun"}
        wday = wdayDict[dt[6]]

        print("New connection: " + wday +" "+ month +" "+ day +" "+ hour+":"+minute+":"+sec+", from", end="")

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
            s = dataServerLines[0].replace("\r\n", "")
            hexOption(s, "--> ")
            print("")
            s = dataClientLines[0].replace("\r\n", "")
            hexOption(s, "<-- ")

        #autoN
        if LOG_OPT.startswith("-auto"):
            bytes = LOG_OPT.lstrip("-auto")
            #try:
            n = int(bytes)
            s = dataServerLines[0]
            counter = 0
            current_position = 0

            char_list = list(s)

            while(current_position < len(char_list)):
                print(repr(''.join(char_list[current_position:n])))
                current_position = current_position + n
                n = n + n

                
               

                






            '''except:
                print("autoN: N must be an integer")
                os._exit(1)'''









if __name__ == "__main__":

    HOST,SRC_PORT = "localhost", int(sys.argv[len(sys.argv) - 3])
    server = socketserver.ThreadingTCPServer((HOST, SRC_PORT), MyTCPHandler)
    server.serve_forever()
