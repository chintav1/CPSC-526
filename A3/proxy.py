import socketserver
import socket,threading
import sys

class MyTCPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		logOption = sys.argv[]

if __name__ == "__main__":
   
   HOST,SRC_PORT = "localhost", len(sys.argv) - 3
  
   DST_PORT = len(sys.argv) - 1 

   server = socketserver.ThreadingTCPServer((HOST, SRC_PORT), MyTCPHandler)
   print("Proxy started on port %d... ", PORT)
   server.serve_forever()

# what change?

# for the HTTP response
# response = urllib.request.urlopen(url)
# self.request.sendall(bytearray("New connection: ", "UTF-8"))
# self.request.sendall(bytearray(response.getheader("Date"), "UTF-8"))
# self.request.sendall(bytearray(" from ", "UTF-8"))
# response.getheader()  # I think this should work?
