import socketserver
import socket,threading
import sys, os
import binascii
import time

def hexOption(s, arrows):
    i = 0
    j = 0
    padding = 0
    ending = ""
    for n, chars in enumerate(s):
        if i == 0:
            # print the number of bytes printed
            print(arrows, "%010d" % j, end="  ")
            padding = 15
            sys.stdout.flush()
        i = i + 1
        # print the hex
        binline = binascii.a2b_qp(chars)
        hexline = binascii.hexlify(binline)
        if chars == "=":
            print("3D", end="")
            padding = padding + 2
        else:
            sys.stdout.buffer.write(hexline)
            padding = padding + len(hexline)
        sys.stdout.flush()
        # add another character for this line
        ending = ending + chars
        if i == 8:
            # split hexes
            print("  ", end="")
            sys.stdout.flush()
            padding = padding + 2
        if i == 16 or n == (len(s)-1):
            # write 3rd part, then new line
            j = j + 16
            ending = "  |" + ending + "|"
            # add padding if needed for ending to align
            m = 0
            align = 64 - padding
            while m < align:
                print(" ", end="")
                m = m + 1
            print(ending)
            sys.stdout.flush()
            ending = ""        # reset endline for new line
            i = 0
        else:
            # put space between hexes
            print(" ", end="")
            sys.stdout.flush()
            padding = padding + 1

class MyTCPHandler(socketserver.BaseRequestHandler):

    replace = False
    output = ""
    LOG_OPT = sys.argv[1]       # options will always be last
    SRC_PORT = int(sys.argv[len(sys.argv) - 3])
    SERVER = sys.argv[len(sys.argv) - 2]
    DST_PORT = int(sys.argv[len(sys.argv) - 1])
    for i, args in enumerate(sys.argv):
        if args == "-replace":
            replace = True

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

        print("\r\nNew connection: " + wday +" "+ month +" "+ day +" "+ hour+":"+minute+":"+sec+", from", end=" ")

        # get the host
        for dataServerLine in dataServerLines[0].split("\n"):
            if len(dataServerLine) > 1:
                if dataServerLine.split(None, 1)[0] == "Host:":
                    dataServerLine = dataServerLine.split("Host:", 2)[1]
                    print(dataServerLine.split(":",1)[0])
            else:
                print(SERVER)
                break





        # raw
        if LOG_OPT == "-raw":
            # print data sent by server
            for dataServerLine in dataServerLines[0].split("\n"):
                if replace:
                    output = output + "--> " + dataServerLine
                else:
                    print("--> ", dataServerLine)
            # print data received from client
            for dataClientLine in dataClientLines[0].split("\n"):
                if replace:
                    output += "<-- " + str(dataClientLine)
                else:
                    print("<-- ", dataClientLine)


        # replace
        newOutput = ""
        for i, args in enumerate(sys.argv):
            if args == "-replace":
                replaceFrom = sys.argv[i+1]
                replaceTo = sys.argv[i+2]
                for word in output.split():
                    if word == replaceFrom:
                        newOutput += newOutput.replace(replaceFrom, replaceTo)
                print(newOutput)
                sys.stdout.flush()
                if newOutput == "":
                    print(output)
                    sys.stdout.flush()

        # strip
        if LOG_OPT == "-strip":
            # print out server
            lines = dataServerLines[0]
            dSL = dataServerLines[0].split("\r\n")
            for char in dSL:
                if not char.isprintable():
                    lines = lines.replace(char, ".")
            for line in lines.split("\n"):
                print("--> ", line)
            sys.stdout.flush()

            lines = dataClientLines[0]
            dCL = dataClientLines[0].split("\r\n")
            for char in dCL:
                if not char.isprintable():
                    lines = lines.replace(char, ".")
            for line in lines.split("\n"):
                print("<-- ", line)
            sys.stdout.flush()

            # I don't think this version is correct?
            '''
            # print out client
            lines = dataClientLines[0]
            for char in dataClientLines[0]:
                if not char.isprintable():
                    lines = lines.replace(char, ".")
            print("<--", lines)
            sys.stdout.flush()
            '''

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
            try:
                n = int(bytes)
                s = dataServerLines[0]
                current_position = 0


            #while(current_position < len(s)):
            #    print(repr(''.join(s[current_position:n]))[1:-1])
            #    current_position = current_position + n
            #    n = n + n

            #    while(current_position < len(s)):
            #        print("-->", repr(''.join(s[current_position:n]))[1:-1])
            #        current_position = current_position + n
            #        n = n + n





            except:
                print("autoN: N must be an integer")
                os._exit(1)









if __name__ == "__main__":

    HOST,SRC_PORT = "localhost", int(sys.argv[len(sys.argv) - 3])
    server = socketserver.ThreadingTCPServer((HOST, SRC_PORT), MyTCPHandler)
    server.serve_forever()
