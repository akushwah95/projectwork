#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import hashlib
import os
from platform import platform

import time
from pyfingerprint.pyfingerprint import PyFingerprint
import requests


url = "http://35.154.44.42:8080/userenrollment/webapi/voter"
plt = platform().lower()
if "windows" in plt:
    port = "COM11"
else:
    port = "/dev/ttyUSB0"
party_list = {1: "BJP", 2: "CONGRESS", 3: "AAP", 4: "LSP"}
## Tries to initialize the sensor
try:
    f = PyFingerprint(port, 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    time.sleep(5)
    exit(1)

## Gets some sensor information
#print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

## Tries to search the finger and calculate hash
try:
    print('Waiting for finger to start voting :')
    print('Please keep your finger on the sensor')
    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

    ## Searchs template
    result = f.searchTemplate()
    positionNumber = result[0]
    accuracyScore = result[1]

    if ( positionNumber == -1 ):
        print('No match found for this fingerprint')
        print ('Exiting')
        time.sleep(5)
        exit(0)
    else:
        #print('Found template at position #' + str(positionNumber))
        #print('The accuracy score is: ' + str(accuracyScore))
        print ('Found you fingerprint!!')
    ## OPTIONAL stuff
    ##

    ## Loads the found template to charbuffer 1
    f.loadTemplate(positionNumber, 0x01)

    ## Downloads the characteristics of template loaded in charbuffer 1
    characterics = str(f.downloadCharacteristics(0x01))

    ## Hashes characteristics of template
    hashes = hashlib.sha256(characterics).hexdigest()

    get_url = url+"/"+hashes
    get_data = requests.get(get_url)
    if get_data.status_code == 204:
        print (get_data.text)
        while True:
            print ('List of parties along with the number :')
            for number, party_name in party_list.iteritems():
                print party_name,number
            try:
                vote_to=int(raw_input("Please enter Party Number to vote to:"))
                if party_list.get(vote_to) is None:
                    raise ValueError
                break
            except ValueError as v:
                print ('Invalid Party Number!!!')
                print ('Try Again')
                os.system('clear')
        post_url = url
        headers = {'content-type' : 'application/json'}
        payload = "{\"fingerPrint\":\"%s\",\"hasVotedTo\":\"%s\"}" % (hashes, party_list.get(vote_to))
        cc = requests.post(post_url, data=payload, headers=headers)
        print cc.text
        time.sleep(5)
except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    time.sleep(5)
    exit(1)
