from bs4 import BeautifulSoup, SoupStrainer
import sys

print(sys.argv[1])

with open(sys.argv[1], 'r') as f:
  for link in BeautifulSoup(f.read(), parse_only=SoupStrainer('a')):
    if link.has_attr('href'):
      print(link.string + ': ' + link['href'])
