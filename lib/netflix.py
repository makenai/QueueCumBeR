from google.appengine.api import urlfetch
from google.appengine.api import memcache
from BeautifulSoup import BeautifulSoup
from exceptions import *
import feedparser
import re

CACHE_NAMESPACE = 'Feeds'
CACHE_TIME      = 5 * 60

def parse_item( item ):

  # First, try to get the position and title
  pattern = re.compile(r"^(\d+)\s*-\s*(.*)$")
  m = pattern.match( item.title )
  if m:
    position = int( m.group(1) )
    title = m.group(2)
  else:
    position = None
    title = item.title
    
  # Then, split image and description parts
  soup = BeautifulSoup( item.description )
  image = soup.findAll('img')[0]['src']
  description = ' '.join( soup.findAll(text=True) )
  
  item = {
    'position': position,
    'title': title,
    'image': image,
    'link': item.link,
    'description': description,
  }
  return item

def get_feed( feed_url ):
  
  xml = memcache.get( feed_url, namespace=CACHE_NAMESPACE )
  if xml is None:
    result = urlfetch.fetch( feed_url )
    if result.status_code != 200:
      raise NetworkError('There was an error fetching the feed. Please check the URL and try again.')  
    xml = result.content
    memcache.set( feed_url, xml, namespace=CACHE_NAMESPACE, time=CACHE_TIME )
  
  feed = feedparser.parse( xml )
  if feed.bozo == 1:
    raise ParseError('There was a problem parsing the feed. Sorry, please try again later.')
  items = []
  
  data = {
    'title': feed.channel.title,
    'description': feed.channel.description,
    'items': [ parse_item( item ) for item in feed.entries ]
  }
  return data