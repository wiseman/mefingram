from mefingram import infodump
from mefingram import mapper
from mefingram import text


class NGramYearlyCounter(mapper.NGramCounter):
  OUTPUT_PROTOCOL = mapper.NGramByDateProtocol

  def __init__(self, *args, **kw_args):
    mapper.NGramCounter.__init__(self, *args, **kw_args)

  def parse_infodump(self, unused_key, line):
    line = unicode(line, 'utf8')
    site, postid_str, datestamp_str, title = line.split('\t')
    datestamp = infodump.parse_datestamp(datestamp_str)
    postid = int(postid_str)
    for i in range(mapper.MAX_N):
      n = i + 1
      ngrams = text.ngrams_for_text(title, n)
      for ngram in ngrams:
        ngram_str = ' '.join(ngram)
        key = (ngram_str, site, datestamp.year)
        value = (1, postid)
        yield (key, value)


if __name__ == '__main__':
  NGramYearlyCounter.run()
