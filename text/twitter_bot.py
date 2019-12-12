import os
import random
import requests
import argparse
import pandas as pd
from tqdm import tqdm
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


PATH_TO_DRIVER = './selenium_drivers/geckodriver'
TMP_PAGE_NAME = 'page.html'

# ==================================================================================
# 									PROXY
# ==================================================================================
def update_proxies():
	# Create webdriver
	options = webdriver.FirefoxOptions()
	options.add_argument('--headless')
	driver = webdriver.Firefox(executable_path=PATH_TO_DRIVER, options=options)
	driver.get('https://free-proxy-list.net/')

	# Scrape proxy table only with HTTPS support
	proxy_list = []
	print("Updateting proxies...")
	for _ in tqdm(range(15)):
	    el = driver.find_element_by_xpath('//*[@id="proxylisttable"]/tbody')
	    for line in el.text.split('\n'):
	        cur_proxy = line.split()
	        https = cur_proxy[6]
	        if https == 'yes':
	        	proxy_list.append(cur_proxy[0] + ':' + cur_proxy[1])

	    # Go further
	    driver.find_element_by_xpath('//*[@id="proxylisttable_next"]/a').click()

	driver.close()

	# Save in da file
	with open('proxy.txt','w+') as f:
		for x in proxy_list:
			f.write(x+'\n')

	print("Updated")


def _get_proxy_profile(PROXY_HOST, PROXY_PORT):
    fp = webdriver.FirefoxProfile()
    fp.set_preference("network.proxy.type", 1)
    fp.set_preference("network.proxy.http", PROXY_HOST)
    fp.set_preference("network.proxy.http_port", int(PROXY_PORT))
    fp.set_preference("network.proxy.https", PROXY_HOST)
    fp.set_preference("network.proxy.https_port", int(PROXY_PORT))
    fp.set_preference("network.proxy.ssl", PROXY_HOST)
    fp.set_preference("network.proxy.ssl_port", int(PROXY_PORT))  
    fp.set_preference("network.proxy.ftp", PROXY_HOST)
    fp.set_preference("network.proxy.ftp_port",int(PROXY_PORT))   
    fp.set_preference("network.proxy.socks", PROXY_HOST)
    fp.set_preference("network.proxy.socks_port", int(PROXY_PORT))   
    fp.set_preference("general.useragent.override", 
    				  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) \
     				  AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A")
    fp.update_preferences()

    return fp

# =============================================================================================
# 										PARSE
# =============================================================================================
def generate_query(key_words, hashtags, start_date, end_date, lang='en'):
	first_part="https://twitter.com/search?l="+lang+"&q="

	s0 = ""
	for word in key_words:
		s0 += word+"%20"
	s0+="%23"

	s1 = ""
	for hst in hashtags[:-1]:
		s1 += hst+"%20OR%20%23"
	s1 += hashtags[-1]+"%20"

	second_part = "since%3A"+start_date+"%20until%3A"+end_date+"&src=typd"

	return first_part+s0+s1+second_part


def dowload_page(query, scroll_numb, delay=1, proxy_flag=False):
	options = webdriver.FirefoxOptions()
	options.add_argument('--headless')

	if proxy_flag:
		profile = get_proxy_profile(host, port)
		driver = webdriver.Firefox(executable_path=PATH_TO_DRIVER, firefox_profile=profile, options=options)
	else:
		driver = webdriver.Firefox(executable_path=PATH_TO_DRIVER, options=options)

	driver.get(query)

	prev_h = driver.execute_script("return document.body.scrollHeight;")
	for i in tqdm(range(scroll_numb)):
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		#driver.implicitly_wait(3)
		sleep(delay)
		#while driver.execute_script('return document.readyState;') != 'complete':
			#sleep(0.1)

		cur_h = driver.execute_script("return document.body.scrollHeight;")
		if prev_h == cur_h:
			print("Stopped at {} iter".format(i))
			break
		
	with open('page.html','w') as f:
		f.write(str(driver.page_source.encode('utf-8')))
		f.close()

	driver.close()
	return 0


def __process_tweet(tweet):
	tweet_div = tweet.find('div', 'tweet')
	if not tweet_div:
		return
	# --- text
	soup_html = tweet.find('div', 'js-tweet-text-container').find('p', 'tweet-text')
	text = soup_html.text
	# --- time
	timestamp_epochs = int(tweet.find('span', '_timestamp')['data-time'])
	timestamp = datetime.utcfromtimestamp(timestamp_epochs)

	action_div = tweet_div.find('div', 'ProfileTweet-actionCountList')

    # --- likes
	likes = int(action_div.find('span', 'ProfileTweet-action--favorite') \
						  .find('span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')
    # --- retweets
	retweets = int(action_div.find('span', 'ProfileTweet-action--retweet') \
							 .find('span', 'ProfileTweet-actionCount')['data-tweet-stat-count'] or '0')

	return [timestamp, text, likes, retweets]



def parse_page():
	with open(TMP_PAGE_NAME) as f:
		page = f.read()

	soup = BeautifulSoup(page, 'lxml')
	tweets = soup.find_all('li', 'js-stream-item')

	hooy = []
	for tweet in tweets:
		t = __process_tweet(tweet)
		if t:
			hooy.append(t)

	return hooy

# ========================================================================================================
# 									MAIN
# ========================================================================================================
def parse_args():
	parser = argparse.ArgumentParser(prog="Twitter scraper", description="Scrapes tweets with parameters")
	parser.add_argument('-t', '--hashtags', nargs='*', help='Hashtags')
	parser.add_argument('-w', '--key_words', nargs='*', help="Key words")
	parser.add_argument('-s', '--start_date', help="Start date in format YYYY-MM-DD")
	parser.add_argument('-e', '--end_date', help="End date in format YYYY-MM-DD")
	parser.add_argument('-l', '--lang', default='en', help='Language')
	parser.add_argument('-c', '--scroll_numb', default=100, type=int, help="Times to scroll the page down")
	parser.add_argument('-o', '--output_fname', default='output.csv', help="Output file name")
	parser.add_argument('-d', '--sleep_time', default=1, type=float, help="Delay for page to download")

	return parser.parse_args()


if __name__ == "__main__":

	args = parse_args()
	
	query = generate_query(key_words=args.key_words, 
						   hashtags=args.hashtags,
						   start_date=args.start_date,
						   end_date=args.end_date,
						   lang=args.lang)

	print("Current url: " + query)

	print("Downloading page...")
	stat = dowload_page(query=query, delay=args.sleep_time, scroll_numb=args.scroll_numb)
	print("Done.\nParsing page...")
	lst = parse_page()
	print("Done. \nResult is in {}".format(args.output_fname))

	df = pd.DataFrame(lst, columns=["date", "text", "likes", "retweets"])
	df.to_csv(args.output_fname, header=True, index=False, encoding='utf-8')

	os.remove(TMP_PAGE_NAME)

#tweets = driver.find_elements_by_css_selector('li.js-stream-item')
#ActionChains(driver).key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
