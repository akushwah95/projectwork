#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

import hashlib
from platform import platform
from pyfingerprint.pyfingerprint import PyFingerprint
import requests

## Search for a finger
##
url="http://35.154.44.42:8080/userenrollment/webapi/voter"
plt= platform().lower()
if "windows" in plt:
    port="COM11"
else:
    port="/dev/ttyUSB0"

## Tries to initialize the sensor
try:
    f = PyFingerprint(port, 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

## Gets some sensor information
print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

## Tries to search the finger and calculate hash
try:
    print('Waiting for finger...')

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
        print('No match found!')
        exit(0)
    else:
        print('Found template at position #' + str(positionNumber))
        print('The accuracy score is: ' + str(accuracyScore))

    ## OPTIONAL stuff
    ##

    ## Loads the found template to charbuffer 1
    f.loadTemplate(positionNumber, 0x01)

    ## Downloads the characteristics of template loaded in charbuffer 1
    characterics = str(f.downloadCharacteristics(0x01))
    fl=open("shas",'a')
    fr=open("shas",'r')
    ## Hashes characteristics of template
    hashes = hashlib.sha256(characterics).hexdigest()
    print type(hashes)
    hashes_file=fr.read()
    if hashes not in hashes_file:
    	fl.write(hashes+'-')
    print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())
    fl.close()
    get_url = url+"/"+hashes
    cc=requests.get(get_url)
    print cc.status_code
    print cc.text
    if cc.status_code==204:
        vote_to=raw_input("Party name to vote to :")
        post_url=url
        headers={'content-type':'application/json'}
        payload = "{\"fingerPrint\":\"%s\",\"hasVotedTo\":\"%s\"}" % (hashes, vote_to)
        cc= requests.post(post_url, data=payload, headers=headers)
        print cc.text
except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
