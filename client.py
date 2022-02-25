import socket
import threading
import sys

####this tutorial as used as a based of the task: https://www.youtube.com/watch?v=3UOyky9sEQY
#client chanel
client_channel = ""

#ask for client nickname. CTRL+C -->exit
try:
    client_nickname = input('Give your NICKNAME for the chat: ')
except:
    sys.exit()


#ask for client channel. Need to be 1 or 2
try:
    while True:
        client_channel = input('Give your CHANNEL(1 or 2) for the chat: ')
        if((client_channel == '1') or (client_channel == '2')):
          
            break
except:
    sys.exit()


#connect client to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 1234))


#getting messages from server
def getMessage():
    while True:
        #try to get message from server
        try:
            #get the message from the server
            message = client.recv(1024).decode('utf-8')
            #if message is NICKNAME-->give client nickname to server
            if(message == 'NICKNAME'):
                client.send(client_nickname.encode('utf-8'))
            #if message is CHANNEL-->give client channel to server
            if(message == 'CHANNEL'):
                client.send(client_channel.encode('utf-8'))
            #message from other clients
            else:
                print(message)

        #if error--> closing the connection
        except:
            print('Closing the connection')
            client.close()
            break

#send message to server
def sendMessage(client_channel):
    
    while True:
        try:
            #ask message from the client
            client_message = input('')
            #if wants to disconnect from server
            if(client_message == '!q'):
                client.send(client_message.encode('utf-8'))
                client.close()
                break
            #if wants to change channel
            elif(client_message == 'CH1'):
                client_channel = '1'
                client.send(client_message.encode('utf-8'))

            #if wants to change channel
            elif(client_message == 'CH2'):
                client_channel = '2'
                client.send(client_message.encode('utf-8'))
            #normal chat message
            else:
                full_message = "<CH{} {}>{}".format(client_channel,client_nickname,client_message)
                #send message to server
                client.send(full_message.encode('utf-8'))
        except:
            client.close()
            sys.exit()
            
            
            
  
    
  


#getting thread 
get_thread = threading.Thread(target=getMessage)
get_thread.start()
#sending thread
send_thread = threading.Thread(target=sendMessage, args=(client_channel))
send_thread.start()
