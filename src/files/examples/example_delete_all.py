#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""
from platform import platform

import time
from pyfingerprint.pyfingerprint import PyFingerprint
plt= platform().lower()
if "windows" in plt:
    port="COM11"
else:
    port="/dev/ttyUSB0"

## Deletes a finger from sensor
##
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

## Tries to delete the template of the finger
try:
    tableIndex = f.getTemplateIndex(0)
    for index, val in enumerate(tableIndex):
        if val:
                print index,val
                if ( f.deleteTemplate(index) == True ):
                    print('Template deleted!')
    time.sleep(5)
except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)