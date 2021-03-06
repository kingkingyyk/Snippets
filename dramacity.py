from splinter import Browser
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import subprocess, time, click, sys, os, requests, webbrowser

class Drama:

	 def __init__ (self, name, link):
	 	self.name = name
	 	self.link = link

def download_drama(url):
	options = Options()
	options.add_argument('--log-level=3')
	options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.javascript': 2, 'profile.managed_default_content_settings.images': 2})
	with Browser('chrome', headless=False, options=options) as browser:
	    print('Loading '+url)
	    browser.visit(url)

	    print('Loading external video site...')
	    browser.click_link_by_text('Click Here To Watch')
	    time.sleep(5)
	    browser.windows.current = browser.windows[1]

	    #Find the openload link from the small video window
	    print('Loading micro video site...')
	    video_window_url = browser.find_by_xpath('/html/body/iframe[1]').first['src']
	    browser.visit(video_window_url)
	    openload_url = [x['href'] for x in browser.find_by_tag('a') if x['href'] is not None and x['href'].startswith('https://openload.co')][0]
	    browser.quit()

	options = Options()
	options.add_argument('--log-level=3')
	options.add_experimental_option( "prefs",{'profile.managed_default_content_settings.images': 2})
	with Browser('chrome', headless=True, options=options) as browser:	    
	    print('Loading '+openload_url)
	    browser.visit(openload_url)
	    #Click small download button
	    browser.find_by_xpath('//*[@id="btnDl"]').first.click()
	    time.sleep(2)
	    for i in range(0,3):
	    	#Click download button for three times!!
	    	browser.find_by_xpath('//*[@id="main"]/div[2]/div/div[2]/div/div/div[2]').first.click()
	    	time.sleep(2)

	    direct_url = browser.find_by_xpath('//*[@id="realdl"]/a').first['href']
	    print('Download link found! '+direct_url)
	    browser.quit()
	    webbrowser.open_new_tab(direct_url)


def query_drama():
	soup = BeautifulSoup(requests.get('http://dramacity.io/').text, 'lxml')
	return [Drama(entry.find('a')['title'], entry.find('a')['href']) for entry in soup.findAll('div', class_ = 'col-md-3 col-sm-3 col-xs-4 item responsive-height post')]

@click.group()
def cli_list():
	pass

@cli_list.command()
def list():
	drama_list = query_drama()
	print('-------------------------------')
	print('         JUST UPDATED          ')
	print('-------------------------------')
	print('')
	print('-------------------------------')
	for index, drama in enumerate(drama_list):
		print(str(index+1) + ") " + str(drama.name.encode("ascii", "ignore")))
		print( "\t\t" + str(drama.link.encode("ascii","ignore")))
		print('-------------------------------')

@click.group()
def cli_download():
	pass

@cli_download.command()
@click.option('--id', help='ID of drama in the list.', required=True)
def download(id):
	drama_list = query_drama()
	ids = id.split(",")
	for x in ids:
		if x.isdigit() and int(x) > 0 and int(x) <= len(drama_list):
			print('Now downloading '+str(drama_list[int(x)-1].name.encode('ascii', 'ignore')))
			download_drama(drama_list[int(x)-1].link)
		else:
			print(x+'is an invalid id, will be skipped!')

cli = click.CommandCollection(sources=[cli_list, cli_download])

if __name__ == '__main__':
    cli()
