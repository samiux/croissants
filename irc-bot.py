# Description : IRC Bot for Croissants Clients
# Purpose     : To count for the total number of Croissants users only.
#               It can do nothing other than idling at the IRC channel.
# Source      : https://www.infragistics.com/community/blogs/torrey-betts/archive/2016/04/04/create-an-irc-bot-using-python-2.aspx
#               http://chamilad.github.io/blog/2015/11/26/timing-out-of-long-running-methods-in-python/
# Modified by : Samiux (https://www.infosec-ninjas.com)
# Date        : Oct 08, 2017 GMT+8

import random
import socket
import sys
import time
import ssl
import os
import signal

reload(sys)
sys.setdefaultencoding('utf8')

server = "chat.freenode.net"
channel = "#croissants"
botnick = "ninjas-" + str(random.randint(1, 100000000))
port = 7070
wait = 60

global administrators
global nick
global completed_ubuntu
global completed_rules
global completed_auto
global completed_suricata
global completed_delete

administrators = ( "samiux" )
nick = ""
completed_ubuntu = None
completed_rules = None
completed_auto = None
completed_suricata = None
completed_delete = None

# timeout handler
def timeout_handler(num, stack):
  print("Received SIGALRM [%s]" % num)
  raise Exception("FUBAR")

# connect routine function
def connect():
  global administrators
  global nick
  global completed_ubuntu
  global completed_rules
  global completed_auto
  global completed_suricata
  global completed_delete

  last_ping = time.time()
  threshold = 5 * 60

  irc_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  irc = ssl.wrap_socket(irc_s)
  print "\nConnecting to:" + server
  irc.connect((server, port))
  irc.send("USER " + botnick + " " + botnick + " " + botnick + " :This is an idle bot\n")
  irc.send("NICK " + botnick + "\n")
  irc.send("JOIN " + channel + "\n")

  try:
    while True:
      signal.signal(signal.SIGALRM, timeout_handler)
      signal.alarm(threshold)

      if completed_ubuntu == False:
        irc.send( "PRIVMSG " + channel + " :" + "Ubuntu Update done even timeout!\n")
        completed_ubuntu = None

      if completed_rules == False:
        irc.send( "PRIVMSG " + channel + " :" + "Rules Update done even timeout!\n" )
        completed_rules = None

      if completed_auto == False:
        irc.send( "PRIVMSG " + channel + " :" + "Auto Update done even timeout!\n" )
        completed_auto = None

      if completed_delete == False:
        irc.send( "PRIVMSG " + channel + " :" + "Waste delete done even timeout!\n" )
        completed_suricata = None

      text = irc.recv(4096)
      if len(text) > 0:
        print text
      else:
        break

      # get the nickname of command issued
      nick = text.split(":")[1]
      nick = nick.split("!")[0]

      # re-join to the channel when kick after preset seconds
      if text.find( "KICK" ) != -1:
        time.sleep(wait)
        irc.send("JOIN " + channel + "\n")

      # to keep client alive
      if text.find( "PING" ) != -1:
        irc.send("PONG " + text.split()[1] + "\n")
        last_ping = time.time()

      # custom commands
      if text.find( ":!ubuntu_update" ) != -1:
        if nick in administrators:
          completed_ubuntu = False
          os.system("sudo /usr/bin/update_ubuntu")
          irc.send( "PRIVMSG " + channel + " :" + "Ubuntu Update done!\n")
          completed_ubuntu = True

      if text.find( ":!rules_update" ) != -1:
        if nick in administrators:
          completed_rules = False
          os.system("sudo /usr/bin/nsm_rules_update")
          irc.send( "PRIVMSG " + channel + " :" + "Rules Update done!\n" )
          completed_rules = True

      if text.find( ":!auto_update" ) != -1:
        if nick in administrators:
          completed_auto = False
          os.system("sudo /etc/croissants/conf.d/auto_update")
          irc.send( "PRIVMSG " + channel + " :" + "Auto Update done!\n" )
          completed_auto = True

      if text.find( ":!suricata_restart" ) != -1:
        if nick in administrators:
          completed_suricata = False
          os.system("sudo systemctl restart suricata")
          irc.send( "PRIVMSG " + channel + " :" + "Suricata Restart done!\n" )
          completed_suricata = True

      if text.find( ":!waste_delete" ) != -1:
        if nick in administrators:
          completed_delete = False
          os.system("sudo /etc/croissants/conf.d/delete_waste")
          irc.send( "PRIVMSG " + channel + " :" + "Wastes delete done!\n" )
          completed_delete = True

  except Exception as ex:
    if "FUBAR" in ex:
      print("Timeout already!  Re-connecting ....")
      pass
    else:
      print ex
      sys.exit()

  except KeyboardInterrupt:
    irc.send("QUIT :I have to go for now!\n")
    print "\n"
    sys.exit()

  finally:
    signal.alarm(0)

# main routine
if not os.geteuid()==0:
  sys.exit("You need root to run this bot!\n")
else:
  while True:
    connect()
