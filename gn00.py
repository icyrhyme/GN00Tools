# -*- coding:utf-8 -*- 
import urllib2
import urllib
import cookielib
import re
import urlparse
import collections
import random
from bs4 import BeautifulSoup
import codecs
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
        #locked_pattern = re.compile('<div class="locked">')
        template_post_page_url = 'http://www.gn00.com/thread-{0}-1-1.html'
        post_page_url = template_post_page_url.format(tid)
        post_page = urllib2.urlopen(post_page_url)
        post_page_unicode = post_page.read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(post_page_unicode)
        post_form = soup.find("form", {'id': 'fastpostform'})
        div_locked = soup.find("div", {"class": "locked"})
        if not post_form or div_locked == None:
            return False
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
        try:
            req = urllib2.Request(post_url, post_data)
            fd = self.opener.open(req)
            print fd.read()
            return True
        except:
            return False
            
        
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
                    
    def get_posts_summary(self, fid):
        f = codecs.open("temp.txt", "w", "utf-8")
        template_forum_url = 'http://www.gn00.com/forum-{0}-{1}.html'
        forum_url = template_forum_url.format(fid, 1)
        first_page = urllib2.urlopen(forum_url)
        pattern = re.compile('<span title="[^\s]+ (\d+) [^\s]+">')
        url_pattern = re.compile('thread-(\d+)')
        text = first_page.read()
        res = pattern.search(text)
        page_num = int(res.group(1))

        for i in range(page_num):
            forum_url = template_forum_url.format(fid, i + 1)
            forum = urllib2.urlopen(forum_url)
            forum_unicode = forum.read().decode('utf-8', 'ignore')
            #if i == 0:
            #    print forum_unicode
            soup = BeautifulSoup(forum_unicode)
            posts = soup.find_all("tbody", {"id": re.compile("thread")})
            for post in posts:
                a_xst = post.find("a", {"class": "xst"})
                post_url = urlparse.urljoin(forum_url, str(a_xst['href']))
                title = a_xst.get_text()

                cites = post.find_all("cite")
                author = cites[0].get_text()
                author = author.strip()
                last_reply = cites[1].get_text()
                last_reply = last_reply.strip()

                td_num = post.find("td", {"class": "num"})
                try:
                    reply_num = int(td_num.a.get_text())
                    see_num = int(td_num.em.get_text())
                except ValueError:
                    print td_num.a.get_text()
                    print td_num.em.get_text()

                res = url_pattern.search(post_url)
                tid = int(res.group(1))
                #f.write("%s %s\n" % (author, post_url))
                yield {
                    'fid':          fid,
                    'tid':          tid,
                    'url':          post_url,
                    'title':        title,
                    'author':       author,
                    'last_reply':   last_reply,
                    'reply_num':    reply_num,
                    'see_num':      see_num
                }
                

if __name__ == "__main__":
    gn00 = TechOtaku()
    gn00.login("轻舟过", "XX")
    #max_reply = -1
    #max_reply_post = None
    replied = 0
    for post in gn00.get_posts_summary(215):
        if replied > 50:
            break
        if gn00.post_reply(post['fid'], post['tid'], random.choice(['看看', '戳开'])):
            replied += 1
    #http://www.gn00.com/plugin.php?id=dsu_paulsign:sign&6a8ebcb5&infloat=yes&handlekey=dsu_paulsign&inajax=1&ajaxtarget=fwin_content_dsu_paulsign
    #formhash	6a8ebcb5
    #qdxq	fd
    #qdmode	1
    #todaysay	study!
    #fastreply	0
    #http://www.gn00.com/plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1
    #for post in gn00.get_posts_summary(45):
    #    if post['reply_num'] > max_reply:
    #        max_reply_post = post
    #        max_reply = post['reply_num']
    #print max_reply_post
    #gn00.post_reply('830', '85577', 'WZ')
    #gn00.get_candy('45')
