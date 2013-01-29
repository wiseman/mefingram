import itertools

from mrjob import job

from mefingram import infodump


MAX_N = 6


class Error(Exception):
  pass


def join_posts(data_file, title_file, joined_file):
  posts = infodump.read_posts(data_file, title_file)
  for post in posts:
    joined_file.write(u'%s\t%s\t%s\n' % (
        post.postid, infodump.datestamp_str(post.datestamp), post.title))


class NGramProtocol(object):
  def read(self, unused_line):
    raise Error('%s does not support reading' % (self,))


class NGramByDateProtocol(NGramProtocol):
  def write(self, key, value):
    ngram, date = key
    count, postids = value
    result = u'%s\t%s\t%s\t%s' % (
      ngram,
      date,
      count,
      u','.join(map(unicode, postids)))
    return result.encode('utf8')


class NGramOverallProtocol(NGramProtocol):
  def write(self, ngram, value):
    count, postids = value
    result = u'%s\t%s\t%s' % (
      ngram,
      count,
      u','.join(map(unicode, postids)))
    return result.encode('utf8')


class NGramCounter(job.MRJob):
  def __init__(self, *args, **kw_args):
    job.MRJob.__init__(self, *args, **kw_args)

  def parse_infodump(self, unsued_key, unused_value):
    raise NotImplementedError()

  def sum_counts(self, key, values):
    counts, postids = itertools.izip(*values)
    postids = sorted(list(set(postids)))
    yield key, (sum(counts), postids)

  def steps(self):
    return [self.mr(self.parse_infodump, self.sum_counts),]
