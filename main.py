from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from lib.netflix import get_feed
from lib.models import *

class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write( template.render('templates/main.html', {}) )
        
class RegisterHandler(webapp.RequestHandler):
  def post(self):
      try:
        feed_url = self.request.get('feed_url')
        feed = RegisteredFeed.for_url( feed_url )
        self.redirect("/" + feed.slug)
      except Exception, reason:
        self.response.out.write( template.render('templates/error.html', { 'reason': reason }) )

class RandomHandler(webapp.RequestHandler):
  def get(self):
      feed = RegisteredFeed.random()
      if feed is None:
        self.redirect("/")
      else:
        self.redirect("/" + feed.slug)

class PageHandler(webapp.RequestHandler):
  def get(self,page):
    self.response.out.write( template.render('templates/' + page + '.html', {}) )
          
class DisplayHandler(webapp.RequestHandler):
  def get(self,slug):
    feed = RegisteredFeed.for_slug( slug )
    if feed is None:
      data = {
        'slug': slug
      }
      self.response.out.write( template.render('templates/not_found.html', data ) )
    else:
      try:
        data = get_feed( feed.get_url() )
        data.update({
          'created_at': feed.create_time,
          'slug':       slug
        })
        self.response.out.write( template.render('templates/list.html', data) )
      except Exception, reason:
        self.response.out.write( template.render('templates/error.html', { 'reason': reason }) )
      
def main():
    application = webapp.WSGIApplication([
      ('/', MainHandler),
      ('/register', RegisterHandler),
      ('/random', RandomHandler),      
      ('/(about|help)', PageHandler),
      ('/(.*)', DisplayHandler)
    ], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()