import itertools
import logging
import os.path
import re
import sys

import gflags
import flask

from mefingram import text


logger = logging.getLogger(__name__)

FLAGS = gflags.FLAGS

app = flask.Flask(__name__)

THIS_DIR = os.path.dirname(__file__)


gflags.DEFINE_string(
  'ngram_dir', '.',
  'The directory containing the ngram files.')


@app.route('/script/<path:filename>')
def send_script(filename):
  return flask.send_from_directory(os.path.join(THIS_DIR, 'static'), filename)


DEFAULT_CONTENT = 'I for one, what it says on the tin, think of the children'
DEFAULT_CORPUS = 'mefi'

YEARS = range(1999, 2014)


def get_year_counts_for_phrase(corpus, phrase):
  phrase = phrase.lower()
  phrase = text.rewrite(phrase)
  tokens = text.tokenize(phrase)
  query = ' '.join(tokens)
  regex = '%s\t%s\t([0-9]+)\t([0-9]+)\t(.*)' % (query, corpus)
  regex = re.compile(regex)
  ngram_path = os.path.join(FLAGS.ngram_dir, 'ngrams_yearly.txt')
  counts = {}
  with open(ngram_path, 'rb') as ngrams:
    for line in ngrams:
      match = regex.match(line)
      if match:
        year = int(match.group(1))
        count = int(match.group(2))
        counts[year] = count
  return counts


@app.route('/')
def index():
  content = unicode(flask.request.args.get('content') or DEFAULT_CONTENT)
  corpus = flask.request.args.get('corpus') or DEFAULT_CORPUS
  content_phrases = content.split(',')

  results = []
  for phrase in content_phrases:
    phrase_counts = get_year_counts_for_phrase(corpus, phrase)
    phrase_results = []
    for year in YEARS:
      phrase_results.append(phrase_counts.get(year, 0))
    results.append(phrase_results)
  final_results = list(itertools.izip(YEARS, *results))

  return flask.render_template(
    'index.tmpl',
    content=content,
    corpus=corpus,
    content_phrases=content_phrases,
    results=final_results)


def main():
  unused_argv = FLAGS(sys.argv)
  app.debug = True
  app.run()


if __name__ == '__main__':
  main()
