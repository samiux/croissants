#!/usr/bin/env python3

# Description : IRC Bot for Croissants Clients
# Purpose     : To count for the total number of Croissants users only.
#               It can do nothing other than idling at the IRC channel.
# Source      : https://www.infragistics.com/community/blogs/torrey-betts/archive/2016/04/04/create-an-irc-bot-using-python-2.aspx
#               http://chamilad.github.io/blog/2015/11/26/timing-out-of-long-running-methods-in-python/
# Modified by : Samiux (https://www.infosec-ninjas.com)
# Date        : Feb 10, 2020 GMT+8

import random
import socket
import sys
import time
import ssl
import os
import signal
import subprocess

server = "chat.freenode.net"
channel = "#croissants"
botnick = "ninjas-" + str(random.randint(1, 100000000))
port = 7070
wait = 10

administrators = ( "samiux" )
nick = ""
completed_ubuntu = None
completed_rules = None
completed_auto = None
completed_suricata = None

# connect routine function
def connect():

  global administrators
  global nick
  global completed_ubuntu
  global completed_rules
  global completed_auto
  global completed_suricata

  ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  irc = ssl.wrap_socket(ircsock)
  irc.settimeout(240)
  print ("\nConnecting to:" + server)
  irc.connect((server, port))

  irc.send(bytes(str("USER " + botnick + " " + botnick + " " + botnick + " :This is an idle bot\n"), "UTF-8"))
  irc.send(bytes(str("NICK " + botnick + "\n"), "UTF-8"))
  irc.send(bytes(str("JOIN " + channel + "\n"), "UTF-8"))

  # check connectivity
  last_ping = time.time()
  threshold = 5 * 60

  try:
    while True:

      # get the nickname of command issued
      text = irc.recv(8192).decode("UTF-8")
      text = text.strip('\n\r')
      print (text)

      nick = text.split(":")[1]
      nick = nick.split("!")[0]

      # re-join to the channel when kick after preset seconds
      if text.find( "KICK" ) != -1:
        time.sleep(wait)
        irc.send(bytes(str("JOIN " + channel), "UTF-8"))

      # to check version number of suricata
      if text.find( "CHECK_VERSION" ) != -1:
        msg = subprocess.getoutput("sudo /usr/bin/suricata -V").strip('\n\r')
        irc.send(bytes(str("PRIVMSG " + channel + " :" + msg +"\n"), "UTF-8"))

      # to say hello
      if text.find( "HELLO" ) != -1:
        irc.send(bytes(str("PRIVMSG " + channel + " :" + "Hello, I am here!\n"), "UTF-8"))

      # to ping and waiting for pong
      if text.find( "PING" ) != -1:
        irc.send(bytes(str("PONG " + text.split()[1] + "\n"), "UTF-8"))
        last_ping = time.time()

      # check if timeout
      if (time.time() - last_ping) > threshold:
        break

      # to update ubuntu
      if text.find( "UBUNTU_UPDATE" ) != -1:
        if nick in administrators:
          os.system("sudo /usr/bin/update_ubuntu")
          irc.send(bytes(str("PRIVMSG " + channel + " :" + "Ubuntu Update is done!\n"), "UTF-8"))

      # to update suricata rules
      if text.find( "RULES_UPDATE" ) != -1:
        if nick in administrators:
          os.system("sudo /usr/bin/nsm_rules_update")
          irc.send(bytes(str("PRIVMSG " + channel + " :" + "Rules Update is done!\n"), "UTF-8"))

      # to conduct auto update/upgrade
      if text.find( "AUTO_UPDATE" ) != -1:
        if nick in administrators:
          os.system("sudo /etc/croissants/conf.d/auto_update")
          irc.send(bytes(str("PRIVMSG " + channel + " :" + "Auto Update is done!\n"), "UTF-8"))

      # to restart suricata
      if text.find( "SURICATA_RESTART" ) != -1:
        if nick in administrators:
          os.system("sudo systemctl restart suricata")
          irc.send(bytes(str("PRIVMSG " + channel + " :" + "Suricata Restart is done!\n"), "UTF-8"))

  except KeyboardInterrupt:
    irc.send(bytes(str("QUIT :I have to go for now!\n"), "UTF-8"))
    print ("\n")
    sys.exit()

# main routine
if not os.geteuid()==0:
  sys.exit("You need root to run this bot!\n")
else:
  while True:
    connect()
