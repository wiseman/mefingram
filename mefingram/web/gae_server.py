import itertools
import json
import logging
import os

import jinja2
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


DEFAULT_CONTENT = u'I for one, what it says on the tin, think of the children'
DEFAULT_CORPUS = u'mefi'

YEARS = range(1999, 2014)


class NGramCount(db.Model):
  ngram = db.StringProperty()
  site = db.StringProperty()
  year = db.IntegerProperty()
  count = db.IntegerProperty()
  postids = db.StringListProperty()


def make_application():
  #init_datastore()
  return  webapp2.WSGIApplication([('/', MainPage)],
                                  debug=True)


def get_year_counts_for_phrases(corpus, phrases):
  # Counts is a map from [phrase][year] -> count
  counts = {}
  tokenized_to_phrases = {}
  for phrase in phrases:
    tokens = text.tokenize(phrase)
    token_str = ' '.join(tokens)
    tokenized_to_phrases[token_str] = phrase
  for phrase in phrases:
    counts[phrase] = {}
  query = NGramCount.all()
  query.filter('site =', corpus)
  query.filter('ngram IN', tokenized_to_phrases.keys())
  for result in query.run(batch_size=10000):
    counts[tokenized_to_phrases[result.ngram]][result.year] = result.count
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
    final_results = transform_results(content_phrases, results)
    template = jinja.get_template('index.tmpl')
    template_values = dict(
      content=content,
      corpus=corpus,
      content_phrases=content_phrases,
      results=final_results)
    self.response.out.write(template.render(template_values))
