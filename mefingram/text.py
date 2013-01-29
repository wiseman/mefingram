import unicodedata

import nltk
from nltk import data as nltk_data
from nltk import util as nltk_util


def is_letter_or_number(c):
  category = unicodedata.category(c)
  return category[0] == 'L' or category[0] == 'N'


REWRITE_RULES = {
  "haven't": 'have not',
  "couldn't": 'could not',
  "what's": 'what is',
  "i'm": 'i am ',
  "can't": 'can not',
  "don't": 'do not',
  "won't": 'will not',
  "they'll": 'they will',
  "i'll": 'i will',
  "isn't": 'is not',
  "you'll": 'you will',
  "you're": 'you are',
  "we're": 'we are',
  "'s": '',
  }


def rewrite(s):
  for k in REWRITE_RULES:
    s = s.replace(k, REWRITE_RULES[k])
  return s


def tokenize(string):
  string = rewrite(string.lower())
  tokens = nltk.tokenize.wordpunct_tokenize(string)
  tokens = [t for t in tokens if is_letter_or_number(t[0])]
  return tokens


def ngrams_for_text(text, n):
  tokens = tokenize(text)
  ngrams = []
  if tokens:
    ngrams = nltk_util.ngrams(tokens, n)
  return ngrams
