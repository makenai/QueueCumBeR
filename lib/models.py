from google.appengine.ext import db
from urlparse import urlparse
from cgi import parse_qs
from slugger import get_slug
from exceptions import *
import random

class RegisteredFeed(db.Model):
  id = db.StringProperty(required=True)
  feed_type = db.StringProperty(required=True)
  slug = db.StringProperty()
  rand = db.FloatProperty()
  create_time = db.DateTimeProperty(auto_now_add=True)
  
  def get_url(self):
    return self.key().name()
    
  @classmethod
  def random(self):
    results = RegisteredFeed.gql('WHERE rand > :1 ORDER BY rand LIMIT 1', random.random())
    feeds = results.fetch(1)
    if len( feeds ) == 0:
      return None
    return feeds[0]
        
  @classmethod
  def for_slug(self, slug):
    results = RegisteredFeed.gql('WHERE slug = :1 LIMIT 1', slug)
    feeds = results.fetch(1)
    if len( feeds ) == 0:
      return None
    return feeds[0]
    
  @classmethod
  def for_url(self, url):
    """Find or create the feed record for a feed URL"""
    if url is None or url == '':
      raise BadURLException('Did you forget to provide a feed URL?')
    def txn():
      feed = RegisteredFeed.get_by_key_name(url)
      if feed is None:
        u = urlparse( url )
        q = parse_qs( u.query )
        if u.scheme != 'http' or u.netloc != 'rss.netflix.com' or 'id' not in q:
          raise BadURLException('Invalid Netflix feed URL was provided')
        feed = RegisteredFeed(
          key_name  = url,
          id        = q['id'][0],
          feed_type = u.path,
          rand = random.random()
        )
        feed.put()
      return feed
    feed = db.run_in_transaction(txn)
    if feed.slug is None:
      feed.slug = get_slug()
      feed.put()
    return feed