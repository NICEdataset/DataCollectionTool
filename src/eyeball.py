import os, shutil
import random as np

date = '2013-04'
path = 'F:/reddit_img/conv/all/%s.tsv'%date
fld_img = 'F:/reddit_img/img/%s/'%date
fld_out = 'F:/reddit_img/eyeball/'

n_sub = 10
lines = dict()
for i in range(n_sub):
	lines[i] = []
	fld_sub = fld_out + str(i)
	if not os.path.exists(fld_sub):
		os.makedirs(fld_sub)

n = 0
m = 0
for line in open(path, encoding='utf-8'):
	n += 1
	ss = line.strip('\n').split('\t')
	img_id = ss[0]
	for ext in ['.png','.jpg','.gif']:
		path_img = fld_img + img_id + ext
		if os.path.exists(path_img):
			m += 1
			sub = m % n_sub
			shutil.copyfile(path_img, fld_out + '%i/%s%s'%(sub, img_id, ext))
			lines[sub].append(line.strip('\n'))
			break

	if n % 100 == 0:
		print('picked %i/%i examples'%(m, n))

	if m / n_sub == 1000 and m % n_sub == 0:
		break

header = '\t'.join(['img_id','title','body','turn0','turn1','...'])
for i in range(n_sub):
	with open(fld_out + '%i/conv.tsv'%i, 'w', encoding='utf-8') as f:
		f.write(header+'\n')
		f.write('\n'.join(lines[i]))

