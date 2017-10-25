import socketserver
import socket,threading
import sys
#something
if __name__ == "__main__":
   HOST, PORT = "localhost", int(sys.argv[1])
   server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
   print("Proxy started on port %d... ", PORT)
   server.serve_forever()
