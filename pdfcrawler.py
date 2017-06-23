#!/usr/bin/python3
import os
import sys
import urllib
import httplib2
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

def main():
  textfile = open('depth_1.txt','wt')
  urls = list()
  visited = list()
  urls.append(sys.argv[1])
  download_dir = sys.argv[2]
  if(download_dir[-1:] != '/'):
    download_dir += '/'

  http = httplib2.Http()
  index = 0

  while(index < len(urls)):
    url = urls[index]
    if(url in visited):
      print('already visited %s\n' % url)
      index += 1
      continue

    if(url[0] == '#'):
      print('skipping %s' % url)
      index += 1
      continue

    print('visiting %s' % url)

    try:
      status, response = http.request(url)
      if(url[-3:] == 'pdf'):
        parsed_url = urllib.parse.urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)
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
        if(l != None and len(l) > 0):
          if('http' not in l):
            l = urllib.parse.urljoin(url, l)
          if(l not in visited and l not in urls):
            n += 1
            urls.append(l)
            textfile.write(l + '\n')
      print(str(n) + ' links found\n' + str(index + 1) + ' visited, ' + str(len(urls) - index - 1) + ' to visit\n')
    except httplib2.RedirectLimit as e:
      print('redirection limit on %s\n' % url)
    except httplib2.ServerNotFoundError as e:
      print('server not found %s\n' % url)
    except Exception as e:
      print('exception: %s' % sys.exc_info()[0])
    index += 1
  textfile.close()

if(__name__ == '__main__'):
    main()
