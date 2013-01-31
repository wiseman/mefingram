import csv
import datetime
import logging

from mefingram import text


logger = logging.getLogger(__name__)


SITES = ['askme', 'mefi', 'meta', 'music']

DATESTAMP_FORMAT = u'%Y-%m-%d %H:%M:%S.%f'


class Error(Exception):
  pass


class Post(object):
  def __init__(self, postid=None, userid=None, datestamp=None, title=None):
    self.postid = postid
    self.userid = userid
    self.datestamp = datestamp
    self.title = title


def infodump_csv_reader(stream):
  return csv.reader(stream, delimiter='\t', quoting=csv.QUOTE_NONE)


def parse_datestamp(datestamp):
  return datetime.datetime.strptime(datestamp, DATESTAMP_FORMAT)


def datestamp_str(datestamp):
  return datestamp.strftime(DATESTAMP_FORMAT)


def read_posts(data_file, title_file):
  posts = []
  titles = {}

  # Read the title file.
  # Skip the first line, the timestamp.
  title_file.readline()
  # Skip the second line, the column titles.
  title_file.readline()
  csv_reader = infodump_csv_reader(title_file)
  bad_utf8_postids = []
  for record_num, row in enumerate(csv_reader):
    # If we can't even parse the postid, die.
    postid = unicode(row[0], 'utf8')
    try:
      title = unicode(row[1], 'utf8')
      titles[postid] = title
    except UnicodeDecodeError, e:
      logger.debug(
        '%s:%s Skipping line due to %s: %r',
        title_file.name, record_num + 2, e, row)
      bad_utf8_postids.append(postid)
  if bad_utf8_postids:
    logger.warn(
      'Skipped %s posts due to UTF8 errors.', len(bad_utf8_postids))

  # Read the data file.
  # Skip the first line, the timestamp.
  data_file.readline()
  # Skip the second line, the column titles.
  data_file.readline()
  csv_reader = infodump_csv_reader(data_file)
  for record_number, row in enumerate(csv_reader):
    if len(row) != 8:
      logging.warn(
        '%s:%s Unable to parse line, skipping: %r',
        data_file.name, record_number + 2, row)
    else:
      postid = unicode(row[0], 'utf8')
      userid = unicode(row[1], 'utf8')
      datestamp = parse_datestamp(row[2])
      if postid in titles:
        post = Post(
          postid=postid, userid=userid, datestamp=datestamp,
          title=titles[postid])
        posts.append(post)
      else:
        logger.debug(
          'postid %s exists in %s but not in %s' % (
            postid, data_file, title_file))
        if not postid in bad_utf8_postids:
          logger.warn(
            '%s:%s Skipping postid %s because it does not exist in title file',
            data_file.name, record_number + 2, postid)
  return posts


def make_ngram_model(n, posts):
  words = []
  for post in posts:
    words += text.tokenize(post.title)
  return ngram.NgramModel(n, words)
