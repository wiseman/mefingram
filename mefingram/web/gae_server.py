import itertools
import json
import logging
import os

import jinja2
from google.appengine.api import memcache
from google.appengine.ext import db
import webapp2

from mefingram import infodump
from mefingram import text


logger = logging.getLogger(__name__)
jinja = jinja2.Environment(
  loader=jinja2.FileSystemLoader(os.path.join(
      os.path.dirname(__file__), 'templates')))


def to_json_filter(v):
  return json.dumps(v)

jinja.filters['tojson'] = to_json_filter


DEFAULT_CONTENT = u'I for one welcome, what it says on the tin, slyt'
DEFAULT_CORPUS = u'mefi'

YEARS = range(1999, 2014)


class NGramCount(db.Model):
  ngram = db.StringProperty()
  site = db.StringProperty()
  year = db.IntegerProperty()
  count = db.IntegerProperty()
  postids = db.StringListProperty()


class NGramCountTotal(db.Model):
  n = db.IntegerProperty()
  site = db.StringProperty()
  year = db.IntegerProperty()
  count = db.IntegerProperty()


class Post(db.Model):
  site = db.StringProperty()
  postid = db.StringProperty()
  datestamp = db.StringProperty()
  # There are a few posts with titles that are longer than the 500
  # character limit for StringProperty.
  title = db.TextProperty()


def get_ngram_total_for_year(n, site, year):
  key = 'ngram_total'
  cache =  memcache.get(key)
  if not cache:
    cache = {}
    logger.info('Building ngram total cache')
    query = NGramCountTotal.all()
    for result in query.run(batch_size=10000):
      result_key = '%s-%s-%s' % (result.n, result.site, result.year)
      cache[result_key] = result.count
    memcache.set(key, cache, 60)
  item_key = '%s-%s-%s' % (n, site, year)
  total = cache[item_key]
  return total


def get_year_counts_for_phrases(corpus, phrases):
  # Counts is a map from [phrase][year] -> (count, postids)
  counts = {}
  tokenized_to_phrases = {}
  for phrase in phrases:
    cooked_phrase = phrase.lower()
    cooked_phrase = text.rewrite(cooked_phrase)
    tokens = text.tokenize(cooked_phrase)
    token_str = ' '.join(tokens)
    tokenized_to_phrases[token_str] = phrase
  for phrase in phrases:
    counts[phrase] = {}
  query = NGramCount.all()
  query.filter('site =', corpus)
  query.filter('ngram IN', tokenized_to_phrases.keys())
  for result in query.run(batch_size=10000):
    total = get_ngram_total_for_year(
      len(result.ngram.split()),
      corpus,
      result.year)
    counts[tokenized_to_phrases[result.ngram]][result.year] = (
      float(result.count) / total, result.postids)
  return counts


def transform_results(phrases, results):
  xformed_results = []
  for phrase in phrases:
    phrase_results = []
    for year in YEARS:
      phrase_results.append(results[phrase].get(year, 0))
    xformed_results.append(phrase_results)
  return list(itertools.izip(YEARS, *xformed_results))


class MainPage(webapp2.RequestHandler):
  def get(self):
    content = self.request.get('content') or DEFAULT_CONTENT
    corpus = self.request.get('corpus') or DEFAULT_CORPUS
    content_phrases = content.split(',')
    results = get_year_counts_for_phrases(corpus, content_phrases)
    template = jinja.get_template('index.tmpl')
    template_values = dict(
      content=content,
      corpus=corpus,
      content_phrases=content_phrases,
      results=results)
    self.response.out.write(template.render(template_values))


class PostRequester(webapp2.RequestHandler):
  def get(self):
    corpus = self.request.get('corpus')
    postids = self.request.get('postids')
    postid_list = postids.split(',')
    postid_list = postid_list[:30]
    query = Post.all()
    query.filter('site =', corpus)
    query.filter('postid IN', postid_list)
    results = []
    for post in query.run(batch_size=10000):
      result = (post.postid, post.datestamp, post.title)
      results.append(result)
    self.response.write(json.dumps(results))


ROUTES = [
  ('/', MainPage),
  ('/post', PostRequester)]


def make_application():
  #init_datastore()
  return  webapp2.WSGIApplication(
    ROUTES,
    debug=True)
