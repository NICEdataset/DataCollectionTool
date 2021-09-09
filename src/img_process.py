import os, base64

def img2tsv(fld, fld_out):
	assert(os.path.exists(fld))
	if not os.path.exists(fld_out):
		os.makedirs(fld_out)
	lines = []
	n = 0
	m = 0
	print('preparing listdir, which may take quite a while...')
	for file in os.listdir(fld):
		if n == 0:
			print('start encoding')
		n += 1
		name = file.split('.')[0]
		code = base64.b64encode(open(fld + '/' + file, 'rb').read())
		lines.append(name + '\t' + code.decode('utf-8'))
		if n % 1e3 == 0:
			print('[%s] processed %i k img'%(fld[-7:], n/1e3))
			with open(fld_out + '/part%i.tsv'%m, 'w', encoding='utf-8') as f:
				f.write('\n'.join(lines))
			lines = []
			m += 1
	print('writing part %i'%m)
	with open(fld_out + '/part%i.tsv'%m, 'w', encoding='utf-8') as f:
		f.write('\n'.join(lines))

if __name__ == '__main__':
	root = 'f:/reddit_img/'
	for mo in range(12, 12+1):
		mo = str(mo)
		if len(mo) == 1:
			mo = '0'+mo
		date = '2012-' + mo
		print(date)
		img2tsv('%s/img/%s'%(root, date), '%s/img_encoded/%s'%(root, date))
