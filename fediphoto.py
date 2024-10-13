#!/usr/bin/env python3
import cups
from mastodon import Mastodon
import feedparser
from urllib.request import urlretrieve
from pathlib import Path
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os
import time

feedurls = ['https://infosec.exchange/tags/altparty.rss', 'https://sauna.social/tags/altparty.rss', 'https://mastodon.social/tags/altparty.rss']

printername = 'UP-DR200'

conn = cups.Connection()
printer = conn.getDefault()

os.system('lprm')
time.sleep(1)
os.system('cupsenable ' + printername)

if not printer:
	print('No default printer defined, cannot print!')

def poll_feed(feedurl):
	feed = feedparser.parse(feedurl)
	for item in feed.entries:
		tootid = int(item.id[item.id.rfind('/') + 1:])
		baseurl = item.id[:item.id.rfind('@') - 1]
		mastodon = Mastodon(api_base_url = baseurl)
		status = mastodon.status(tootid)
		url = status['account']['url']
		domain = url[:url.rfind('/')][url.find('//')+2:]
		user = url[url.rfind('@'):]
		fediuser = user + '@' + domain

		for attachment in status['media_attachments']:
			print('Attachment', attachment['id'], attachment['url'], end=' -> ')
			filename = str(attachment['id']) + '.jpg'
			modfile = 'pics/' + 'mod_' + filename
			needs_print = True
			needs_dl = True
			if not attachment['type'] == 'image':
				print('not image')
				needs_print = False
				needs_dl = False
			if Path('pics/printed/' + filename).is_file():
				print('already printed')
				needs_print = False
				needs_dl = False
			elif Path('pics/' + filename).is_file():
				print('file exists')
				needs_dl = False
			if needs_dl:
				urlretrieve(attachment['url'], 'pics/' + filename)
				print('saved as', filename)
			if needs_print:
				label = status['account']['display_name'] + '\n' + fediuser
				img = Image.open('pics/' + filename)
				if img.mode != 'RGB':
					img = img.convert('RGB')
				draw = ImageDraw.Draw(img)
				topaz = ImageFont.truetype('topaz_unicode_ks13_regular.ttf', int(img.size[0] / 30))
				draw.text((img.size[0] / 30, img.size[1] / 30), label, fill=(255,255,255), stroke_fill=(0,0,0), stroke_width=5, font=topaz)
				img.save(modfile)

			if printer and needs_print:
				pid = conn.printFile(printer, modfile, 'From fediverse - ' + fediuser, {'fit-to-page': 'TRUE' })
				print('Printing image as job', pid, '..')
				time.sleep(20)
				os.system('lprm')
				time.sleep(1)
				os.system('cupsenable ' + printername)
				os.rename(modfile, 'pics/printed/' + filename)
				print('Printed and moved to ', 'pics/printed/' + filename)


while True:
	for feedurl in feedurls:
		poll_feed(feedurl)
	print('Sleeping for 60 secs, press ctrl-c to exit..')
	time.sleep(60)

