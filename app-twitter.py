#!/usr/bin/python

import twitter
import json
import threading
import sys, os
import datetime

lastID = 0

query = ''

with open('candidates.txt') as f:
	for line in f:
		line = line.replace('\n', '')
		line = line.lower()
		query += line + ' OR '
	
	query += 'ohio OR #ohio'
	print query

api = twitter.Api(consumer_key="syu9AYHHv1WwCwjVHyzdwush5",
	consumer_secret="ErXSvPm0lGSMTmISNVCcii2AUvIljPFuY5EpuYBe6usG03jaU0",
	access_token_key="188154178-KFgNRQfgp0bRXirIRCXMHn1rE2grb2bctf693Hmz",
	access_token_secret="crMPFkgmWmtS3xGdPw6llAfG2SMbl6q3iFyPW4V7Tqsai",
	timeout=15)

def searchTweets():
	date = datetime.date.today()
	filename = "public/twitterdata" + str(date) + ".txt"
	global lastID
	try:
		search = api.GetSearch(term=query, count=100, lang="en", since_id=lastID)
		if len(search) > 0:
			if lastID == 0:
				with open('lastID.txt') as f:
					for line in f:
						lastID = line
					# print lastID
				for s in search:
					# print s.id
					# print s.text.encode('utf-8')
					text = s.text.encode('utf-8')
					with open(filename, 'a') as f:
						try:
							f.write('[' + s.user.screen_name.encode('utf-8') + "; " + s.user.location.encode('utf-8') + "; " + text.encode('utf-8') + "; " + str(s.geo) + ']')
						except UnicodeDecodeError:
							print "ERROR"
							# print s.user.screen_name.encode('utf-8')
							# print s.text.encode('utf-8')
							# print s.user.location.encode('utf-8')
						f.write('\n')

				lastID = search[0].id
				with open('lastID.txt', 'w+') as f:
					f.write(str(lastID))
				print "last ID collected: " + str(lastID)
				print "------------"

			else:
				for s in search:
					# print s.id
					# print s.text
					text = s.text
					with open(filename, 'a') as f:
						try:
							f.write('[' + s.user.screen_name.encode('utf-8') + "; " + s.user.location.encode('utf-8') + "; " + text.encode('utf-8') + "; " + str(s.geo) + ']')
						except UnicodeDecodeError:
							print "ERROR"
							# print s.user.screen_name.encode('utf-8')
							# print s.text.encode('utf-8')
							# print s.user.location.encode('utf-8')
						f.write('\n')

				lastID = search[0].id
				with open('lastID.txt', 'w+') as f:
					f.write(str(lastID))
				print "last ID collected: " + str(lastID)
				print "------------"

			print len(search)

		startTimer(5.0)
	except:
		print "No tweets collected. Trying again in a few!"
		startTimer(5.0)


def startTimer(time):

	print "starting timer..."
	t = threading.Timer(time, searchTweets)
	t.start()



searchTweets()
