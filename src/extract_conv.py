from shared import *

def extract_comments(path_bz2, path_out, path_sub):
	# extract comment from path_bz2 filter by
	#   link_id in sids
	# 	not deleted
	#	len > 1
	# 	no comment in line

	name_in = get_fname(path_bz2)
	sids = set()
	f = open(path_sub, encoding='utf-8')
	header = f.readline().strip('\n').split('\t')
	ix_sid = header.index('id')
	for line in f:
		sids.add(TAG_RS + line.strip('\n').split('\t')[ix_sid])		# 't3_' is a tag/prefix for d
	print('# sid = %i'%len(sids))
	
	fields = [ "id", "author", "parent_id", "link_id", "score", "body"]
	with open(path_out, 'w', encoding='utf-8') as f:
		f.write('\t'.join(fields) + '\n')

	n_total = 0
	n_err = 0
	n_save = 0
	lines = []

	for line in bz2.open(path_bz2, 'rt', encoding="utf-8"):
		n_total += 1
		if n_total%1e5 == 0:
			print('[%s] selected %.3f M from %.1f M. Error %.2f k'%(
				name_in, n_save/1e6, n_total/1e6, n_err/1e3))
			if len(lines) > 0:
				with open(path_out, 'a', encoding='utf-8') as f:
					f.write('\n'.join(lines) + '\n')
				lines = []
		try:
			d = json.loads(line)
			sid = d['link_id']
		except Exception:
			n_err += 1
			continue

		if sid in sids:
			lines.append('\t'.join([get_v(d, k) for k in fields]))
			n_save += 1

	s = '[%s] finally, selected %i (%.2f M) from %i (%.2f M). Error %i (%.2f k)'%(
		name_in, n_save, n_save/1e6, n_total, n_total/1e6, n_err, n_err/1e3)
	print(s)
	with open(path_out, 'a', encoding='utf-8') as f:
		f.write('\n'.join(lines))
	with open(path_out.replace('.tsv','') + '.log', 'w', encoding='utf-8') as f:
		f.write(s)


def get_leaf_conv(path_sub, path_comm, path_out, subreddit=None):

	path_log = path_out.replace('.tsv','') + '.log'
	open(path_log, 'w')
	def log(s):
		print(s)
		with open(path_log, 'a') as f:
			f.write(s + '\n')

	log('subreddit = %s'%subreddit)

	title = dict()
	sbody = dict()	# body of submission

	f = open(path_sub, encoding='utf-8')
	header = f.readline().strip('\n').split('\t')
	ix_sid = header.index('id')
	ix_title = header.index('title')
	ix_sbody = header.index('selftext')
	ix_subreddit = header.index('subreddit')
	for line in f:
		cells = line.strip('\n').split('\t')
		if len(cells) != len(header):
			print(header)
			print(cells)
			exit()
		if subreddit is None or cells[ix_subreddit] == subreddit:
			sid = TAG_RS + cells[ix_sid]
			title[sid] = cells[ix_title]
			sbody[sid] = cells[ix_sbody]

	log('# sid = %i'%len(title.keys()))
	
	f = open(path_comm, encoding='utf-8')
	header = f.readline().strip('\n').split('\t')
	ix_sub_id = header.index('link_id')
	ix_comm_id = header.index('id')
	ix_parent_id = header.index('parent_id')
	ix_body = header.index('body')

	parent = dict()
	cbody = dict()
	cid2sid = dict()
	for line in f:
		cells = line.strip('\n').split('\t')
		sid = cells[ix_sub_id]
		if subreddit is None or sid in title:
			cid = TAG_RC + cells[ix_comm_id]
			parent_id = cells[ix_parent_id]
			parent[cid] = parent_id
			cbody[cid] = cells[ix_body]
			cid2sid[cid] = sid

	log('# cid = %i'%len(cbody.keys()))

	leaf = set(cbody.keys())
	for k in parent:
		leaf.discard(parent[k])

	log('# leaf = %i, or %.1f perc'%(len(leaf), 100.*len(leaf)/(len(cbody.keys()) + 1E-6)))

	def get_ancestor_txts(_id, txts):
		if _id in cbody:
			txts = [cbody[_id]] + txts
			return get_ancestor_txts(parent.get(_id), txts)
		elif _id in sbody:
			return [title[_id], sbody[_id]] + txts
		else:
			return [TAG_broken] + txts

	open(path_out, 'w', encoding='utf-8')
	lines = []
	n_broken = 0
	for i, cid in enumerate(leaf):
		try:
			txts = get_ancestor_txts(cid, [])
		except:
			txts = [TAG_broken]
		n_broken += (txts[0] == TAG_broken)
		sid = cid2sid[cid].replace(TAG_RS,'')
		lines.append('\t'.join([sid] + txts))
		if i % 1e5 == 0:
			print('processed %.1f M leaf, broken %.3f'%(i/1e6, n_broken/(i+1)))
			with open(path_out, 'a', encoding='utf-8') as f:
				f.write('\n'.join(lines) + '\n')
			lines = []
	with open(path_out, 'a', encoding='utf-8') as f:
		f.write('\n'.join(lines))

	log('# broken = %i, or %.1f perc'%(n_broken, n_broken/(len(leaf) + 1e-6)*100))