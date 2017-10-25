import socketserver
import socket,threading
import sys
import urllib.request

if __name__ == "__main__":
   HOST, PORT = "localhost", int(sys.argv[1])
   server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
   print("Proxy started on port %d... ", PORT)
   server.serve_forever()


# for the HTTP response
# response = urllib.request.urlopen(url)
# self.request.sendall(bytearray("New connection: ", "UTF-8"))
# self.request.sendall(bytearray(response.getheader("Date"), "UTF-8"))
# self.request.sendall(bytearray(" from ", "UTF-8"))
# response.getheader()  # I think this should work?

