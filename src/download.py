from os import listdir
from os.path import isfile, join

import urllib2
import os
import wget
import requests
import unirest
# import OCR_API as ocr
import json, pdb

logger_file = open("log.txt", "w")


def check_for_repetition_in_id_list(data_path):
	id_list = []

	files_list = [f for f in listdir(data_path)]

	for file in files_list:
		if not(file.endswith('tsv')):
			continue
		print(file)
		input_file = open(data_path + file, encoding="utf8")
		for line in input_file:
			line_parts = line.split('\t')
			if line_parts[0] == "id":
				continue
			if line_parts[0] in id_list:
				return False
			else:
				id_list.append(line_parts[0])
		print("id_list size is now " + str(len(id_list)))
	return True

def read_refrence_ids(ref_data_path, file_name):
	refrence_ids = []
	input_file = open(ref_data_path + file_name, encoding="utf8")
	for line in  input_file:
		line_parts = line[:-1].split('\t')
		refrence_ids.append(line_parts[0])
	return refrence_ids

def check_if_refrece_related(rid):
	return rid in refrence_ids


def write_the_url_id_list(data_path, ref_data_path):
	files_list = [f for f in listdir(data_path)]

	for file in files_list:
		
		if not(file.endswith('.tsv')):
			continue
		
		print("processing file: " + file)
		refrence_ids = read_refrence_ids(ref_data_path, file)
		
		input_file = open(data_path + file, encoding="utf8")
		output_file = open(data_path + 'url_id_map/' + file , 'w', encoding="utf8")
		url_id_map = {}
		
		for line in input_file:
			line_parts = line[:-1].split("\t")
			url_id_map[line_parts[0]] = line_parts[-1]

		for element_key in url_id_map:
			if element_key in refrence_ids:
				output_file.write(element_key + '\t' + url_id_map[element_key] + '\n')

def download_by_url(url, data_img_directory, file_name):
	try:
		request = urllib2.urlopen(url, timeout=2)
		with open(data_img_directory + file_name, 'wb') as f:
			f.write(request.read())
		return True
	except Exception:
		print("error from download_by_url")
		return False

	"""
	# import pdb; pdb.set_trace()
	global logger_file
	try:
		wget.download(url, data_img_directory + file_name)
	except Exception as e:
		logger_file.write(str(e) + '\t')
		logger_file.write("for url " + url + '\n')
		print(e)
		pass
		"""
	#urllib2.urlretrieve(url, data_img_directory + file_name)


def find_extention(url):
	if url.endswith(".jpg") or url.endswith('.png') or url.endswith('.gif'):
		return url[-4:]
	elif url.endswith(".JPG"):
		return '.jpg'
	elif url.endswith(".jpeg"):
		return url[-5:]
	else:
		return None


def get_imgur_link_rapidAPI(url):
	if(".com") not in url:
		return None
	response = unirest.get("https://imgur-apiv3.p.rapidapi.com/3/image" + url[url.index(".com") + 4:],
		headers={
		    "X-RapidAPI-Host": "imgur-apiv3.p.rapidapi.com",
		    "X-RapidAPI-Key": "Your Key",
		    "Authorization": "You client-ID"
  		}
	)
	# import pdb; pdb.set_trace()
	if response.code == 200:
		return str(response.body['data']['link'])
	elif response.code == 429:
		import pdb; pdb.set_trace()
	else:
		# import pdb; pdb.set_trace()
		return None




def get_imgur_link(url):

	if(".com") not in url:
		return None
	api_url = "https://api.imgur.com/3/image/" + url[url.index(".com") + 4:]

	headers = {
	    'Authorization': "You client-ID",
	    'User-Agent': "PostmanRuntime/7.15.0",
	    'Accept': "*/*",
	    'Cache-Control': "no-cache",
	    'Postman-Token': "Your Postman-Token",
	    'Host': "api.imgur.com",
	    'accept-encoding': "gzip, deflate",
	    'Connection': "keep-alive",
	    'cache-control': "no-cache"
	    }

	response = requests.request("GET", api_url, headers=headers)
	if response.status_code == 200:
		return response.json()['data']['link']
	elif response.status_code == 429:
		import pdb; pdb.set_trace()
	else:
		# import pdb; pdb.set_trace()
		return None



