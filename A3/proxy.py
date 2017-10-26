import socketserver
import socket,threading
import sys



class MyTCPHandler(socketserver.BaseRequestHandler):
    
    
    LOG_OPT = sys.argv[len(sys.argv) - 4]
    SRC_PORT = int(sys.argv[len(sys.argv) - 3])
    SERVER = sys.argv[len(sys.argv) - 2]
    DST_PORT = int(sys.argv[len(sys.argv) - 1])
	

    print("Port logger running: srcPort = ",SRC_PORT, "host = ",SERVER, "dstPort = ",DST_PORT)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", SRC_PORT))
    server_socket.listen(0)

    print("here")
    connection, s = server_socket.accept()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER, DST_PORT))

    print("another ssshere")

    while True:
        data = connection.recv(1024)
        client_socket.send(data)
        sys.stdout.buffer.write(data)
        data = client_socket.recv(1024)
        connection.send(data)
        sys.stdout.buffer.write(data)

    

	

    
        


if __name__ == "__main__":
   
    HOST,SRC_PORT = "localhost", int(sys.argv[len(sys.argv) - 3])
    server = socketserver.ThreadingTCPServer((HOST, SRC_PORT), MyTCPHandler)
    server.serve_forever()

   



# for the HTTP response
# response = urllib.request.urlopen(url)

# For when new connection comes
# date = response.getheader("Date")     # record the date/time when connection was initiated
# sourceip = ""                         # source ip of originating connection
# print("New connection: ", Date, " from
# response.getheader()  # I think this should work?
