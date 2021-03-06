#!/usr/bin/env python3
'''thimbl.py - Command-line python tools '''

import io
import datetime
import json
import pdb
import os
import re
import sys
import time
import finger # finger.py must be in same directory.

#################################################################

class Data:
    def __init__(self):
        self.load_cache()
        self.whoami = self.data['me']
        self.me = self.data['plans'][self.whoami]
    
    def __cache_filename(self):
        'Return the name of the cache file that stores all of the data'
        thimbldir = os.path.expanduser('~/.config/thimbl')
        try: os.makedirs(thimbldir)
        except OSError: pass # don't worry if directory already exists
        thimblfile = os.path.join(thimbldir, 'data1.jsn')
        return thimblfile
        
    def load_cache(self):
        'Load the data file'
        thimblfile = self.__cache_filename()
        if os.path.isfile(thimblfile):
            self.data = load(thimblfile) # Load is a function below, not a py2 carryover!
        else:
            self.setup()

    def save_cache(self):
        cache_file = self.__cache_filename()
        save(self.data, cache_file) # Save is a function below, not a py2 carryover
 
    def fetch(self):
        '''Retrieve all the plans of the people I am following'''
        for following in self.me['following']:
            address = following['address']
            if address == self.data['me']:
                print("Stop fingering yourself!")
                continue

            print('Fingering ' + address)
            try:
                plan = finger_user(address)
                print("OK")
            except AttributeError:
                print('Failed. Skipping')
                continue
            self.data['plans'][address] = plan
        print('Finished')
    
    def follow(self, nick, address):
        self.me['following'].append( { 'nick' : nick, 'address' : address } )
    
    def post(self, text):
        'Create a message, add it to messages in self.me, refresh cache.'
        timefmt = time.strftime('%Y%m%d%H%M%S', time.gmtime())
        message = { 'time' : timefmt, 'text' : text }
        self.me['messages'].append(message)
        self.save_cache()
    
    def post_file(self, filename):
        'Create a post from the text in a file'
        with open(filename, encoding = 'utf-8', mode='r') as ReadFile:
            text = ReadFile.read()
        self.post(text)
        self.save_cache()
        
    def prmess(self):
        'Print messages in reverse chronological order'
        # accumulate messages
        messages = []
        for address in list(self.data['plans'].keys()):
            plan = self.data['plans'][address]
            if 'messages' not in plan: continue
            for msg in plan['messages']:
                msg['address'] = address
                messages.append(msg)
        messages.sort(key = lambda x: x['time'])
        
        # print messages
        for msg in messages:
            # format time
            t = str(msg['time'])
            tlist = list(map(int, [t[:4], t[4:6], t[6:8], t[8:10], t[10:12], t[12:14]]))
            tstruct = datetime.datetime(*tlist)
            ftime = tstruct.strftime('%Y-%m-%d %H:%M:%S')
            text = '{0}  {1}\n{2}\n'.format(ftime, msg['address'], msg['text'])
            print(text)
        
    def following(self):
        'Who am I following?'
        followees = self.me['following']
        followees.sort(key = lambda x: x['nick'])
        for f in followees:
            print('{0:5} {1}'.format(f['nick'], f['address']))
    
    def setup(self):
        def create(address, bio, name, website, mobile, email):
            'Create data given user information'
            properties = {
                           'website' 	: website,
                           'mobile'  	: mobile,
                           'email'   	: email
                          }
            plan = {       'address' 	: address,
                           'name' 	: name,
                           'bio'	: bio,
                           'messages' 	: [],
                           'replies' 	: {},
                           'following' 	: [],
                           'properties'	: properties
                    }
            data = {       'me' 	: address,
                           'plans' 	: { address : plan }
                    }
            return data

        # Get values from interactive prompt:
        NewAddress = input('Please provide your username:\n(this should be your login and static IP, domain, or dynDNS, as in "cathalgarvey@cathalgarvey.me)\n> ')
        NewBio = input('Provide a short biography for other users:\n> ')
        NewName = input('Provide your name:\n> ')
        NewWebsite = input('Provide your website:\n> ')
        NewMobile = input('Provide your (preferably mobile) phone number:\n> ')
        NewEmail = input('Provide your email address:\n> ')
        self.data = create(NewAddress, NewBio, NewName, NewWebsite, NewMobile, NewEmail)
        self.save_cache()

    def unfollow(self, address):
        'Remove an address from someone being followed'
        def func(f): return not (f['address'] == address)
        new_followees = list(filter(func, self.me['following']))
        self.me['following'] = new_followees
    
    def __del__(self):
        #print "Data exit"
        self.save_cache()
        save(self.me, os.path.expanduser('~/.plan'))
        
#################################################################

def finger_user(user_name):
    '''Try to finger a user using finger.py, and convert the returned plan into a dictionary

    Usage e.g. jsonPlan = finger_user("dk@telekommunisten.org")
    print(jsonPlan['bio'])
    '''
    output = finger.finger(user_name) # Call the finger() function from finger.py
    getplan = re.search('^.{0,}?Plan:\s{0,}(.{0,})', output, re.MULTILINE + re.DOTALL)
    rawcontent = getplan.group(1)
    jsonData = json.loads(rawcontent)
    return jsonData

def catfollows(user):
    fingereduser = finger_user(user)
    print("{0} follows (nick / address):".format(fingereduser['name']))
    for follow in fingereduser['following']:
        follownick = follow['nick']
        if (follownick == None) or (follownick == '') or (follownick == 'None'):
            follownick = 'No nick'
        follownick = follownick.ljust(20,'-') #pads the name to line up output. Assumes nicks are never longer than 20 characters. Really?
        print("{0} {1}".format(follownick,follow['address']))

def save(data, filename):
    'Save data to a file as a json file'
    jsondata = json.dumps(data, indent=2) # Pretty indentation!
    with open(filename, encoding='utf-8', mode='w') as OutFile:
        OutFile.write(jsondata)
         
def load(filename):
    'Load data from a json file'
    with open(filename, encoding='utf-8', mode='r') as InFile:
        jsondata = InFile.read()
    return json.loads(jsondata)

def main():
    num_args = len(sys.argv) - 1
    if num_args < 1 :
        print("No command specified. Try help")
        return
        
    d = Data()
    cmd = sys.argv[1]
    if cmd =='fetch':
        d.fetch()
    elif cmd == 'follow':
        d.follow(sys.argv[2], sys.argv[3])
    elif cmd == 'following':
        d.following()
    elif cmd == 'help':
        print("Sorry, not much help at the moment")
    elif cmd == 'post':
        if num_args > 1:
            posttext = sys.argv[2]
        else:
            posttext = input('Type your message and press return:\n> ')
        d.post(posttext)
    elif cmd == 'print':
        d.prmess()
    elif cmd == 'read':
        d.fetch()
        d.prmess()
    elif cmd == 'setup':
        d.setup()
    elif cmd == 'stdin':
        text = sys.stdin.read()
        d.post(text)
    elif cmd == 'unfollow':
        d.unfollow(sys.argv[2])
    elif cmd == 'whois':
        fingereduser = finger_user(sys.argv[2])
        print("User Name: {0} (address: {1})".format(fingereduser['name'],fingereduser['address']))
        print("Biography: " + fingereduser['bio'])
        print("Contact:\n - Email: {0}\n - web: {1}\n - mobile: {2}".format(fingereduser['properties']['email'],fingereduser['properties']['website'],fingereduser['properties']['mobile']))
    elif cmd == 'catfollows':
        catfollows(sys.argv[2])
    else:
        print("Unrecognised command: ", cmd)

if __name__ == "__main__":
    main()
