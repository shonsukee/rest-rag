### python/iniHandler.py
#!/usr/bin/env python
import sys
import os
import ConfigParser
import json

iniDirectory = './' + os.path.dirname(os.path.relpath(os.path.realpath(__file__))) + '/'
credentialsFile = 'credentials.ini'
credentialParser = ConfigParser.SafeConfigParser()

def print_json(type, message):
    #Convert output to json and print (node_helper reads from stdout)
    print(json.dumps({type: message}))
    #stdout has to be flushed manually to prevent delays in the node helper communication
    sys.stdout.flush()

def fileExists(path,file):
    if os.path.isfile(path + file):
        print_json("status","%s exists" %file)
        return True
    else:
        print_json("status","%s does not exist" %file)
        return False

def ReadCredentials():
    #Check if credentials.ini exists
    if not fileExists(iniDirectory, credentialsFile):
        print_json('error', '%s does not exist' %s)
        sys.exit(1)
    #Reads app credentials from credentials.ini
    print_json("status", "Reading from %s" %credentialsFile)
    
    try:
        #Open file and read credentials
        credentialParser.read(iniDirectory + credentialsFile)
        client_id = credentialParser.get('Credentials', 'C_ID')
        client_key = credentialParser.get('Credentials', 'C_KEY')
        client_secret = credentialParser.get('Credentials', 'C_SECRET')
    except ConfigParser.NoSectionError:
        #If the credentials file is not correctly formatted
        print_json("error","Cannot read %s" %credentialsFile)
        sys.exit(1)
    else:
        #Return credentials
        print_json("status", "Read of %s successful." %credentialsFile)
        return client_id, client_key, client_secret

### python/authHandler.py
#!/usr/bin/env python
from iniHandler import print_json, ReadCredentials, WriteTokens

#Get credentials from file
client_id, client_key, client_secret = ReadCredentials()
