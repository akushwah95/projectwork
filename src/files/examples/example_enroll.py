#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Enrolls a voter to the database
"""
import os

import requests
import time
from pyfingerprint.pyfingerprint import PyFingerprint
import hashlib
from platform import platform

plt = platform().lower()
if "windows" in plt:
    port = "COM11"
else:
    port = "/dev/ttyUSB0"

post_url = "http://35.154.44.42:8080/userenrollment/webapi/users"

try:
    f = PyFingerprint(port, 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

#print('Currently used templates: ' + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))


try:
    print ('-------------------------------')
    print ('Welcome To Enrollment Portal !!!')
    print ('Waiting for finger to Enroll')

    ## Wait that finger is read
    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

    ## Checks if finger is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if ( positionNumber >= 0 ):
        #print('Template already exists at position #' + str(positionNumber))
        print ('Fingerprint is already stored in the Database !!')
        characterics = str(f.downloadCharacteristics(0x01))
        hashes = hashlib.sha256(characterics).hexdigest()
        get_utl=post_url+"/"+hashes
        resp = requests.get(get_utl)
        print (resp.text)
        time.sleep(5)
        print ('Exiting now !!!')
        time.sleep(2)
        exit(0)
    print('Remove finger...')
    time.sleep(5)

    print('Waiting for same finger again...')

    while ( f.readImage() == False ):
        pass

    f.convertImage(0x02)

    if f.compareCharacteristics() != 0:
        f.createTemplate()
        characterics = str(f.downloadCharacteristics(0x01))
        hashes = hashlib.sha256(characterics).hexdigest()
        print ('Please Fill in the details that follows to Enroll New Voter : ')
        voter_name = raw_input("Please enter you name : ")
        dob = raw_input("Please Enter Date of Birth : ")
        mother_name = raw_input("Please Enter Mother's Name : ")
        father_name = raw_input("Please Enter Father's name : ")
        address = raw_input("Please enter address :")
        mobile_number = int(raw_input("Please Enter Mobile Number :"))
        os.system('clear')
        positionNumber = f.storeTemplate()
        headers = {'content-type': 'application/json'}
        diction = "{\"address\": \"%s\",\"dob\":\"%s\",\"fatherName\": \"%s\",\"fingerPrint\": \"%s\",\"mobileNumber\": %s,\
                \"motherName\": \"%s\",\"name\": \"%s\"}" \
                % (address, dob, father_name, hashes, mobile_number, mother_name, voter_name)
        print ('Please be Patient while we store the data onto our database')
        send_data = requests.post(post_url, data=diction, headers=headers)
        if send_data.status_code == 200:
            print ('Data sent successfully !!')
        print ('Congratulations %s' % voter_name)
        print ('Finger enrolled successfully!')
        time.sleep(5)
        #print('New template position #' + str(positionNumber))
    else:
        print('Fingerprints do not match')
        time.sleep(5)
except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
