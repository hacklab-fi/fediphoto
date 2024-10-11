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

feed = feedparser.parse('https://sauna.social/tags/altparty.rss')

conn = cups.Connection()
printer = conn.getDefault()

if not printer:
	print('No default printer defined, cannot print!')

for item in feed.entries:
	tootid = int(item.id[item.id.rfind('/') + 1:])
	baseurl = item.id[:item.id.rfind('@') - 1]
	mastodon = Mastodon(api_base_url = baseurl)
	status = mastodon.status(tootid)
	url = status['account']['url']
	domain = url[:url.rfind('/')][url.find('//')+2:]
	user = url[url.rfind('@'):]
	fediuser = user + '@' + domain
#	print(fediuser, status['account']['display_name'], status['account']['url'])
	for attachment in status['media_attachments']:
		print(attachment['id'], attachment['url'])
		filename = str(attachment['id']) + '.jpg'
		needs_print = True
		if Path('pics/' + filename).is_file():
			print('(Already exists)')
		elif Path('pics/printed/' + filename).is_file():
			print('(Already printed)')
			needs_print = False
		else:
			urlretrieve(attachment['url'], 'pics/' + filename)
			print('Saved as', filename)
			label = status['account']['display_name'] + '\n' + fediuser
			img = Image.open('pics/' + filename)
			draw = ImageDraw.Draw(img)
			topaz = ImageFont.truetype('topaz_unicode_ks13_bold.ttf', img.size[0] / 50)
			draw.text((img.size[0] / 30, img.size[1] / 30), label, fill=(255,255,255), stroke_fill=(0,0,0), stroke_width=5, font=topaz)
			modfile = 'pics/' + 'mod_' + filename
			img.save(modfile)

			if printer and needs_print:
				pid = conn.printFile(printer, modfile, 'From fediverse - ' + fediuser, {'fit-to-page': 'TRUE' })
				while conn.getJobs().get(pid, None) is not None:
					time.sleep(5)
					print('Printing job id', pid, '..')
				os.rename(modfile, 'pics/printed/' + filename)
				print('Printed and moved to ', 'pics/printed/' + filename)


