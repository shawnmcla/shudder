import socket
import threading
import time
import queue
from lib.cfg import config


class Irc():
    """Class which initializes and maintains an IRC connection to Twitch chat.
    Handles inbound and outbound message queues.
    """
    
    def __init__(self, msghandler):
        self.sock = socket.socket()
        self._outMessageQueue = queue.Queue()
        self._inMessageQueue = queue.Queue()
        self._msg_handler = msghandler

    def _send_message(self, msg):
        """Send the specified string as an IRC message to the bot's channel"""
        if type(msg) is str:
            message = "PRIVMSG #{} : {}\r\n".format(config['channelName'], msg).encode("utf-8")
            self.sock.send(message)

    def _pong(self):
        """Reply to PINGs from the server."""
        self.sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

    def _connect_to_server(self):
        """Connect to the IRC server"""
        self.sock.connect((config['host'], config['port']))
        self.sock.send("PASS {}\r\n".format(config['password']).encode("utf-8"))
        self.sock.send("NICK {}\r\n".format(config['username']).encode("utf-8"))
        self.sock.send("JOIN #{}\r\n".format(config['channelName']).encode("utf-8"))
        if config['messageOnConnect']:
            self._send_message(config['connectMessage'])

    def _get_out_queue_count(self):
        """Get the number of elements in the outbound queue."""
        return self._outMessageQueue.qsize()

    def _get_in_queue_count(self):
        """Get the number of elements in the inbound queue."""
        return self._inMessageQueue.qsize()

    def queue_out_messages(self, *messages):
        """Queue one or more messages to be sent."""
        for msg in messages:
            if type(msg) is str:
                self._outMessageQueue.put(msg)

    def queue_in_messages(self, *messages):
        """Queue one or more messages to be processed."""
        for msg in messages:
            if type(msg) is str:
                self._inMessageQueue.put(msg)

    def _send_next(self):
        """Send the next message from the outbound queue to the server."""
        if self._get_out_queue_count()>0:
            self._send_message(self._outMessageQueue.get())

    def _receive_message(self):
        """Receive the next IRC message through the socket."""
        response = self.sock.recv(1024).decode("utf-8")
        if response == "PING :tmi.twitch.tv\r\n":
            self._pong()
            return None
        return response
    
    def _receiveLoop(self):
        """Loop infinitely to receive messages and queue them for processing."""
        print("Starting receiving thread")
        while True:
            response = self._receive_message()
            print(response.encode("utf-8"))
            if response:
                self.queue_in_messages(response)
            
    def _sendingLoop(self):
        """Loop infinitely to send messages from the outbound queue at the specified interval."""
        print("Starting sending thread")
        while True:
            self._send_next()
            time.sleep(1/config['messageRate'])        
    
    def _handlerLoop(self):
        """Loop infinitely to handle messages from the inbound queue."""
        print("Starting handler thread")
        while True:
            if self._get_in_queue_count()>0:
                self._msg_handler(self._inMessageQueue.get())
            time.sleep(1/100)

    def start_bot(self):
        """Establish an IRC connection and start the various threads."""
        self._connect_to_server()
        print("Connected!")
        rcvThread = threading.Thread(target = self._receiveLoop)
        sendThread = threading.Thread(target = self._sendingLoop)
        handlerThread = threading.Thread(target = self._handlerLoop)
        rcvThread.start()
        sendThread.start()
        handlerThread.start()