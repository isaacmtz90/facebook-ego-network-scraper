''' 
@Filename: extract_ego.py
@Author: Isaac Martinez // imtz90@gmail.com

Get all of your friend's facebook user ids 
Usage: python get_friends_network.py <username> <password> <numerical_fb_id> <output file>
 
The output format is a .dot file (specify in the arguments)

This script uses a browser automation library and the Firefox browser.
Automates the actions using selenium

Install via Pip:
pip install splinter 
pip install selenium
pip install codecs
pip install requests

'''

import sys 
import json 
import time
import selenium
import codecs
import requests 
from splinter import Browser
from urllib2 import URLError
from selenium.webdriver.common.keys import Keys

_base_url = "https://www.facebook.com"
_login_url = "https://www.facebook.com/login.php"
_mutual_friends_url = _base_url + "/%s/friends_mutual"
_friends_url = _base_url+ "/%s/friends"
_node_label_pattern = "%s [label=\"%s\"]\n"
_edge_label_pattern = "%s -- %s;\n"

try:
	username = sys.argv[1]
	password = sys.argv[2]
	own_fb_id = sys.argv[3]
	out = sys.argv[4]
except IndexError:
	print "Usage: python extract_ego.py <username> <password> <numerical_fb_id> <output file>.dot"
	sys.exit()

# Create the browser instance  (#TODO: make Phantom js work instead of FF)
browser = selenium.webdriver.Firefox()

# Log in by finding the log in form and filling it 
# with your username and password. Then automatically
# "click" on the enter button, and navigate to the 
# messages page. 
def login():
	
	browser.get(_base_url)

	assert "Facebook" in browser.title
	elem = browser.find_element_by_id("email")
	elem.send_keys(username)
	elem = browser.find_element_by_id("pass")
	elem.send_keys(password)
	elem.send_keys(Keys.RETURN)

	print "Logged in!"
	time.sleep(3)
	

# This is the automatic equivalent of scrolling down.
def load_all_friends(scroller_type):
	done = False
	# Friends are contained within these divs 
	#Find my friends:
	if scroller_type == "me":
		#Scroll bottom until finding a specific div (This div depend on the fb html)
		while not done:
			try:
				browser.find_element_by_xpath("//div[@class='mbm _5vf sectionHeader _4khu']")
				done = True
				return "my_friends"
			except:
				browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	else:#mutual
		#Check if there are no mutual friends
		try:
			browser.find_element_by_xpath("//a[@name='Mutual Friends']")
		except:
			return "no_mutual"
	
	while not done:
		#Scroll bottom while in the mutual friend section
		try:
			browser.find_element_by_xpath("//div[@class='mbm _5vf sectionHeader _4khu']")
			done = True
			return "has_mutual"
		except:
			browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

#Get a list of my friends and write initial edges
def get_my_friends():
	browser.get(_friends_url % username)
	time.sleep(2)
	load_all_friends("me")	
	#f = open(out,'w')
	friends = browser.find_elements_by_xpath("//*[@class='fsl fwb fcb']/a")	
	my_friends = list(map (parse_friends, friends))
	print "extracting own friends..."

	#make an edge to myself for each of them
	for friend in my_friends:
		with codecs.open(out,'a+', 'utf8') as f:
			if not friend [0] == "-1": #omits disabled accounts
				f.write(_edge_label_pattern % (friend[0], own_fb_id))

	return my_friends

#Extract friend information from the web element
def parse_friends(friend_web_element):
	try:
		friend_identifiers = json.loads(friend_web_element.get_attribute("data-gt"))
		friend_name = friend_web_element.get_attribute("text")
		friend_id = friend_identifiers["engagement"]["eng_tid"]
		
	except:
		friend_name = friend_web_element.get_attribute("text")
		friend_id = "-1"

	#print friend_id + "| " + friend_name
	return (friend_id, friend_name)

#Write edges for mutual friends
def get_mutual_friends(current_friend):
	if(current_friend[0] != "-1"):
		print "Getting %s 's friends" % current_friend[1]
		browser.get(_mutual_friends_url % current_friend[0])
		time.sleep(2)
		parsable =load_all_friends("mutual")	
		if parsable == "has_mutual":
			friends = browser.find_elements_by_xpath("//*[@class='fsl fwb fcb']/a")	
			mutual_friends = list(map (parse_friends, friends))
			for friend in mutual_friends:
				with codecs.open(out,'a+', 'utf8') as f:
					f.write(_edge_label_pattern % (current_friend[0] ,friend[0]))
		else: #no mutual friends, just draw one edge
				with codecs.open(out,'a+', 'utf8') as f:
					f.write(_edge_label_pattern % (current_friend[0] ,own_fb_id))
		time.sleep(1)


# Log in to Facebook 
login() 

#start graph file
with codecs.open(out,'a+', 'utf8') as f:
	f.write("graph ego {\n")
# #get my friends:
my_friends = get_my_friends()

for friend in my_friends:
	get_mutual_friends(friend)

#Rename labels (from userid to real names)
for friend in my_friends:
	with codecs.open(out,'a+', 'utf8') as f:
		if not friend [0] == "-1": #omits disabled accounts
			f.write(_node_label_pattern % (friend[0], friend[1]))
#Add myself	and finish the file		
with codecs.open(out,'a+', 'utf8') as f:
	f.write(_node_label_pattern % (own_fb_id,"Me"))
	f.write("}")

print "Finished"
