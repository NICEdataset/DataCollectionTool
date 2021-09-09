
from shared import *
import urllib.request

img_fmt = ['.jpg','.png','.jpeg','.gif']

def extract_submissions(path_in, path_out):
	# extract "valid" submissions from a bz2 zip file (path_in)
	# and save them in a tsv file (path_out)
	# some statistics are recorded in path_log

	assert('/RS_20' in path_in and path_in.endswith('.bz2'))
	fields = [ 
		'id', 'score', 'subreddit', 'num_comments', 'permalink', 
		'title', 'selftext', 'over_18', 'author', 'url',
		]
	with open(path_out, 'w', encoding='utf-8') as f:
		f.write('\t'.join(fields) + '\n')
	name_in = get_fname(path_in)

	n_total = 0
	n_err = 0
	n_load = dict()
	n_img = dict()
	lines = []

	for line in bz2.open(path_in, 'rt', encoding="utf-8"):
		n_total += 1
		if n_total%1e5 == 0:
			print('[%s] selected %.3f M from %.1f M. Error %.2f k'%(
				name_in, sum(n_img.values())/1e6, n_total/1e6, n_err/1e3))
			if len(lines) > 0:
				with open(path_out, 'a', encoding='utf-8') as f:
					f.write('\n'.join(lines) + '\n')
				lines = []
		try:
			d = json.loads(line)
			subreddit = d['subreddit']
		except Exception:
			n_err += 1
			continue

		if subreddit not in n_load:
			n_load[subreddit] = 0
			n_img[subreddit] = 0
		n_load[subreddit] += 1

		if d['num_comments'] < 1:
			continue

		if 'url' in d:
			url = d['url'].lower()
			has_img = False
			for c in ['imgur.com'] + img_fmt:
				if c in url:
					has_img = True
					break
			if has_img:
				lines.append('\t'.join([get_v(d, k) for k in fields]))
				n_img[subreddit] += 1


	n_img_total = sum(n_img.values())
	s = '[%s] finally, selected %i (%.2f M) from %i (%.2f M). Error %i (%.2f k)'%(
		name_in, n_img_total, n_img_total/1e6, n_total, n_total/1e6, n_err, n_err/1e3)
	print(s)
	with open(path_out, 'a', encoding='utf-8') as f:
		f.write('\n'.join(lines))

	log = []
	log.append(s)
	log.append('\t'.join(['subreddit','has_img','total']))
	for k in n_load:
		log.append('\t'.join([k, '%i'%n_img[k], '%i'%n_load[k]]))
	with open(path_out.replace('.tsv','') + '.log', 'w') as f:
		f.write('\n'.join(log))





def merge_log(years, fld_out):
	n_img = dict()
	n_load = dict()
	for year in years:
		for date in get_dates(year):
			lines = open(fld_out + '/sub_%s.log'%date, encoding='utf-8').readlines()
			for line in lines[2:]:
				k, img, load = line.strip('\n').split('\t')
				if k not in n_img:
					n_img[k] = 0
					n_load[k] = 0
				n_img[k] += int(img)
				n_load[k] += int(load)

	path_out = fld_out + '/RS_log_'
	if len(years) == 1:
		path_out += str(years[0])
	else:
		path_out += '%i-%i'%(min(years), max(years))
	path_out += '.tsv'
	lines = ['\t'.join(['subreddit','has_img','total','ratio'])]
	for k in n_load:
		lines.append('\t'.join([k, '%i'%n_img[k], '%i'%n_load[k], '%.4f'%(n_img[k]/n_load[k])]))
	with open(path_out, 'w', encoding='utf-8') as f:
		f.write('\n'.join(lines))



def download_img(path_in, fld_out):
	f = open(path_in, encoding='utf-8')
	header = f.readline().strip('\n').split('\t')
	ix_sid = header.index('id')
	ix_url = header.index('url')

	n_success = 0
	n_total = 0
	n_exist = 0

	for line in f:
		n_total += 1
		if n_total % 100 == 0:
			print('total %.2fk (exist %.2fk) from %.1fk'%(n_success/1e3, n_exist/1e3, n_total/1e3))
		ss = line.strip('\n').split('\t')
		if len(ss) < ix_url + 1:
			continue
		sid = ss[ix_sid]
		url = ss[ix_url]
		if '//imgur' in url:
			imgur_id = url.strip('/').split('/')[-1]
			url = 'http://i.imgur.com/%s.jpg'%imgur_id
		ext = url.split('.')[-1]
		if '.'+ext in img_fmt:
			path_out = fld_out + '/%s.%s'%(sid, ext)
		else:
			continue
		if os.path.exists(path_out):
			n_exist += 1
			n_success += 1
			continue
		try:
			urllib.request.urlretrieve(url, path_out)
			n_success += 1
		except:
			pass
		time.sleep(0.1)




