# -*- coding: utf-8 -*-

import re
import os, csv
from pattern.en import parse

ohioTweets = []
locations = ['OH', 'Ohio', 'Buckeye', 'oh', 'ohio', 'buckeye']
mentions = ['OH', 'Ohio', 'Buckeye', 'oh', 'ohio', 'buckeye']
retweets = []
candidates = ['jeb', 'bush', 'carson', 'trump', 'fiorina', 'christie', 'cruz', 'gilmore', 'graham', 'huckabee', 'jindal', 'kasich', 'pataki', 'perry', 'rand', 'rubio', 'santorum', 'walker', 'hillary', 'clinton', 'bernie', 'sanders', "o'malley", 'omalley', 'chafee', 'webb']

phrases = {}
foundPhrases = []
punctuation = ['.', '!', ';', '?', ':', ',', 'https', ')', '(']
toCheck = [[' is ', 'JJ'], [' is ', 'NN'], [' is ', 'RB'], [' is ', 'VB'], [' is ', 'DT'], [" wants ", 'NN'], [" wants to ", 'VB'], [" doesn't want to ", 'VB'], [" doesn't want ", 'NN'], [" does ", ''], [" doesn't ", ''], [' thinks ', '']]
descriptors = ['JJ', 'RB', 'IN']

emotions = []
candidateEmotions = []

with open('NRC-emotion-lexicon-wordlevel-alphabetized-v0.92.txt', 'rb') as f:
	reader = csv.reader(f, delimiter="\t")
	for row in reader:
		if row[2] == "1":
			if len(emotions) == 0:
				emotions.append([row[0], row[1]])
			else:
				for i in range(len(emotions)-1, len(emotions)):
					if row[0] in emotions[i]:
						emotions[i].append(row[1])
						continue
					else:
						emotions.append([row[0], row[1]])

print "Emotions loaded!"

cities = open('ohio-cities.txt', 'r')
c = cities.read()
c = c.split('\n')
for line in c:
	locations.append(line)

print parse('of')

def loadFile(filename):
	print "Processing " + filename + "..."
	f = open(filename, 'r')
	fullfile = f.read()
	fullfile = fullfile.replace('\n', '').split('][')
	
	for text in fullfile:
		line = text.split(';')
		# print len(line)
		if len(line) > 3:
			geo = line[1]
			content = line[2]
			# print content

		loc = checkLocation(geo)

		if loc == True:
			# print geo
			ohioTweets.append(line)
		else:
			tweet = checkOhioMention(content)
			if tweet == True:
				# print tweet
				ohioTweets.append(line)

def checkLocation(geo):
	for l in locations:
		s = re.search(l, geo)
		if s != None:
			inOhio = True
			break
		else:
			inOhio = False
	return inOhio

def checkOhioMention(tweet):
	for m in mentions:
		se = re.search(m, tweet)

		if se != None:
			mentionsOhio = True
			break
		else:
			mentionsOhio = False
	
	return mentionsOhio

def checkRetweet(tweet):
	s = re.search('RT', tweet)
	if s != None:
		# print "RETWEET FOUND: " + tweet
		fragment = tweet.split(s.group(0))
		if fragment[1] not in retweets:
			retweets.append(fragment[1])
			# print len(retweets)
	# else:
	# 	print "not a retweet"

