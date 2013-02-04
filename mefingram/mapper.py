import codecs
import csv
import itertools
import logging
import StringIO
import sys

from mrjob import job

from mefingram import infodump
from mefingram import text


logger = logging.getLogger(__name__)

# The default field size limit is 131072 bytes.  We need more.
csv.field_size_limit(1000000000)


MAX_N = 6


class Error(Exception):
  pass


class UTF8Recoder:
  """Iterator that reads an encoded stream and reencodes the input
  to UTF-8.
  """
  def __init__(self, f, encoding):
    self.reader = codecs.getreader(encoding)(f)

  def __iter__(self):
    return self

  def next(self):
    return self.reader.next().encode("utf-8")


class UnicodeCSVReader:
  """A CSV reader which will iterate over lines in the CSV file "f",
  which is encoded in the given encoding.
  """
  def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
    f = UTF8Recoder(f, encoding)
    self.reader = csv.reader(f, dialect=dialect, **kwds)

  def next(self):
    row = self.reader.next()
    return [unicode(s, "utf-8") for s in row]

  def __iter__(self):
    return self


class UnicodeCSVWriter:
  """A CSV writer which will write rows to CSV file "f", which is
  encoded in the given encoding.
  """
  def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
    # Redirect output to a queue
    self.queue = StringIO.StringIO()
    self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
    self.stream = f
    self.encoder = codecs.getincrementalencoder(encoding)()

  def writerow(self, row):
    self.writer.writerow([s.encode("utf-8") for s in row])
    # Fetch UTF-8 output from the queue ...
    data = self.queue.getvalue()
    data = data.decode("utf-8")
    # ... and reencode it into the target encoding
    data = self.encoder.encode(data)
    # write to the target stream
    self.stream.write(data)
    # empty queue
    self.queue.truncate(0)

  def writerows(self, rows):
    for row in rows:
      self.writerow(row)


def join_posts(data_file, title_file, joined_file, site=None):
  tsv_writer = UnicodeCSVWriter(joined_file, dialect='excel-tab')
  posts = infodump.read_posts(data_file, title_file)
  for post in posts:
    if site:
      fields = [site, post.postid, infodump.datestamp_str(post.datestamp),
                post.title]
    else:
      fields = [post.postid, infodump.datestamp_str(post.datestamp),
                post.title]
    tsv_writer.writerow(fields)


class NGramProtocol(object):
  def read(self, unused_line):
    raise Error('%s does not support reading' % (self,))


class NGramByDateProtocol(NGramProtocol):
  def write(self, key, value):
    ngram, site, date = key
    count, postids = value
    result = u'%s\t%s\t%s\t%s\t%s' % (
      ngram,
      site,
      date,
      count,
      u','.join(map(unicode, postids)))
    return result.encode('utf8')


class NGramOverallProtocol(NGramProtocol):
  def write(self, key, value):
    ngram, site = key
    count, postids = value
    result = u'%s\t%s\t%s\t%s' % (
      ngram,
      site,
      count,
      u','.join(map(unicode, postids)))
    return result.encode('utf8')


class NGramCounter(job.MRJob):
  def __init__(self, *args, **kw_args):
    job.MRJob.__init__(self, *args, **kw_args)

  def parse_infodump(self, unsued_key, unused_value):
    raise NotImplementedError()

  def parse_line(self, line):
    tsv_reader = UnicodeCSVReader(StringIO.StringIO(line), dialect='excel-tab')
    fields = tsv_reader.next()
    return fields

  def ngrams_for_text(self, s, n):
    tokens = text.title_tokens(s)
    return text.ngrams_for_tokens(tokens, n)

  def sum_counts(self, key, values):
    counts, postids = itertools.izip(*values)
    postids = sorted(list(set(postids)))
    yield key, (sum(counts), postids)

  def steps(self):
    return [self.mr(self.parse_infodump, self.sum_counts),]


def calculate_ngram_counts(ngram_file, output_file, with_date=False):
  counter = {}
  reader = UnicodeCSVReader(ngram_file, dialect='excel-tab')
  for row in reader:
    if with_date:
      ngram, site, date, count, postids = row
      ngram_n = len(ngram.split())
      key = '%s\t%s\t%s' % (ngram_n, site, date)
      counter[key] = counter.get(key, 0) + int(count)
    else:
      ngram, site, count, postids = row
      ngram_n = len(ngram.split())
      key = '%s\t%s' % (ngram_n, site)
      counter[key] = counter.get(key, 0) + int(count)
  for key in sorted(counter.keys()):
    output_file.write('%s\t%s\n' % (key, counter[key]))
