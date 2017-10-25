import socketserver
import socket,threading
import sys

class MyTCPHandler(socketserver.BaseRequestHandler):
    
    
    LOG_OPT = sys.argv[len(sys.argv) - 4]
    SRC_PORT = int(sys.argv[len(sys.argv) - 3])
    SERVER = sys.argv[len(sys.argv) - 2]
    DST_PORT = int(sys.argv[len(sys.argv) - 1])
	

    print("Port logger running: srcPort = ",SRC_PORT, "host = ",SERVER, "dstPort = ",DST_PORT)

	server
if __name__ == "__main__":
   
   HOST,SRC_PORT = "localhost", int(sys.argv[len(sys.argv) - 3])
  

   

   server = socketserver.ThreadingTCPServer((HOST, SRC_PORT), MyTCPHandler)
   server.serve_forever()

# what change?

# for the HTTP response
# response = urllib.request.urlopen(url)
# self.request.sendall(bytearray("New connection: ", "UTF-8"))
# self.request.sendall(bytearray(response.getheader("Date"), "UTF-8"))
# self.request.sendall(bytearray(" from ", "UTF-8"))
# response.getheader()  # I think this should work?
