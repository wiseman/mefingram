import codecs
import logging
import os
import sys
import tempfile

import gflags

from mefingram import infodump
from mefingram import mapper
from mefingram import mfngrams_overall
from mefingram import mfngrams_monthly
from mefingram import mfngrams_yearly

logger = logging.getLogger(__name__)

LOGGING_FORMAT = '%(asctime)s:%(levelname)s: %(message)s'

FLAGS = gflags.FLAGS

gflags.DEFINE_string(
  'infodump_dir', '.',
  'The directory containing the infodump files.')

gflags.DEFINE_string(
  'sites', ','.join(map(str, infodump.SITES)),
  'A comma-delimited list of the sites to process.')

gflags.DEFINE_list(
  'aggregate', ['overall', 'yearly', 'monthly'],
  'Aggregate groups')


def generate_ngrams_for_sites(sites):
  joined_posts_path = 'posts.tsv'
  with open(joined_posts_path, 'wb') as joined_file:
    for site in sites:
      logger.info('Joining post data for %s...', site)
      data_path = os.path.join(FLAGS.infodump_dir, 'postdata_%s.txt' % (site,))
      title_path = os.path.join(
        FLAGS.infodump_dir, 'posttitles_%s.txt' % (site,))
      with open(data_path, 'rb') as data_file:
        with open(title_path, 'rb') as title_file:
          mapper.join_posts(data_file, title_file, joined_file, site=site)
  # Write n-gram files
  if 'overall' in FLAGS.aggregate:
    logger.info('Generating overall ngrams for %s...', sites)
    output_path = 'ngrams_overall.tsv'
    run_counter(
      mfngrams_overall.NGramOverallCounter, joined_posts_path, output_path)
  if 'yearly' in FLAGS.aggregate:
    logger.info('Generating yearly ngrams for %s...', sites)
    output_path = 'ngrams_yearly.tsv'
    run_counter(
      mfngrams_yearly.NGramYearlyCounter, joined_posts_path, output_path)
  if 'monthly' in FLAGS.aggregate:
    logger.info('Generating monthly ngrams for %s...', sites)
    output_path = 'ngrams_monthly.tsv'
    run_counter(
      mfngrams_monthly.NGramMonthlyCounter, joined_posts_path, output_path)


def run_counter(klass, input_path, output_path):
  args = [
    '--jobconf', 'mapreduce.job.maps=6',
    '--jobconf', 'mapreduce.job.reduces=6',
    input_path
    ]
  counter = klass(args=args)
  with counter.make_runner() as runner:
    logger.info('Running mrjob with args %s' % (args,))
    runner.run()
    logger.info('Writing results to %s...', output_path)
    with open(output_path, 'wb') as output_file:
      for line in runner.stream_output():
        output_file.write('%s' % (line,))


def main():
  unused_argv = FLAGS(sys.argv)
  logging.basicConfig(
    level=logging.INFO,
    format=LOGGING_FORMAT)
  sites = FLAGS.sites.split(',')
  generate_ngrams_for_sites(sites)


if __name__ == '__main__':
  sys.exit(main())
