import sys, traceback, json, bz2, time, os

# defined by the dump
TAG_RC = 't1_'
TAG_RS = 't3_'

# defined by us
TAG_na = '[none]'
TAG_broken = '[broken]'

def get_dates(year):
	dates = []
	for m in range(1, 12+1):
		mm = str(m)
		if len(mm) == 1:
			mm = '0'+mm
		dates.append('%i-%s'%(year, mm))
	return dates


def makedirs(fld):
	if not os.path.exists(fld):
		os.makedirs(fld)

def get_fname(path):
	return path.split('/')[-1].split('.')[0]

def get_v(d, k):
	v = d.get(k, TAG_na)
	if isinstance(v, str):
		for c in ['\r','\n','\t']:
			v = v.replace(c,' ')
		return v
	else:
		return str(v)