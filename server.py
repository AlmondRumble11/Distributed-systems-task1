from http import server
from os import remove
import socket
import threading


####this tutorial as used as a based of the task: https://www.youtube.com/watch?v=3UOyky9sEQY
#port and host
PORT = 1234
HOST  = '127.0.0.1'


#make a server and start it
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))
server.listen()


#list of client nicknames, ports and channels
client_ports = []
client_nicknames = []
channel_1 = []
channel_2 = []

#send message to  connected clients
def sendMessage(message):
    #print("message is "+message.decode('utf-8'))
    
    #try-expect for private message. Example message '*user* Hello there user2'. 
    try:

        #decode message and split it--> [<sender>, receiver, message]
        private = message.decode('utf-8').split("*")

        #separate message contents
        pm_sender = private[0]
        pm_message = private[2]
        pm_receiver = private[1]

        #get client index and send the message to the client
        index = client_nicknames.index(pm_receiver)
        pm_client = client_ports[index]
        pm_client.send('<PRIVATE {}>{}'.format(pm_sender, pm_message).encode('utf-8'))

        #also send the message back to sender      
        sender = message.decode('utf-8').split("*")[0].split(" ")[1].split('>')[0]
        print(sender)
        index_sender = client_nicknames.index(sender)
        pclient = client_ports[index_sender]
        ##print(pclient)
        pclient.send('<PRIVATE {}>{}'.format(pm_sender, pm_message).encode('utf-8'))
        
    #was not private message
    except:
        #try-except to send to correct channels
        try:
            #split the message to get the sender channel and name
            sender = message.decode('utf-8').split("<")
            name = sender[1].split(">")[0].split(' ')
          
            #check the sender channel
            if(name[1] in channel_1):
                channel = 1        
            else:
                channel = 2
                
            #go through the clients and send the message to correct channel
            for client in client_ports:
                
                #get the client nickname to see on which channel they are on 
                index = client_ports.index(client)
                nickname = client_nicknames[index]

                #send message to correct channels
                if((nickname in channel_1) and (channel == 1)):
                    client.send(message)
                elif((nickname in channel_2) and (channel == 2)):
                    client.send(message)
                
        #when new client has logged to ether of the channels at the start or client changes the channel
        except:
            print('SENDING TO ALL')
            #send message to all of the clients
            for client in client_ports:
                client.send(message)
            

#change client from channel 2 to channel 1
def changeChannel1(client):
    
    #getting the client nickname and adding/removing it from correct channel lists
    index = client_ports.index(client)
    nickname = client_nicknames[index]
    channel_1.append(nickname)

    #if moved to other channel send message to all of the clients
    if(nickname in channel_2):
        channel_2.remove(nickname)
        sendMessage("{} has LEFT CHANNEL 2 and JOINED CHANNEL 1".format(nickname).encode('utf-8'))

#change client from channel 1 to channel 2
def changeChannel2(client):

    #getting the client nickname and adding/removing it from correct channel lists
    index = client_ports.index(client)
    nickname = client_nicknames[index]
    channel_2.append(nickname)

    #if moved to other channel send message to all of the clients
    if(nickname in channel_1):
        channel_1.remove(nickname)
        sendMessage("{} has LEFT CHANNEL 1 and JOINED CHANNEL 2".format(nickname).encode('utf-8'))

#disconnect client from the server
def disconnectClient(client):
    #getting the index of the client in the client port list
    client_index = client_ports.index(client)
    #remove the client list and close the client connetion
    client_ports.remove(client)
    client.close()

    #get client nickname and remove it from lists
    client_nickname = client_nicknames[client_index]
    client_nicknames.remove(client_nickname)
    if(client_nickname in channel_1):
        channel_1.remove(client_nickname)
    if(client_nickname in channel_2):
        channel_2.remove(client_nickname)
    
    
    #show to other clients in the chat who has left the chat
    sendMessage("{} has left the APP".format(client_nickname).encode('utf-8'))

#handle client message 
def handleMessage(client):

    while True:
        #try to get the client message
        try:
            #get client message 
            message = client.recv(1024)
            #if client wants to disconnect
            if(message.decode('utf-8') == '!q'):
                disconnectClient(client)
                break
            #client wants to change to channel 1
            elif(message.decode('utf-8') == 'CH1'):
                changeChannel1(client)
            #client wants to change to channel 2
            elif(message.decode('utf-8') == 'CH2'):
                changeChannel2(client)
            else:
                #send message to all clients
                sendMessage(message)        
        #some error in getting or sending message
        #cut connection to client and remove from the client list
        except:
            disconnectClient(client)
            break

#handle client connetion to server
def getClient():

    print('SERVER started')

    while True:
    
        #when connects to clint gets client and its ip addrress
        client, client_address = server.accept()
        print('Connected to CLIENT:{}'.format(client_address))

        #get client nickname by using keyword and add it to list of nicknames
        client.send('NICKNAME'.encode('utf-8'))
        client_nickname = client.recv(1024).decode('utf-8')
        client_nicknames.append(client_nickname)
        
        #get client channel and add it to correct list and add client port to list
        client.send('CHANNEL'.encode('utf-8'))
        cl_channel = client.recv(1024).decode('utf-8')
        if(cl_channel == '1'):
            print('IN CHANNEL 1')
            channel_1.append(client_nickname)
        else:
            print('IN CHANNEL 2')
            channel_2.append(client_nickname)

        client_ports.append(client)
        

        #send the nickname of the client to all clients
        print('NICKNAME of the new CLIENT is:{}'.format(client_nickname))
        #tell client that connection established to server and chat info
        client.send('*********************************************************'.encode('utf-8'))
        client.send('Connected to SERVER using NICKNAME:{}\n'.format(client_nickname).encode('utf-8'))
        client.send("To disconnect write '!q' to chat\n".encode('utf-8')) 
        client.send('Use *INSERT NICKNAME* to use send private message\n'.encode('utf-8'))
        client.send('There are 2 channels(1,2). You are in channel 1. Use CH1 or CH2 to switch channel that channel.\n'.encode('utf-8'))
        client.send('*********************************************************\n'.encode('utf-8'))
        sendMessage('{} has joined the chat on CHANNEL {}'.format(client_nickname,cl_channel).encode('utf-8'))


        #start a new thread for the client that handles client messages
        client_thread = threading.Thread(target=handleMessage, args=(client, ))
        client_thread.start()
    
getClient()

