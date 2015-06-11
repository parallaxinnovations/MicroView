import os
import urllib2
import tempfile

try:
    import paramiko
    import re
    use_sftp = 1

    class SFTPBaseHandler(urllib2.BaseHandler):

        """URLLib2 basehandler that handles sftp requests"""

        def sftp_open(self, req):
            m = re.compile('(.*):(.*)@(.*)')
            s = m.match(req.get_host())
            if (s):
                uname, pword, host = s.groups()
            else:
                uname = ''
                pword = ''
                host = req.get_host()
            t = paramiko.Transport(host)
            t.connect(username=uname, password=pword)
            self._sftp = paramiko.SFTP.from_transport(t)
            s = self._sftp.open(req.get_selector())
            return s
except:
    use_sftp = 0


class URLManager(object):

    def __init__(self):
        global use_sftp
        if use_sftp == 1:
            o = urllib2.build_opener()
            o.add_handler(SFTPBaseHandler())
            urllib2.install_opener(o)
        self._tempfiles = []

    def __del__(self):
        """cleanup tempfiles"""
        for i in self._tempfiles:
            os.unlink(i)

    def getURL(self, url):
        """given a single-file URL, get the file, return a local filename version of the url"""
        s = tempfile.mkstemp(os.path.splitext(url)[-1])
        self._tempfiles.append(s[1])
        f = os.fdopen(s[0], 'wb')
        u = urllib2.urlopen(url)
        # copy file here
        st = u.read(4096)
        while st:
            f.write(st)
            st = u.read(4096)
        f.close()
        u.close()
        return s[1]
