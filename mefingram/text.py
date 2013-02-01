import htmlentitydefs
import re
import unicodedata


try:
  import nltk
  from nltk import data as nltk_data
  from nltk import util as nltk_util
except ImportError:
  pass


def is_letter_or_number(c):
  """Checks whether a unicode character is a letter or number."""
  category = unicodedata.category(c)
  return category[0] == 'L' or category[0] == 'N'


REWRITE_RULES = {
  u"haven't": u'have not',
  u"couldn't": u'could not',
  u"what's": u'what is',
  u"i'm": u'i am ',
  u"can't": u'can not',
  u"don't": u'do not',
  u"won't": u'will not',
  u"they'll": u'they will',
  u"i'll": u'i will',
  u"isn't": u'is not',
  u"you'll": u'you will',
  u"you're": u'you are',
  u"we're": 'uwe are',
  u"'s": u'',
  }


def rewrite(s):
  """Expands contractions and removes possessives.  Very simpleminded."""
  for k in REWRITE_RULES:
    s = s.replace(k, REWRITE_RULES[k])
  return s


WORDPUNCT_RE = re.compile(
  r'\w+|[^\w\s]+', re.UNICODE | re.MULTILINE | re.DOTALL)


def tokenize(string):
  """Tokenzies a string.

  Splits on punctuation and removes tokens that are entirely
  punctuation.
  """
  tokens = WORDPUNCT_RE.findall(string)
  tokens = [t for t in tokens if is_letter_or_number(t[0])]
  return tokens


# From http://effbot.org/zone/re-sub.htm#unescape-html
def html_unescape(text):
  """Removes HTML or XML character references and entities from a text
  string.

  @param text The HTML (or XML) source text.
  @return The plain text, as a Unicode string, if necessary.
  """
  def fixup(m):
    text = m.group(0)
    if text[:2] == u"&#":
      # character reference
      try:
        if text[:3] == u"&#x":
          return unichr(int(text[3:-1], 16))
        else:
          return unichr(int(text[2:-1]))
      except ValueError:
        pass
    else:
      # named entity
      try:
        text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
      except KeyError:
        pass
      return text  # leave as is
  return re.sub("&#?\w+;", fixup, text)


def title_tokens(title):
  title = html_unescape(title)
  title = title.lower()
  title = rewrite(title)
  tokens = tokenize(title)
  return tokens


def ngrams_for_tokens(tokens, n):
  return nltk_util.ngrams(tokens, n)
