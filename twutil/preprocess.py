from collections import defaultdict
import json
import re
import string


punc_re = '[' + re.escape(string.punctuation) + ']'


class Tokenizer(object):
    """
    >>> t = Tokenizer()
    >>> t.tokenize(Tweet(json.loads(data.test_tweet)))
    {'text': [u'if', u'only', u"bradley's", u'arm', u'was', u'longer', u'.', u'best', u'photo', u'ever', u'.', u'HASHTAG_oscars', u'THIS_IS_A_URL'], 'user.name': [u'ellen', u'degeneres']}
    """
    def __init__(self, fields=['text', 'user.name'], ngrams=1, lc=True, collapse_hashtags=False,
                 collapse_mentions=True, collapse_urls=True, limit_repeats=True, retain_punc_toks=True,
                 collapse_digits=False, rt_prefix=False):
        self.ngrams = ngrams
        if ngrams > 1:
            raise NotImplementedError('ngrams > 1 not yet implemented')
        self.fields = fields
        self.lc = lc
        self.collapse_hashtags = collapse_hashtags
        self.collapse_mentions = collapse_mentions
        self.collapse_urls = collapse_urls
        self.limit_repeats = True
        self.retain_punc_toks = retain_punc_toks
        self.collapse_digits = collapse_digits
        self.rt_prefix = rt_prefix

    def do_tokenize(self, text):
        """
        >>> tk = Tokenizer(ngrams=1, lc=True, collapse_urls=True, collapse_mentions=True, collapse_hashtags=False, retain_punc_toks=True)
        >>> tk.do_tokenize('http://www.foo.com fast-forward hi there :) how?? U.S.A. @you whaaaaaaat? #awesome.')
        ['THIS_IS_A_URL', 'fast-forward', 'hi', 'there', ':)', 'how', '??', 'u.s.a', '.', 'THIS_IS_A_MENTION', 'what', '?', 'HASHTAG_awesome', '.']
        >>> tk = Tokenizer(rt_prefix=True)
        >>> tk.do_tokenize('RT hi there')
        ['RT_hi', 'RT_there']
        >>> tk.do_tokenize('hi there')
        ['hi', 'there']
        """
        text = text.lower() if self.lc else text
        if self.collapse_hashtags:
            text = re.sub('#\S+', 'THIS_IS_A_HASHTAG', text)
        else:
            text = re.sub('#(\S+)', r'HASHTAG_\1', text)
        if self.collapse_mentions:
            text = re.sub('@\S+', 'THIS_IS_A_MENTION', text)
        if self.collapse_urls:
            text = re.sub('http\S+', 'THIS_IS_A_URL', text)
        if self.limit_repeats:
            text = re.sub(r'(.)\1\1\1+', r'\1', text)
        if self.collapse_digits:
            text = re.sub(r'[0-9]+', '9', text)
        toks = []
        for tok in text.split():
            tok = re.sub(r'^(' + punc_re + '+)', r'\1 ', tok)
            tok = re.sub(r'(' + punc_re + '+)$', r' \1', tok)
            for subtok in tok.split():
                if self.retain_punc_toks or re.search('\w', subtok):
                    toks.append(subtok)
        if self.rt_prefix:
            rt_text = 'rt' if self.lc else 'RT'
            if rt_text in toks:
                toks.remove(rt_text)
                toks = ['RT_' + t for t in toks]
        return toks

    def tokenize(self, tw):
        """ Given a Tweet object, return a dict mapping field name to tokens. """
        toks = defaultdict(lambda: [])
        for field in self.fields:
            if '.' in field:
                parts = field.split('.')
                value = tw.js
                for p in parts:
                    value = value[p]
            else:
                value = tw.js[field]
            toks[field].extend(self.do_tokenize(value))
        return dict([(f, v) for f, v in toks.iteritems()])
