from urlextract import URLExtract
import csv
import subprocess
from urllib.parse import urlparse

class UTILITIES(object):
	"""docstring for UTILITIES"""
	def __init__(self,):
		self.n = None

	def extract_urls(self, text):
		urls = list()
		extractor = URLExtract()
		urls += extractor.find_urls(text)
		return urls

	def write_to_file(self, file_name, my_dict):
		with open(file_name, 'w') as f:
			w = csv.DictWriter(f, my_dict.keys())
			w.writeheader()
			w.writerow(my_dict)

	def write_to_file_csv(self, file_name, my_dict):
		with open(file_name, 'w') as csv_file:
			writer = csv.writer(csv_file)
			for key, value in my_dict.items():
				writer.writerow([key, value])

	# data to be segregated
	# delimiters to segregate on 
	# remove if any of one of these delimiters is found
	def segregation_of_data(self, data, delimiters, not_list):
		output = dict()
		for data_point in data:
			found = False
			for limiter in delimiters:
				if limiter in data_point:
					found=True
					break

			for nt in not_list:
				if nt in data_point:
					found=False
					break
			if found: output[data_point] = data[data_point] 
		return output

	def url_extraction_from_links(self, link):
		data = urlparse(link)
		return data

	def is_possible_google_drive_data(self, file):
		info = subprocess.check_output(["strings", file])
		if 'https://lh3.google.com/' in str(info) or 'https://lh3.googleusercontent.com' in str(info): return True
		return False

	def emails_to_file_mapping(self, file, url, files_to_url):
		if 'Users' in file:
			p=False
			if '@' in url:
				p=True 
			for symb in ['[', '~', '^', '#', '-', ':', '{', '}', '/', '\\']:
				if symb in url:
					p=False
					break
			if p:
				if url in files_to_url: files_to_url[url].add(file)
				else: 
					files_to_url[url] = set()
					files_to_url[url].add(file)
		return files_to_url


	def domain_name_ranking(self, files):
		domains=dict()
		for file in files:
			with open(file, 'r') as fd:
				csv_file = csv.reader(fd, delimiter=',')
				for row in csv_file:
					parsed_uri = urlparse(row[0])
					result = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
					if '///' in result: continue 
					if result in domains: domains[result] += 1
					else: domains[result] = 1
		return domains
