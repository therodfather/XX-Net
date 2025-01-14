import time

from xlog import getLogger
xlog = getLogger("smart_router")


class SocketWrap(object):

    def __init__(self, sock, ip=None, port=None, host="", target=""):
        self._sock = sock
        self.ip = ip
        self.port = port
        self.host = host
        self.target = target
        self.recved_data = 0
        self.recved_times = 0
        self.sent_data = 0
        self.sent_times = 0
        self.create_time = time.time()
        self.closed = False
        self.replace_pattern = None

        self.buf = []
        self.buf_size = 0
        self.buf_num = 0

    def __getattr__(self, attr):
        return getattr(self._sock, attr)

    def close(self):
        # xlog.debug("%s close", self)
        self._sock.close()
        self.closed = True

    def is_closed(self):
        return self.closed

    def __str__(self):
        return "%s[%s]:%d" % (self.host, self.ip, self.port)

    def recv(self, bufsiz, flags=0):
        d = self._sock.recv(bufsiz, flags)
        if self.replace_pattern and b" HTTP/1.1\r\n" in d:
            line_end = d.find(b"\r\n")
            req_line = d[:line_end]

            words = req_line.split()
            if len(words) == 3:
                method, url, http_version = words
                url = url.replace(self.replace_pattern[0], self.replace_pattern[1])

                d = b"%s %s %s" % (method, url, http_version) + d[line_end:]

        # xlog.debug("%s recv %d", self, len(d))
        return d

    def add_dat(self, data):
        # xlog.debug("%s add data %d", self, len(data))
        self.buf.append(data)
        self.buf_size += len(data)
        self.buf_num += 1

    def get_dat(self):
        if not self.buf:
            return b""
        dat = self.buf.pop(0)
        self.buf_size -= len(dat)
        self.buf_num -= 1
        return dat

    def restore_dat(self, dat):
        # xlog.debug("%s restore_dat %d", self, len(dat))
        self.buf.insert(0, dat)
        self.buf_size += len(dat)
        self.buf_num += 1
