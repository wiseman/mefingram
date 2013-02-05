mefingram
=========

Mefingram is a Python library for generating n-grams from the
[Metafilter infodump](http://stuff.metafilter.com/infodump/).

Currently it processes post titles only.

To use it, first download the infodump (beware, it is big: about 350
MB):

```
$ curl -O http://mefi.us/infodump/infodump-all.zip
$ unzip infodump-all.zip
```

Then download and build mefingram:

```
$ git clone https://github.com/wiseman/mefingram.git
$ cd mefingram
$ virtualenv env
$ env/bin/pip setup.py develop
```

Now you can generate the n-gram files (this takes about 10 minutes on
my laptop):

```
$ env/bin/python scripts/mfngrams.py --infodump_dir=../infodump-all
```

This creates the following files in the current directory (with their
approximate sizes):

```
ngrams_monthly.tsv  295M
ngrams_yearly.tsv   252M
ngrams_overall.tsv  205M
```

N-gram file format
------------------

The n-gram files contain tab-separated values.

The `overall` file contain n-gram data for the entire history of the
metafilter sub-sites.  Each record has the following fields:

  * n-gram - The actual n-gram
  * site - The name of the sub-site: askme, mefi, meta or music.
  * occurrences - The number of times this n-gram appeared in this year.
  * postids - A comma-delimited list of postids in which this n-gram occurred.

For example:

```
should a doctor be able to\taskme\t1\t35675
should a doctor be able\taskme\t1\t35675
should a doctor be\taskme\t1\t185,11432,35675
```

The `yearly` file contain n-grams grouped by year.  It contains
records with the following fields:

  * n-gram - The actual n-gram
  * site - The name of the sub-site: askme, mefi, meta or music.
  * year - The year in which the n-gram occurred.
  * occurrences - The number of times this n-gram appeared in this year.
  * postids - A comma-delimited list of postids in which this n-gram occurred.

For example:

```
slyt\tmefi\t2008\t3\t71254,75686,76724
slyt\tmefi\t2009\t2\t86791,87482
slyt\tmefi\t2010\t13\t88738,90507,92332,93465,94670,95247,96291,96625,97251,97305,97595,97878,97975
slyt\tmefi\t2011\t15\t99189,99953,100110,100284,101967,103370,106855,106980,107213,109140,109296,110073,110203,110395,111039
slyt\tmefi\t2012\t14\t111175,111811,112509,112714,114503,114588,114605,114752,114806,117570,117998,120616,120656,122077
slyt\tmefi\t2013\t2\t123660,123826
```

The `monthly` files contain n-grams grouped by month.  It's records
have the following fields:

  * n-gram - The actual n-gram
  * site - The name of the sub-site: askme, mefi, meta or music.
  * month - The month in which the n-gram occurred, for example 2013-01.
  * occurrences - The number of times this n-gram appeared in this year.
  * postids - A comma-delimited list of postids in which this n-gram occurred.

For example:

```
slyt\tmefi\t2008-04\t1\t71254
slyt\tmefi\t2008-10\t1\t75686
slyt\tmefi\t2008-11\t1\t76724
slyt\tmefi\t2009-11\t1\t86791
slyt\tmefi\t2009-12\t1\t87482
slyt\tmefi\t2010-01\t1\t88738
slyt\tmefi\t2010-03\t1\t90507
slyt\tmefi\t2010-05\t1\t92332
slyt\tmefi\t2010-07\t1\t93465
slyt\tmefi\t2010-08\t2\t94670,95247
```

Exploration
-----------

To see the 10 most common 6-grams from ask.metafilter.com (the `\t`
values after the `-t` and `-F` options are literal tab characters
inside single quotes--you can insert a literal tab by pressing CTRL-V
then TAB):

```
$ cat ngram_overall.tsv |
  grep '.* .* .* .* .* ' | grep '\taskme' |
  sort -t '\t' -k2n |
  tail -10 |
  awk -F '\t' '{print $1, $3;}' |
  tac

what is the best way to 113
what do i need to know 88
should i stay or should i 82
i stay or should i go 80
how do i get rid of 79
what is the name of this 69
i do not want to be 63
is there such a thing as 48
what should i do with my 45
i do not know how to 34
```


Running the web server
----------------------

The easiest way to run the n-gram viewer is this:

```
$ env/bin/python -m mefingram.web.server --ngram_dir=../infodump-all
 * Running on http://127.0.0.1:5000/
```

Then point your browser at
[http://127.0.0.1:5000/](http://127.0.0.1:5000/).


mefingram.appspot.com on Google App Engine
------------------------------------------

To upload n-gram data to Google App Engine:

```
# N-gram data:
$ appcfg.py --oauth2 upload_data \
  --config_file=bulkloader_custom.yaml \
  --url=http://mefingram.appspot.com/_ah/remote_api \
  --kind=NGramCount \
  --filename=ngrams_yearly.txt \
  --batch_size=20 \
  --rps_limit=15000 \
  --num_threads=200 \
  --http_limit=400 \
  --rps_limit=1000 \
  --bandwidth_limit=304800

# N-gram total data, for scaling:
$ appcfg.py --oauth2 upload_data \
  --config_file=bulkloader_ngramcounttotal.yaml \
  --url=http://mefingram.appspot.com/_ah/remote_api \
  --kind=NGramCountTotal \
  --filename=ngrams_yearly_total.tsv \
  --batch_size=20 \
  --rps_limit=15000 \
  --num_threads=1 \
  --http_limit=400 \
  --rps_limit=1000  \
  --bandwidth_limit=304800

# Post titles for links:
$ appcfg.py --oauth2 upload_data \
  --config_file=bulkloader_post.yaml \
  --url=http://mefingram.appspot.com/_ah/remote_api \
  --kind=NGramCount --filename=posts.tsv \
  --batch_size=20 \
  --rps_limit=15000 \
  --num_threads=1 \
  --http_limit=400 \
  --rps_limit=1000  \
  --bandwidth_limit=304800
```

Beware, the full n-gram data can take a couple hours to upload and
cost $50 in datastore writes.

The development server can't handle all the data.  Try generating data
for just music, which will still bog the server down pretty badly:

```
$ env/bin/python scripts/mfngrams.py --sites=music --infodump_dir=../infodump-all
```