def checkPhrase(tweet, regex, pos):
	tweetLower = tweet.lower()
	expression = ''
	for p in punctuation:
		tweetLower = tweetLower.replace(p, ' END ')

	for c in candidates:
		# phrases = {}
		searchString = c + regex
		# print searchString
		splitString = searchString.split(" ")
		if '' in splitString:
			splitString.remove('')

		fragmentPhrase = "%s(.*)" % searchString
		m = re.search(fragmentPhrase, tweetLower)

		if m != None:
			matchingFragment = m.group(0)
			# print matchingFragment
			matchingFragment = matchingFragment.replace('@', 'at').replace('_', '').replace('&amp', 'and').replace("&slash;", "/").replace('"', '').replace("'", '')

			if 'END' in matchingFragment:
				matchingFragment = matchingFragment.split('END')[0]

			words = matchingFragment.split(' ')
			if '' in words:
				words.remove('')

			if "hillary" in searchString:
				searchString = searchString.replace("hillary", "clinton")
			elif "bernie" in searchString:
				searchString = searchString.replace("bernie", "sanders")
			elif "jeb" in searchString:
				searchString = searchString.replace("jeb", "bush")
			# elif "rand" in searchString:
			# 	searchString = searchString.replace("rand", "paul")

			# regex by word type
			if len(words) > len(splitString):
				w = parse(words[len(splitString)]).split('/')
				if len(w) > 1:
					if 'ing' in w[0]:
						w[1] = 'VB'
					if pos in w[1] or pos == '':
						expression = searchString
						if pos not in descriptors:
							for i in range(len(splitString), len(words)):
								x = parse(words[i]).split('/')
								if 'ing' in x[0]:
									x[1] = 'VB'
								if len(x) > 2:
									expression += x[0].encode('utf-8')
									if 'NN' in x[1] and i < len(words)-1:
										y = parse(words[i+1]).split('/')
										if 'ing' in y[0]:
											y[1] = 'VB'
										if len(y) > 1 and y[1] in descriptors:
											expression += ' '
											continue
										else:
											break
									else:
										expression += ' '
										continue
						elif pos in descriptors:
							for i in range(len(splitString), len(words)):
								x = parse(words[i]).split('/')
								if 'ing' in x[0]:
									x[1] = 'VB'
								if len(x) > 2:
									expression += x[0].encode('utf-8')
									if 'JJ' in x[1] and i < len(words)-1:
										y = parse(words[i+1]).split('/')
										if 'ing' in y[0]:
											y[1] = 'VB'
										if len(y) > 1 and 'NN' in y[1]:
											expression += ' '
											continue
										else:
											break
									elif 'NN' in x[1]:
										break
									else:
										expression += ' '
										continue

			expression = expression.strip() #strip whitespace
			if len(expression) > 1:
				if expression not in phrases:
					phrases[expression] = 1
				else:
					phrases[expression] += 1

def checkCandidateSentiment(tweet, name):
	tweetLower = tweet.lower()
	loc = candidates.index(name)
	for p in punctuation:
		tweetLower = tweetLower.replace(p, '')

	if name in tweetLower:
		wordsInPost = tweetLower.split(" ")

		for p in wordsInPost:
			for e in emotions:
				if p == e[0]:
					if e[1] not in candidateEmotions[loc]:
						candidateEmotions[loc][e[1]] = 1
					else:
						candidateEmotions[loc][e[1]] += 1


# allFiles = os.listdir('data/prejanuary/')
# # print allFiles

# for a in allFiles:
# 	if a != ".DS_Store":
# 		loadFile('data/prejanuary/' + a)

for i in range(1, 2):
	fn = 'data/twitterdata2016-04-' + str(i).zfill(2) + '.txt'
	# fn = 'data/twitterdata2016-04-19.txt'
	if os.path.exists(fn):
		loadFile(fn)

print "\n*** TWEETS COLLECTED! ***"
# print "Tweets collected: " + str(len(ohioTweets))

print "\n*** RUNNING REGEX ***"
for c in toCheck:
	print "checking" + c[0] + "(" + c[1] + ")"
	for t in ohioTweets:
		if len(t) > 2:
			checkPhrase(t[2], c[0], c[1])

for i in range(0, len(candidates)):
	p = []
	foundPhrases.append(p)
	candidateEmotions.append({})

sortedPhrases = sorted(phrases.items(), key=lambda x: x[1], reverse=True)
# print sortedPhrases

for phrase in sortedPhrases:
	for i in range(0, len(candidates)):
		try:
			if phrase[0].index(candidates[i]) == 0 and phrase[1] >= 10:
				foundPhrases[i].append(phrase)
		except:
			continue

with open('test-data-analysis.txt', 'w') as fl:
# with open('prejanuary-data-analysis.txt', 'w') as f:
	for i in range(0, len(foundPhrases)):
		for f in foundPhrases[i]:
			try:
				fl.write(f[0] + ": " + str(f[1]) + '\n')
			except UnicodeEncodeError:
				fl.write(f[0].encode('utf-8') + ": " + str(f[1]) + '\n')
			except UnicodeDecodeError:
				fl.write(f[0].decode('utf-8') + ": " + str(f[1]) + '\n')

		fl.write('-----\n')

	fl.close()

print "*** DONE WITH REGEX ***"

print "\n*** CHECKING SENTIMENT ***"
for c in candidates:
	print "checking sentiment for " + c
	for t in ohioTweets:
		if len(t) > 2:
			checkCandidateSentiment(t[2], c)

	loc = candidates.index(c)
	sortedEmotions = sorted(candidateEmotions[loc].items(), key=lambda x: x[1], reverse=True)
	if len(sortedEmotions) > 0:
		print c + ": " + str(sortedEmotions[0][0]) + ", " + str(sortedEmotions[0][1])

print "\n*** CHECKING RETWEETS ***"
for t in ohioTweets:
	if len(t) > 2:
		checkRetweet(t[2])

print "Tweets collected: " + str(len(ohioTweets))
print "Number of retweets: " + str(len(retweets))
print "Percentage that are retweets: " + str((float(len(retweets))) / float(len(ohioTweets))*100)
