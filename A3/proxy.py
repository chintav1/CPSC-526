import socketserver
import socket,threading
import sys
import urllib.request

class MyTCPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		logOption = sys.argv[]

if __name__ == "__main__":
   
   HOST,SRC_PORT = "localhost", len(sys.argv) - 3
  
   DST_PORT = len(sys.argv) - 1 

   server = socketserver.ThreadingTCPServer((HOST, SRC_PORT), MyTCPHandler)
   print("Proxy started on port %d... ", PORT)
   server.serve_forever()



# for the HTTP response
# response = urllib.request.urlopen(url)

# For when new connection comes
# date = response.getheader("Date")     # record the date/time when connection was initiated
# sourceip = ""                         # source ip of originating connection
# print("New connection: ", Date, " from
# response.getheader()  # I think this should work?
