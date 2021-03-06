#!/usr/bin/env python3
# Originally written for python 2.x by Mark Carter, presented here:
# http://alt-mcarter.blogspot.com/2010/11/finger-protocol-notes.html
# Converted and refactored for python3 by Cathal Garvey of cathalgarvey.me
# Intended for use with thimbl, a decentralised and standards-compliant
# microblogging standard, based on the finger protocol.
# Neither finger.py or thingerd.py are technically required to make use
# of or participate in thimbl, but offer a python-based alternative to
# existing tools.
# For information on the Finger protocol, see RFC1288:
# http://www.faqs.org/rfcs/rfc1288.html

import socket
import sys

textencoding = 'utf-8'

def PrintIfMain(string):
    'If run directly, the script prints usage info. Otherwise, it minimises output.'
    if __name__=='__main__':
        print(string)
    else:
        return None

def finger(node):
    
    # Separate out username and domain
    elements = node.split('@')
    if len(elements) == 1:
        user, host = '', elements[0] #This is deliberate, in line with RFC-742
    elif len(elements) == 2:
        user, host = elements
    else:
        return '' # Input was not in a useful format
    
    # Contact host
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5) # we get bored after N seconds
    PrintIfMain('Fingering {0} at host {1}'.format(user,host))
    socket.gethostbyname(host)
    socket.getaddrinfo(host, 79)
    s.connect((host, 79))
    PrintIfMain('Connect Finished')
    
    message = bytes(user + "\r\n", textencoding) # ASCII required by RFC 1288..
    s.send(message)
    result = ''
    while True:
        data = s.recv(1024)
        data = str(data,textencoding)
        if len(data) == 0:
            break
        result += data
    s.close()
    return result

def usage():
    print("Usage: finger.py [user@hostname]")
    exit(1)

def HandleUserArg(UserArg):
    'Checks User Argument for multiple hostnames. Returns a list of target user@host combinations.'
    if not isinstance(UserArg,str):
        print("UserArg must be a string!")
        return None
    splitquery = UserArg.split('@')
    if len(splitquery) > 2: #do stuff
        username = splitquery.pop(0)
        returnlist = []
        for hostname in splitquery:
            newquery = username + '@' + hostname
            returnlist.append(newquery)
        return returnlist
    else:
        # If not longer than 2, then it's just user@host, so return the query in a list.
        return [UserArg]

if __name__=='__main__':
    if len(sys.argv) == 2:
        userquery = str(sys.argv[1])
        # For more than utterly basic usage, will need to change how userquery is found
        for query in HandleUserArg(userquery):
            print(finger(query))
    else:
        usage()

#print(finger('cathalgarvey@127.0.0.1'))
#print(finger('dmytri@thimbl.tk'))
