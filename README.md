mefingram
=========

Mefingram is a Python library for generating n-grams from the
[Metafilter infodump](http://stuff.metafilter.com/infodump/).

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

This creates the following files (with their approximate sizes):

```
ngram_askme_monthly.txt  176M 
ngram_askme_overall.txt  122M 
ngram_askme_yearly.txt   150M 
ngram_mefi_monthly.txt    67M 
ngram_mefi_overall.txt    46M 
ngram_mefi_yearly.txt     58M 
ngram_meta_monthly.txt    10M 
ngram_meta_overall.txt     7M 
ngram_meta_yearly.txt      8M 
ngram_music_monthly.txt    2M 
ngram_music_overall.txt    1M 
ngram_music_yearly.txt     1M  
```

N-gram file format
------------------

The n-gram files contain tab-separated values.

The `overall` files contain n-gram data for the entire history of the
site, including counts and a list of comma-separated post IDs.  For
example:

```
should a doctor be able to	1	35675
should a doctor be able	1	35675
should a doctor be	1	185,11432,35675
```

The `yearly` files contain n-grams grouped by year:

```
slyt	2008	3	71254,75686,76724
slyt	2009	2	86791,87482
slyt	2010	13	88738,90507,92332,93465,94670,95247,96291,96625,97251,97305,97595,97878,97975
slyt	2011	15	99189,99953,100110,100284,101967,103370,106855,106980,107213,109140,109296,110073,110203,110395,111039
slyt	2012	14	111175,111811,112509,112714,114503,114588,114605,114752,114806,117570,117998,120616,120656,122077
slyt	2013	2	123660,123826
```

The `monthly` files contain n-grams grouped by month:

```
slyt	2008-04	1	71254
slyt	2008-10	1	75686
slyt	2008-11	1	76724
slyt	2009-11	1	86791
slyt	2009-12	1	87482
slyt	2010-01	1	88738
slyt	2010-03	1	90507
slyt	2010-05	1	92332
slyt	2010-07	1	93465
slyt	2010-08	2	94670,95247
```

Exploration
-----------

To see the 10 most common 6-grams from ask.metafilter.com (the values
after the `-t` and `-F` options are literal tab characters that you
can insert in bash by pressing CTRL-V then TAB):

```
$ cat ~/data/ngram_askme_overall.txt |
  grep '.* .* .* .* .* ' |
  sort -t '	' -k2n |
  tail -10 |
  awk -F '	' '{print $1, $2;}' |
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
