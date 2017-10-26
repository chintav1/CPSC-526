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

    
    connection, s = server_socket.accept()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER, DST_PORT))

    
    data = ""

    while True:
        # sending data
        data = connection.recv(1024)
        client_socket.send(data)
        
        dataDecoded = data.decode("utf-8")
        dataLines = dataDecoded.split("\r\n\r\n")

        for dataLine in dataLines[0].split("\n"):
            print("<-- ", dataLine)

        # receiving data
        data = client_socket.recv(1024)
        connection.send(data)
        
        dataDecoded = data.decode("utf-8")
        dataLines = dataDecoded.split("\r\n\r\n")

        for dataLine in dataLines[0].split("\n"):
            print("--> ", dataLine)
      
        break;

    

	

    
        


if __name__ == "__main__":
   
    HOST,SRC_PORT = "localhost", int(sys.argv[len(sys.argv) - 3])
    server = socketserver.ThreadingTCPServer((HOST, SRC_PORT), MyTCPHandler)
    server.serve_forever()

   



