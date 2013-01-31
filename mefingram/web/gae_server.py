import logging

from google.appengine.ext import db
import webapp2

from mefingram import infodump


logger = logging.getLogger(__name__)


# key_name = mefi|askme|music|meta
class Site(db.Model):
  pass


class NGramCount(db.Model):
  ngram = db.StringProperty()
  year = db.IntegerProperty()
  count = db.IntegerProperty()
  postids = db.StringListProperty()


def init_datastore():
  site_keys = [db.Key.from_path('Site', s) for s in infodump.SITES]
  sites = db.get(site_keys)
  logger.info('Got %s', sites)
  sites = [s for s in sites if s]
  logger.info('keys=%s', [s.key().name() for s in sites])
  needed_site_names = infodump.SITES
  for site in sites:
    needed_site_names.remove(site.key().name())
  logging.info('Creating sites: %s', needed_site_names)
  needed_sites = [Site(key_name=s) for s in needed_site_names]
  db.put(needed_sites)

  parent = Site(key_name='mefi')
  count = NGramCount(
    parent=parent,
    ngram='hello there',
    year=2012,
    count=5,
    postids=['1', '2', '3'])
  count.put()


def make_application():
  init_datastore()
  return  webapp2.WSGIApplication([('/', MainPage)],
                                  debug=True)


class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('Hello, webapp2 World!')
