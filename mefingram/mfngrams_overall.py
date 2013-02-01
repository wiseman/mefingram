from mefingram import mapper


class NGramOverallCounter(mapper.NGramCounter):
  OUTPUT_PROTOCOL = mapper.NGramOverallProtocol

  def __init__(self, *args, **kw_args):
    mapper.NGramCounter.__init__(self, *args, **kw_args)

  def parse_infodump(self, unused_key, line):
    line = unicode(line, 'utf8')
    site, postid_str, unused_datestamp_str, title = line.split('\t')
    postid = int(postid_str)
    for i in range(mapper.MAX_N):
      n = i + 1
      ngrams = self.ngrams_for_text(title, n)
      for ngram in ngrams:
        ngram_str = ' '.join(ngram)
        key = (ngram_str, site)
        value = (1, postid)
        yield (key, value)


if __name__ == '__main__':
  NGramOverallCounter.run()
