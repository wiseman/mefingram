# -*- coding: utf-8 -*-
import unittest

from mefingram import text


class TestText(unittest.TestCase):
  def test_is_letter_or_number(self):
    self.assertTrue(text.is_letter_or_number(u'a'))
    self.assertTrue(text.is_letter_or_number(u'1'))
    self.assertTrue(text.is_letter_or_number(u'Ü'))
    self.assertFalse(text.is_letter_or_number(u'?'))
    self.assertFalse(text.is_letter_or_number(u'.'))
    self.assertFalse(text.is_letter_or_number(u'-'))
    self.assertFalse(text.is_letter_or_number(u'¶'))
    self.assertRaises(TypeError, text.is_letter_or_number, 'a')

  def test_rewrite(self):
    self.assertEqual(text.rewrite("isn't it"), 'is not it')
    self.assertEqual(text.rewrite("isn't it"), 'is not it')
    self.assertEqual(text.rewrite("john's"), 'john')
    self.assertEqual(text.rewrite("'s's's's"), '')

  def test_tokenize(self):
    self.assertEqual(text.tokenize(u'one'), ['one'])
    self.assertEqual(text.tokenize(u'one two'), ['one', 'two'])
    self.assertEqual(text.tokenize(u'one  two'), ['one', 'two'])
    self.assertEqual(text.tokenize(u'    one  two  '), ['one', 'two'])
    self.assertEqual(text.tokenize(u'one.two'), ['one', 'two'])
    self.assertEqual(text.tokenize(u'one...two'), ['one', 'two'])
    self.assertEqual(text.tokenize(u'..one...two'), ['one', 'two'])
    self.assertRaises(TypeError, text.tokenize, 'one two')

  def test_html_unescape(self):
    self.assertEqual(text.html_unescape('umlaut'), 'umlaut')
    self.assertEqual(text.html_unescape('&Uuml;'), u'Ü')
    self.assertEqual(text.html_unescape('&#220;'), u'Ü')

  def test_ngrams_for_tokens(self):
    self.assertEqual(text.ngrams_for_tokens(['one', 'two', 'three'], 1),
                     [('one',), ('two',), ('three',)])
    self.assertEqual(text.ngrams_for_tokens(['one', 'two', 'three'], 2),
                     [('one', 'two'), ('two', 'three')])
    self.assertEqual(text.ngrams_for_tokens(['one', 'two', 'three'], 3),
                     [('one', 'two', 'three')])

  def test_title_tokens(self):
    self.assertEqual(text.title_tokens("Strap on your Zyklon B's."),
                     ['strap', 'on', 'your', 'zyklon', 'b'])
