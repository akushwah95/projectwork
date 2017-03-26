#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""
import requests
import time
from pyfingerprint.pyfingerprint import PyFingerprint
import hashlib
from platform import platform

## Enrolls new finger
##
plt= platform().lower()
if "windows" in plt:
    port="COM11"
else:
    port="/dev/ttyUSB0"
post_url="http://35.154.44.42:8080/userenrollment/webapi/users"
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

## Tries to enroll new finger
try:
    print('Waiting for finger...')

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

    ## Checks if finger is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if ( positionNumber >= 0 ):
        print('Template already exists at position #' + str(positionNumber))
        exit(0)
    print('Remove finger...')
    time.sleep(2)

    print('Waiting for same finger again...')

    ## Wait that finger is read again
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 2
    f.convertImage(0x02)

    ## Compares the charbuffers and creates a template
    if f.compareCharacteristics() != 0:
        f.createTemplate()
        ## Saves template at new position number
        characterics = str(f.downloadCharacteristics(0x01))
        print(characterics)
        fl = open("shas-store", 'a')
        fr = open("shas-store", 'r')
        ## Hashes characteristics of template
        hashes = hashlib.sha256(characterics).hexdigest()
        print type(hashes)
        hashes_file = fr.read()
        if hashes not in hashes_file:
            fl.write(hashes + '-')
        else:
            print "Hash already present machaaa!!!"
        print('SHA-2 hash of template: ' + hashlib.sha256(characterics).hexdigest())

        voter_name = raw_input("Please enter you name : ")
        dob = raw_input("Please Enter Date of Birth : ")
        mother_name = raw_input("Please Enter Mother's Name : ")
        father_name = raw_input("Please Enter Father's name : ")
        address = raw_input("Please enter address :")
        mobile_number = int(raw_input("Please Enter Mobile Number"))
        headers= {'content-type': 'application/json'}
        diction="{\"address\": \"%s\",\"dob\":\"%s\",\"fatherName\": \"%s\",\"fingerPrint\": \"%s\",\"mobileNumber\": %s, \
                \"motherName\": \"%s\",\"name\": \"%s\"}" % (address,dob,father_name,hashes,mobile_number,mother_name,voter_name)
        cc = requests.post(post_url,data=diction,headers=headers)
        print cc.text

        cd = requests.get(post_url)
        print cd.text
        print cd.content
        positionNumber = f.storeTemplate()
        print('Finger enrolled successfully!')
        print('New template position #' + str(positionNumber))
    else:
        print('Fingerprints do not match')

    ## Saves template at new position number
    # positionNumber = f.storeTemplate()
    # print('Finger enrolled successfully!')
    # print('New template position #' + str(positionNumber))

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