def read_and_download_img(data_path, data_img_directory):
	url_id_map_files_list = [f for f in listdir(data_path + 'url_id_map/')]
	no_content_img_urls = open("no_content_found.txt", 'w')

	for file in url_id_map_files_list:
		
		if file.startswith('2011'):
			continue
		mo = int(file.replace('.tsv','').split('-')[1])
		if mo < 9:
			continue

		print("processing file: " + file)
		no_content_img_urls.write("processing file:\t" + file + '\n')

		input_file = open(data_path + 'url_id_map/' + file)

		n_line = 0
		n_skip = 0
		n_new = 0
		for line in input_file:
			n_line += 1
			#if mo == 8 and n_line < 248600:
			#	continue

			#if n_line < 67330:
			#	continue
			if n_line % 10 == 0:
				print('\n[%s] line = %i, already %i, new %i'%(file, n_line, n_skip, n_new))
			line_parts = line[:-1].split('\t')
			if line_parts[0] == 'id':
				continue
			file_extention = find_extention(line_parts[1])
			fld_save = data_img_directory + file[:-4] + '/'
			if file_extention is None:
				ext = ['.jpg','.png','.gif']
			else:
				ext = [file_extention]
			already = False
			for e in ext:
				if os.path.exists(fld_save + line_parts[0] + e):
					already = True
					break
			if already:
				n_skip += 1
				continue

			url = line_parts[1]
			if  file_extention == None:
				try:
					url = get_imgur_link_rapidAPI(line_parts[1])
				except Exception:
					print('error from get_imgur_link_rapidAPI')
					continue
				if url == None:
					# import pdb; pdb.set_trace()
					no_content_img_urls.write("url was none for " + line)
					continue
				file_extention = find_extention(url)
				if  file_extention == None:
					no_content_img_urls.write("url is " + url + "no extention found for " + line)
					continue

			if not os.path.isdir(data_img_directory + file[:-4]):
				os.mkdir(data_img_directory + file[:-4])

			print(n_line, url)
			ok = download_by_url(url, fld_save, line_parts[0] + file_extention)
			if ok:
				n_new += 1


def download_object_json(data_path, data_json_obj_path):
	url_id_map_files_list = [f for f in listdir(data_path + 'url_id_map/')]
	no_content_img_urls = open("no_content_found.txt", 'w')

	print(len(url_id_map_files_list))
	for file in url_id_map_files_list:

		print("processing file: " + file)
		no_content_img_urls.write("processing file:\t" + file + '\n')

		input_file = open(data_path + 'url_id_map/' + file)

		for line in input_file:
			line_parts = line[:-1].split('\t')
			if line_parts[0] == 'id':
				continue
			file_extention = find_extention(line_parts[1])
			url = line_parts[1]

			if  file_extention == None:
				url = get_imgur_link_rapidAPI(line_parts[1])
				if url == None:
					# import pdb; pdb.set_trace()
					no_content_img_urls.write("url was none for " + line)
					continue
				file_extention = find_extention(url)
				if  file_extention == None:
					no_content_img_urls.write("url is " + url + "no extention found for " + line)
					continue

			if not os.path.isdir(data_json_obj_path + file[:-4]):
				os.mkdir(data_json_obj_path + file[:-4])

			# download_by_url(url, data_json_obj_path + file[:-4] + '/', line_parts[0] + file_extention )

			image_json = ocr.get_image_objects_json(url)
			if image_json == None:
				continue
			my_json = image_json.decode('utf8').replace("'", '"')
			data = json.loads(my_json)

			with open(data_json_obj_path + file[:-4] + '/'+ line_parts[0] + '.json' , 'w') as outfile:  
			    json.dump(data, outfile, indent=4)


def make_and_download():
	ref_data_path = "F:/reddit_img/conv/all/"
	data_path = "f:/reddit_img/RS/"
	data_img_directory = "f:/reddit_img/img/"
	data_json_obj_path = "f:/reddit_img/json/"


	#write_the_url_id_list(data_path, ref_data_path)
	read_and_download_img(data_path, data_img_directory)
	# download_object_json(data_path, data_json_obj_path)


if __name__ == "__main__":
	make_and_download()