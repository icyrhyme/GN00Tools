# -*- coding:utf-8 -*- 
import urllib2
import urllib
import cookielib
import re
import urlparse
import collections
from bs4 import BeautifulSoup
class TechOtaku:
    def __init__(self):
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(self.opener)
        self.opener.addheaders = [('User-agent', 'IE')]
        #self.author_set = collections.defaultdict(lambda: 0)

    def login(self, username, password):
        url = 'http://www.gn00.com/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
        data = urllib.urlencode({
            'username' : username,
            'password' : password,
            'quickforward' : 'yes',
            'handlekey' : 'ls'
        })
        #print data
        req = urllib2.Request(url, data)
        fd = self.opener.open(req)
        fd.read()
        
    def post_reply(self, fid, tid, msg):
        template_post_page_url = 'http://www.gn00.com/forum.php?mod=viewthread&tid={0}&extra=page%3D1%26filter%3Dauthor%26orderby%3Ddateline%26orderby%3Ddateline'
        post_page_url = template_post_page_url.format(tid)
        post_page = urllib2.urlopen(post_page_url)
        post_page_unicode = post_page.read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(post_page_unicode)
        post_form = soup.find("form", {'id': 'fastpostform'})
        if not post_form:
            return
        post_time = post_form.find("input", {'name': 'posttime'})['value']
        form_hash = post_form.find("input", {'name': 'formhash'})['value']
        use_sig = post_form.find("input", {'name': 'usesig'})['value']
        subject = post_form.find("input", {'name': 'subject'})['value']

        template_post_reply_url = 'http://www.gn00.com/forum.php?mod=post&action=reply&fid={0}&tid={1}&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'
        post_url = template_post_reply_url.format(fid, tid)
        post_data = urllib.urlencode({
            'message': msg,
            'posttime': post_time,
            'formhash': form_hash,
            'usesig': use_sig,
            'subject': subject
        })
        req = urllib2.Request(post_url, post_data)
        fd = self.opener.open(req)
        print fd.read()
        
    def get_candy(self, fid):
        template_forum_url = 'http://www.gn00.com/forum.php?mod=forumdisplay&fid={0}&filter=author&orderby=dateline&page={1}'
        for i in range(200):
            forum_url = template_forum_url.format(fid, i)
            forum = urllib2.urlopen(forum_url)
            pattern = re.compile(u"回帖奖励")
            forum_unicode = forum.read().decode('utf-8', 'ignore')
            soup = BeautifulSoup(forum_unicode)
            posts = soup.find_all("tbody", {"id": re.compile("thread")})
            for post in posts:
                res = pattern.search(post.prettify())
                if res:
                    post_url = str(post.find("a")['href'])
                    post_url = post_url.replace("&amp;", "&")
                    post_url_abs = urlparse.urljoin(forum_url, post_url)
                    parse_res = urlparse.urlparse(post_url)
                    tid = urlparse.parse_qs(parse_res.query)['tid'][0]
                    self.post_reply(fid, tid, "test")

    def get_forum_page(self, fids):
        author_set = collections.defaultdict(lambda: 0)
        for fid in fids:
            template_forum_url = 'http://www.gn00.com/forum-{0}-{1}.html'
            forum_url = template_forum_url.format(fid, 1)
            first_page = urllib2.urlopen(forum_url)
            pattern = re.compile('<span title="[^\s]+ (\d+) [^\s]+">')
            text = first_page.read()
            res = pattern.search(text)
            print text
            print repr(unicode(res.group(1)))
            page_num = int(res.group(1))

            for i in range(page_num):
                forum_url = template_forum_url.format(fid, i + 1)
                page = urllib2.urlopen(forum_url)
                page_unicode = page.read().decode('utf-8', 'ignore')
                soup = BeautifulSoup(page_unicode)
                authors = soup.find_all("td", {"class": "by"})
                for j in range(len(authors)):
                    if j % 2 == 0:
                        #print authors[j].prettify()
                        cite = authors[j].find("cite")
                        if cite:
                            author = cite.get_text()
                            author = author.strip()
                            print author
                            author_set[author] += 1

        print "Hahaha....."
        sorted_author = sorted(author_set.items(), lambda x, y: -cmp(x[1], y[1]))
        for k, v in sorted_author:
            print "%s: %d" % (k, v)
                
                

                

if __name__ == "__main__":
    gn00 = TechOtaku()
    gn00.login("轻舟过", "XXXX")
    gn00.get_forum_page([827, 830, 831, 828, 829, 835])
    #gn00.post_reply('830', '85577', 'WZ')
    #gn00.get_candy('45')
