#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time

url="http://35.154.44.42:8080/userenrollment/webapi/voter/votecount"
print ('Welcome to EC Portal ')
print ('Please wait we are fetching the Voting Data')
voting_data = requests.get(url)
print voting_data.text
print ('-----------')
print voting_data.content
v=raw_input('Press any key to exit')
print ('Exiting.....')
time.sleep(5)