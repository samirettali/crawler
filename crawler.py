#!/usr/bin/python3
import os
import sys
import time
import urllib
import httplib2
import threading
import optparse
import http.client
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

urls = list()
visited = list()
depths = list()
threads_number = 0
index = 0

class Crawler (threading.Thread):

  def __init__(self, thread_number):
    threading.Thread.__init__(self)
    self.thread_number = thread_number

  def run(self):
    crawl(self.thread_number)
    print('thread %d ended' % self.thread_number)


def crawl(thread_number):

  global urls
  global visited
  global depths
  global index

  textfile = open('loot.txt','a')

  max_depth = 1
  download = True
  download_dir = 'loot'
  extensions = ['pdf', 'txt', 'mobi', 'jpg', 'png', 'jpeg']

  if download_dir[-1:] != '/':
    download_dir += '/'

  http = httplib2.Http()

  while index < len(urls) and depths[index] <= max_depth:

    url = urls[index]
    if 'http' in url:

      if url in visited:
        print('thread %d\nalready visited %s\n' % (thread_number, url))
        index += 1
        continue

      if url[0] == '#':
        print('thread %d\nskipping %s' % (thread_number, url))
        index += 1
        continue

      print('thread %d\nvisiting %s' % (thread_number, url))

      try:
        status, response = http.request(url)
        if download:
          for ext in extensions:
            if url[-(len(ext) + 1):] == '.' + ext:
              parsed_url = urllib.parse.urlparse(url)
              domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
              print(domain)
              directory = domain.replace('http://', '').replace('www.', '').replace('/', '')

              if(not os.path.exists(download_dir + directory)):
                os.makedirs(download_dir + directory)

              print('downloading %s' % os.path.basename(url))
              urllib.request.urlretrieve(url, download_dir + directory + '/' + os.path.basename(url))

        soup = BeautifulSoup(response, 'html.parser')
        visited.append(url)
        n = 0

        for link in soup.find_all('a'):

          l = link.get('href')
          if l != None and len(l) > 0:

            if 'http' not in l:
              l = urllib.parse.urljoin(url, l)

            if l not in visited and l not in urls:
              n += 1
              urls.append(l)
              depths.append(depths[index] + 1)
              textfile.write(l + '\n')

        print('%d links found, depth %d\n%d visited, %d to visit\n' % (n, depths[index], index + 1, len(urls) - index - 1))

      except httplib2.RedirectLimit as e:
        print('redirection limit on %s\n' % url)
      except httplib2.ServerNotFoundError as e:
        print('server not found %s\n' % url)
      except Exception as e:
        print('exception: %s\n' % sys.exc_info()[0])

    index += 1

  textfile.close()

def main():
  global threads_number
  global depths
  global urls
  global index

  parser = optparse.OptionParser('usage:./crawler.py -f file.txt -u urls -t threads')
  parser.add_option('-f', dest = 'read', type = 'string', help = 'name of the file containing the urls')
  parser.add_option('-u', dest = 'urls', type = 'string', help = 'space separated urls, be sure to surround them with apices')
  parser.add_option('-t', dest = 'threads', type = 'int', help = 'number of threads to run')

  (options, args) = parser.parse_args()

  if options.threads != None:
    threads_number = options.threads

  if options.read != None:
    with open(options.read) as f:
      urls = f.readlines()

  if options.urls != None:
    new_urls = options.urls.split(' ')
    urls += new_urls

  for i in range(len(urls)):
    urls[i] = urls[i].rstrip()

  depths = [0] * len(urls)

  if threads_number == 0 | len(urls) == 0:
    print(parser.usage)
    exit(0)

  threads = list()
  for i in range(threads_number):
      threads.append(Crawler(i))

  for t in threads:
    t.start()
    while len(urls) - index < threads_number:
      print('waiting for enough urls to start all the threads')
      time.sleep(1)

if __name__ == '__main__':
    main()
