#!/usr/bin/env python

import sys
import json
import tweepy
import os
import time
import re
import requests
import urllib

from bs4 import BeautifulSoup
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

consumer_key = "EPmNtSbK0VEX9JMyTeLr8WLLa"
consumer_secret = "j0bhW7iOnBuR9XcNEpKdLIyWmrAy2YMhzbP3AIZabL3EmtmJmv"
access_token = "1149105082442514434-amuNTlY7ef90gLOpIl1lW0Jfkx5NFz"
access_token_secret = "O8OZ7dkO6zoyCXRu2cnjuEDLZO68HuAn81XHxPUeYlIMS"

dir_name = 'data'
file_path = os.path.abspath(dir_name + '/twitter_data1.txt')
dir_path = os.path.abspath(dir_name)

# If the 'data' folder doesn't exist, create it.
if not os.path.exists(dir_path):
	os.makedirs(dir_path)

file = open(file_path, 'w+') # change back to a+ when finished!

# Adding in brace to store data as an array of tweets.
file.write('[')

file_num = 1
doneCrawling = False

class twitterCrawler(StreamListener):

	def on_data(self, data):
		global file
		global file_num
		global doneCrawling

    	#2GB data reached
		if (file_num >= 200): # 200
			print("2GB of data reached \n")
			doneCrawling = True
			file.seek(-1, os.SEEK_END) # remove trailing comma
			file.write(']')            # close array object
			return False

    	#10MB reached. Open new txt file. 
		if (file.tell() >= 1000000): # 1000000
			print("10 MB OF DATA REACHED, STARTING NEW PAGE \n")
			file.seek(-1, os.SEEK_END) # remove trailing comma
			file.write(']')            # close array object
			file.close()		   # close file

			file_num += 1
			file_path = dir_name + '/twitter_data' + str(file_num) + '.txt'
			file = open(file_path, 'w+') # if next file doesn't exist, create + open it
			file.write('[')

    	#Storing data in txt file
		data = data + ','
		print(data)
		file.write(data)
		return True

	def on_error(self, status):
		print(status)
		if (status == 420):
			print("Too many requests for twitter API, please wait 30 seconds.")
			return False


def parse_data():
	print("PARSING COLLECTED DATA...")
	#requesting for parsing the designated html page
	headers = requests.utils.default_headers()

	# Iterate through each of the files...
	files = os.listdir(dir_path)
	for file_name in files:
		path = os.path.abspath('data/' + file_name)
		data_file = open(path)
		data = json.load(data_file) # all of the json objects in the page turned into a dict

		# Iterate through tweet objects... 
		for tweet in data:
			try:
				# Get the text field from a tweet
				tweet_text = tweet["text"]
				# Search for URL in tweet body
				new_text = tweet_text.replace('\\', '')
				
				# [TODO] - replace '<REGEX>' w/ correct expression + uncomment line
				#looking for any strings which has http or https in the beginning
				url1 = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', new_text)
				url2 = url1[0].replace('[', '')
				url = url2.replace(']', '')
				# If tweet contains a URL			
				if "http" in url:
					print("placeholder to avoid indent error")
					# [TODO] - crawl url for title
					req = requests.get(url, headers)
					soup = BeautifulSoup(req.content, 'html.parser')
					
					#store title in the variable name "titles"
					title = soup.title.string
					# Add field to tweet object
					tweet['html_title'] = title
			except Exception as e:
				print(e)

		# Turn data back into json and overwrite the page
		updated_data = json.dumps(data)
		updated_data_str = str(updated_data)
	
		with open (path, "w") as updated_file:
			updated_file.write(updated_data_str)

		updated_file.close()

if __name__ == '__main__':

	while doneCrawling != True:
		try:
			#This handles Twitter authetification and the connection to Twitter Streaming API
			l = twitterCrawler()
			auth = OAuthHandler(consumer_key, consumer_secret)
			auth.set_access_token(access_token, access_token_secret)
			stream = Stream(auth, l)

			#Bounded box location. At the moment, it's around california. 
			stream.filter(locations=[-124.48, 32.53, -114.13, 42.01])

			parse_data()
		except Exception as e:
			print("Exception: " + e)
			time.sleep(30)
			print("Resume crawling")
			pass

	file.close()
