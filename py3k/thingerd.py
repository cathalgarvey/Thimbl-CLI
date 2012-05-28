#!/usr/bin/env python3
# fingerd.py
# Original code by A.M. Kuchling ( amk@amk.ca )
# Adapted to use with thimbl by Mark Carter ( as part of https://github.com/blippy/Thimbl-CLI )
# Updated to py3k & somewhat expanded by Cathal Garvey ( http://www.cathalgarvey.me )
# The finger protocol is a very simple TCP-based protocol; the client
# sends a single line containing the name of the user whose
# information is being requested, followed by a newline.
# Information about the user should then be sent over the socket
# connection to the client.  In this implementation, the server simply
# tells you who you've fingered; you'd probably want it to retrieve
# information from the user's home directory or a database of some sort.
#
# ORIGINAL ANNOTATION
#  The original code can be downloaded from
#  http://www.amk.ca/files/simple/fingerd.txt
#  27-Nov-2010 - In an email correspondence, Andrew Kuchling stated that
#  this is source code is available under an MIT licence shown at:
#  http://www.opensource.org/licenses/mit-license.php
#  I have incorporated that code in with this source file so as to spell it
#  out. Many thanks to Andrew for posting his code and making it available
#  for free use.
#
# MARK CARTER'S ANNOTATION
# thingerd
# thimbl finger daemon
# Author: 		mcturra2000@yahoo.co.uk
# Date: 		2010-11-20
# Copyright: 		Public Domain
# Version: 		0.0
# Manual section: 	8
# Manual group: 	thimbl
# SYNOPSIS
# thingerd.py
# DESCRIPTION
# thingerd (actually thingerd.py, but hereafter referred to as thingerd) is
# a replacement finger daemon, written in Python, that is tailored
# specifically for Thimbl. It is designed to take the hassle out of installing
# and configuring a finger daemon. It exposes very little information about
# the operating environment, and may this be considered beneficial from a
# security standpoint. It was also designed to be used, eventually, from Windows.
# It therefore tries not to rely too much on UNIX infrastructre.
# thingerd was not written by an expert in protocol writing, SO YOU SHOULD
# EXERCISE CAUTION IN ITS USE. I welcome feedback from security experts as to
# how the program can be made more secure.
# 
# The MIT License, as applied to original fingerd.py code portions:
# Copyright (c) 2010 A.M. Kuchling
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import os
import platform
import socketserver

textencoding = 'utf-8'

class FingerHandler(socketserver.StreamRequestHandler): #This class inherits from StreamRequestHandler
    def handle(self):
        # Read a line of text, limiting it to 512 bytes.
        # This will prevent someone trying to crash the server machine
        # by sending megabytes of data.
        username=self.rfile.readline(512)

        # Remove any leading and trailing whitespace, including the
        # trailing newline.
        username = username.strip()
        usernamereq = str(username,textencoding)
        print("Request made for user: " + usernamereq)
        if '@' in usernamereq:
            print("Requested username contains '@' symbol: requesting delegated finger process?")
            print("Refusing delegated finger process: Sent message 'Sorry, this server doesn't support delegated fingering!'")
            Refusal = bytes("Sorry, this server doesn't support delegated fingering!",textencoding)
            self.wfile.write(Refusal)
        else:
            # Call the method to get the user's information, and return it
            # to the client.  The SocketServer classes make self.wfile
            # available to send data to the client.
            #print("Attempting to get information about requested user..")
            info = self.find_user_info(username)
            #print("Debug: 'info' = " + str(info))
            info = bytes(info,textencoding)
            print("Sending information about the user.")
            self.wfile.write(info) # Used to have no "bytes()" casting; needed in py3k for streaming.

    def find_user_info(self, username):
        "Return a string containing the desired user information."
        # This method takes a string containing the username, and returns another string containing desired information.
        # You can subclass the FingerHandler class and override this method with your own to produce customized output.

        username = str(username,textencoding)
        text = "You fingered the user '{0}'\n".format(username)

        # work out user's home name
        #if platform.uname()[0] == "Windows":
        #    home_dir = os.path.expanduser('~')
        #    text += "Windows kludge applied - single user mode only.\n"
        #else:
        #    home_dir = os.path.expanduser('/home/{0}'.format(username))
        home_dir = os.path.expanduser('~{0}'.format(username) )
            
        plan_file = os.path.join(home_dir, ".plan")
        print("Seeking plan file: " + plan_file)
        if os.path.isfile(plan_file):
            with open(plan_file, encoding=textencoding, mode='r') as UserPlanFile:
                text += "Plan:\n" + UserPlanFile.read()
        return text

# If this script is being run directly, it'll start acting as a finger
# daemon.  If someone's importing it in order to subclass
# FingerHandler, that shouldn't be done.  The following "if" statement
# is the usual Python idiom for running code only in a script.

if __name__=='__main__':
    # Create an instance of our server class
    print("Starting Finger Server/Daemon")
    server=socketserver.TCPServer( ('', 79), FingerHandler)
    # Enter an infinite loop, waiting for requests and then servicing them.
    server.serve_forever()
