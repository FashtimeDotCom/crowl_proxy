# -*- encoding: utf-8 -*-
from crawl import crawl
import gevent
from gevent.event import AsyncResult
from gevent.pool import Group
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class async_crawl(crawl):

    def __init__(self):
        crawl.__init__(self)
        self.async_jump = AsyncResult()
        self.async_in = AsyncResult()
        self.finished = AsyncResult()

    def put(self, url):
        super(async_crawl, self).put(url)
        self.job_size = self.url_qu.qsize()

    def put_list_url(self, urls):
        super(async_crawl, self).put_list_url(urls)
        self.job_size = self.url_qu.qsize()

    def setObserver(self, observer):
        self.observer = observer

    def run(self, i):
        task_num = self.job_size
        while task_num > 0:
            print "task ", i
            task_num = task_num - 1
            try:
                details = self.url_qu.get(timeout=100)
                url = details["url"]
                print "crawl url", url
            except Exception, e:
                print "Exception crawl run: ", e
                return
            try:
                text = self.crawl_raw(url)
                self.async_jump.set({"url": url, "text": text, "result": details})
                self.async_in.get()
                self.async_in = AsyncResult()
            except Exception, e:
                print e
            finally:
                self.url_qu.task_done()
        # if self.stop == False:
            # self.finished.get()
            # self.stop = True

        # self.finished.set()
        print "task", i, "finished."

    def start(self, num):
        # self.work_group = Group()
        # [gevent.spawn(self.run, i) for i in range(num)]
        # gevent.spawn(self.observer)
        # self.url_qu.join()
        gevent.joinall([gevent.spawn(self.run, i) for i in range(num)]+[gevent.spawn(self.observer)])  # , self.async_jump, self.async_in)])


# ----------TEST CODE-----------
def observer_test(async_jump, async_in):
    # global async_jump, async_in
    while True:
        print "wait before"
        async_jump.get()
        async_jump = AsyncResult()
        print "-----------------",
        print "wait after"
        async_in.set()

if __name__ == "__main__":
    url = ["http://www.cnproxy.com/proxy1.html"]
    # async = async_crawl()
    # async.setObserver(observer_test)
    # async.put_list_url(url*5)
    # async.start(5)
    from observer import Observer
    tester = Observer()
    async = async_crawl()
    async.setObserver(tester.inform)
    async.put_list_url(url*5)
    async.start(5)
