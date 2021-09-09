import urllib.parse, json, time
import http.client

key = 'copy_key_here'
region = 'westcentralus'

class LangDetection():

    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': key,
            }
        self.url = '%s.api.cognitive.microsoft.com'%region
        self.endpoint = '/text/analytics/v2.1/languages?%s'%urllib.parse.urlencode({'showStats': False})

    def get_lang(self, txt):
        body = json.dumps({'documents': [{'id': '1', 'text': txt}]})
        conn = http.client.HTTPSConnection(self.url)
        conn.request('POST', self.endpoint, body, self.headers)
        response = conn.getresponse()
        data = json.loads(response.read())
        conn.close()
        return data['documents'][0]['detectedLanguages'][0]['name']

    def interact(self):
        while True:
            print('---- txt ----')
            txt = input()
            if len(txt) == 0:
                break
            out = self.get_score(txt)
            print(out)

def scan(api, path):
    d_ok = dict()
    n = 0
    m = 0
    for line in open(path, encoding='utf-8'):
        n += 1
        ss = line.strip('\n').split('\t')
        k = ss[0]
        txt = ' '.join(ss[1:])
        if n%100 == 0:
            print('%i of %i are samples not English'%(m, n))
        #print(line.strip('\n'))
        n_try = 0
        lang = None
        while n_try < 3:
            try:
                lang = api.get_lang(txt)
                break
            except:
                print('got error at try %i of line %i, sleep'%(n_try, n))
                n_try += 1
                time.sleep(10)
                print('resume')
        if lang is None:
            continue
        if lang == 'English':
            if k not in d_ok:
                d_ok[k] = True
        else:
            m += 1
            d_ok[k] = False
            print(lang, line)

    lines = ['%s\t%s'%(k, d_ok[k]) for k in d_ok]
    with open(path+'.lang_ok.tsv','w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    api = LangDetection()
    #api.interact()
    scan(api, 'F:/reddit_img/conv/all/2011-01.tsv')