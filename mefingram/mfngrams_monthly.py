from mefingram import infodump
from mefingram import mapper


class NGramMonthlyCounter(mapper.NGramCounter):
  OUTPUT_PROTOCOL = mapper.NGramByDateProtocol

  def __init__(self, *args, **kw_args):
    mapper.NGramCounter.__init__(self, *args, **kw_args)

  def parse_infodump(self, unused_key, line):
    site, postid_str, datestamp_str, title = self.parse_line(line)
    datestamp = infodump.parse_datestamp(datestamp_str)
    postid = int(postid_str)
    for i in range(mapper.MAX_N):
      n = i + 1
      ngrams = self.ngrams_for_text(title, n)
      for ngram in ngrams:
        ngram_str = ' '.join(ngram)
        key = (ngram_str, site, '%s-%02d' % (datestamp.year, datestamp.month))
        value = (1, postid)
        yield (key, value)


if __name__ == '__main__':
  NGramMonthlyCounter.run()
