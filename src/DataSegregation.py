#!/usr/bin/env python3

import os
from dotenv import load_dotenv, find_dotenv
import logging
import argparse
import subprocess
from urllib.parse import urlparse
from .Utilities import UTILITIES
import os
from dotenv import load_dotenv, find_dotenv
from shutil import copyfile
from .Utilities import UTILITIES
import time
load_dotenv(dotenv_path='.env', verbose=True)

class DataSegregation(object):

	def __init__(self):

		self.CHROME_CACHE_PATH = os.getenv("CHROME_CACHE_PATH")
		self.FIREFOX_CACHE_PATH = os.getenv("FIREFOX_CACHE_PATH")

		self.FILE_SET = set()

		self.CHROME_PATH_IMAGE = os.getenv('CHROME_PATH_IMAGE')
		self.CHROME_PATH_DATA = os.getenv('CHROME_PATH_DATA')
		self.CHROME_PATH_HTML = os.getenv('CHROME_PATH_HTML')
		self.CHROME_PATH_COMPRESSED = os.getenv('CHROME_PATH_COMPRESSED')
		self.CHROME_PATH_GOOGLE_DRIVE = os.getenv('CHROME_PATH_GOOGLE_DRIVE')

		self.FIREFOX_PATH_IMAGE = os.getenv('FIREFOX_PATH_IMAGE')
		self.FIREFOX_PATH_DATA = os.getenv('FIREFOX_PATH_DATA')
		self.FIREFOX_PATH_HTML = os.getenv('FIREFOX_PATH_HTML')
		self.FIREFOX_PATH_COMPRESSED = os.getenv('FIREFOX_PATH_COMPRESSED')
		self.FIREFOX_PATH_GOOGLE_DRIVE = os.getenv('FIREFOX_PATH_GOOGLE_DRIVE')

		self.CURRENT_DIRECTORY = os.getcwd()


	def make_directory(self, name_of_directory):

		if not os.path.exists(name_of_directory): 
			os.makedirs(name_of_directory)
			return {'status': True, 'directory_name': name_of_directory, 'exists': False, 'message': 'Directory Created.'}
		return {'status': False, 'directory_name': name_of_directory, 'exists': True, 'message': 'Directory already existed.'}

	def _get_global(self):
		return self

	def is_possible_google_drive_data(self, file):
		info = subprocess.check_output(["strings", file])
		if 'https://lh3.google.com/' in str(info) or 'https://lh3.googleusercontent.com' in str(info): return True
		return False

	def segregate(self, paths):

		path = paths['path']

		urls = dict()
		emails_to_url = dict()
		self.FILE_SET = set()

		for root, dirs, files in os.walk(path, topdown=True):
			for name in files: self.FILE_SET.add(os.path.join(root, name))

		for index, file in enumerate(self.FILE_SET):

			info = ''
			try:
				info = subprocess.check_output(["file", file])
				website_info = str(subprocess.check_output(["strings", file]))
			except Exception as e:
				pass

			if website_info or len(website_info) > 20:
				_temp = UTILITIES().extract_urls(website_info)
				for url in _temp:
					if url not in urls: urls[url] = 1
					else:  urls[url] += 1

					emails_to_url = UTILITIES().emails_to_file_mapping(file, url, emails_to_url)

			try:
				if 'image' in str(info):
					copyfile(file, paths['current_directory']+'/'+paths['image'] + '/' + file.split('/')[-1])
				elif 'html' in str(info):
					copyfile(file, paths['current_directory']+'/'+paths['html'] + '/' + file.split('/')[-1])
				elif 'gzip' in str(info) or 'zlib' in str(info):
					copyfile(file, paths['current_directory']+'/'+paths['compressed'] + '/' + file.split('/')[-1])
				else:
					copyfile(file, paths['current_directory']+'/'+paths['data'] + '/' + file.split('/')[-1])
				if self.is_possible_google_drive_data(file):
					copyfile(file, paths['current_directory']+'/'+paths['gdrive'] + '/' + file.split('/')[-1])
			except Exception as e:
				pass

		return urls, emails_to_url

	def run(self):

		start =  time.time()
		t = self.make_directory(self.CHROME_PATH_IMAGE)
		f = self.make_directory(self.CHROME_PATH_DATA)
		t = self.make_directory(self.FIREFOX_PATH_IMAGE)
		t = self.make_directory(self.FIREFOX_PATH_COMPRESSED)
		t = self.make_directory(self.CHROME_PATH_COMPRESSED)
		f = self.make_directory(self.FIREFOX_PATH_DATA)
		t = self.make_directory(self.FIREFOX_PATH_HTML)
		f = self.make_directory(self.CHROME_PATH_HTML)
		t = self.make_directory(self.FIREFOX_PATH_GOOGLE_DRIVE)
		f = self.make_directory(self.CHROME_PATH_GOOGLE_DRIVE)


		print("Directories created!\n")
		

		paths = {'path': self.FIREFOX_CACHE_PATH,
				'image': self.FIREFOX_PATH_IMAGE,
				'gdrive': self.FIREFOX_PATH_GOOGLE_DRIVE,
				'compressed': self.FIREFOX_PATH_COMPRESSED,
				'data':self.FIREFOX_PATH_DATA,
				'html':self.FIREFOX_PATH_HTML,
		}
		print( '-'*60 + '\n Starting firefox cache analysis \n' + ''*60)
		urls_firefox, files_to_url_firefox = self.segregate(paths)
		print( '-'*60 + '\n Done with firefox cache analysis \n' + '-'*60)

		paths = {'path': self.CHROME_CACHE_PATH,
				'image': self.CHROME_PATH_IMAGE,
				'gdrive': self.CHROME_PATH_GOOGLE_DRIVE,
				'compressed': self.CHROME_PATH_COMPRESSED,
				'data':self.CHROME_PATH_DATA,
				'html':self.CHROME_PATH_HTML,
		}

		print( '-'*60 + '\n Starting chrome cache analysis \n' + '-'*60)
		urls_chrome, files_to_url_chrome = self.segregate(paths)
		print( '-'*60 + '\n Done with chrome cache analysis \n' + '-'*60)

		for link in urls_firefox:
			if link in urls_chrome: urls_chrome[link] += 1
			else: urls_chrome[link] = 1

		java_files = UTILITIES().segregation_of_data(urls_chrome, ['.java'], [])
		java_files = dict(sorted(java_files.items(), key=lambda item: item[1], reverse=True))
		
		links = UTILITIES().segregation_of_data(urls_chrome, ['http', '.edu', '.com', '.io'], ['document', 'script', '$image', '$script', 'href', 'data.', 'div','subdocument', '@', '['])
		links = dict(sorted(links.items(), key=lambda item: item[1], reverse=True))
		
		# ['.jpg', '.png', '.gif', 'document', 'script', '$image', '$script', 'href', 'data.', 'div', 'image','subdocument']
		
		# emails = UTILITIES().segregation_of_data(urls_chrome, ['@'], ['[', '~', '^', '#', '-'])
		# email_cleaning = dict()

		# for key in emails:
		# 	found = False
		# 	for not_allowed in ['/', '\\', '}', '{', ':']:
		# 		if not_allowed in key:
		# 			found = True
		# 	if not found: email_cleaning[key] = emails[key]

		# emails = email_cleaning
		# emails = dict(sorted(emails.items(), key=lambda item: item[1], reverse=True))
		# ['document', 'script', '$image', '$script', 'href', 'data.', 'div', 'http','image','subdocument']

		for i in files_to_url_chrome:
			if i in files_to_url_firefox:
				for k in files_to_url_chrome[i]:
					files_to_url_firefox[i].append(k)
			else:
				files_to_url_firefox[i] = files_to_url_chrome[i]
		
		images = UTILITIES().segregation_of_data(urls_chrome, ['.jpg', '.png', '.gif'], ['|'])
		images = dict(sorted(images.items(), key=lambda item: item[1], reverse=True))

		UTILITIES().write_to_file_csv('urlist.csv', links)
		UTILITIES().write_to_file_csv('emaillist.csv', files_to_url_firefox)
		UTILITIES().write_to_file_csv('images.csv', images)
		UTILITIES().write_to_file_csv('java_files.csv', java_files)

		domains = UTILITIES().domain_name_ranking(['urlist.csv', 'images.csv'])
		domains = dict(sorted(domains.items(), key=lambda item: item[1], reverse=True))
		UTILITIES().write_to_file_csv('top_domains.csv', domains)

		print('Processing took ', int((time.time() - start))/60 +1 , ' minutes')

