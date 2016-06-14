#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import sys, os, fileinput
from itertools import imap, islice, product

# patterns
reservedWords = { 'to', 'so', 'not', 'where', 'which',
                  'that', 'as', 'if', 'though', 'and',
                  'by', 'with', 'together', 'way', 'into' }
simple_Vpatterns = set( 'V, V n, V pl-n, V pron-refl, V amount, '
                        'V adj, V v-ing, V to -inf, V inf, V that, '
                        'V wh, V wh to -inf, V quote, V so, V not, '
                        'V as if, V as though, V and V, '
                        'V prep, V adv, pl-n V together, '
                        'V about n, V across n, V after n, V against n, '
                        'V around n, V round n, V as adj, V as n, '
                        'V as to wh, V at n, V between pl-n, '
                        'V by amount, V by v-ing, V for n, V from n, '
                        'V in n, V into n, V in favor of n, V like n, '
                        'V of n, V off n, V on n, V on n, V onto n, '
                        'V out of n, V over n, V through n, V to n, '
                        'V towards n, V toward n, V under n, V with n, '
                        'V among pl-n, V adj among pl-n, V before n, '
                        'V behind n, V down n, V past n'.split(', '))
complex_Vpatterns = set('V n n, V n prep n, V n n prep, V n n that, V n adj, '
                        'V n v-ing, V n to -inf, Vn -inf, V n that, V n wh, '
                        'V n wh to -inf, V n quote, V n v-ed, '
                        'V n prep, V n adv, V adv n, V pl-n together, '
                        'V way prep, V way adv, V n about n, V n against n, '
                        'V n as adj, V n as n, V n as to wh, V n at n, '
                        'V n between pl-n, V n among pl-n, V n by n, '
                        'V n for n, V n from n, V n in n, V n into v-ing, '
                        'V n of n, V n off n, V n out of n, V n over n, '
                        'V n on n, V n onto n, V n on to n, '
                        'V n to n, V n towards n, V n toward n, V n with n, '
                        'V n after n, V n around n, V n round n, '
                        'V n before n, V n through n'.split(', '))
passive_Vpatterns = set('V-ed prep, '
                        'be V-ed n, be V-ed prep n, be V-ed n prep, be V-ed n that, '
                        'be V-ed adj'.split(', '))
Vpatterns = simple_Vpatterns | complex_Vpatterns | passive_Vpatterns
Npatterns = set("N that, N to -inf, the N, N v-ing, N 's ADJST, "
                "N about -inf, N prep n, N of amount N of pl-n, "
                "N of n as n, N of n to n, N of n with n, "
                "N on n for n, N on n to -inf, N ord ADJ?, "
                "N to n that, N to n to -inf, N with n for n, "
                "N with n that, N with n to -inf, N for n to -inf, "
                "N from n for n, N from n that, N from n to -inf, "
                "N from n to n, "
                "number N, n of N, n to N, "
                "on N, with N, within N, without N, in N, "
                "in N of n, "
                "N be, there be N, there be ? about N".split(', '))
Apatterns = set('a ADJ amount, ADJ adj, ADJ and adj, ADJ that, ADJ to-inf, ADJ enough, ADJ v-ing, ADJ n, ADJ wh however ADJ, '
                'ADJ prep n, ADJ after v-ing, ADJ as to wh, ADJ enough n, ADJ enough PREP2 n, ADJ in color, ADJ onto v-ing n, '
                'ADJ PREP1 n for? n, ADJ to n for v-ing n, ADJ enough for n to-inf, ADJ enough that, ADJ enough to -inf, '
                'ADJ enough n for n, ADJ enough n for n to-inf, ADJ enough n that, ADJ enough n to-inf, ADJ n for n, '
                'ADJR n than clause, ADJR n than n, ADJR n than prep, ADJR than done n, ADJR than adj, ADJR than someway, '
                'adv. ADJ, adv. ADJ n, amount ADJ, as ADJ as COMP, how ADJ COMP2, however ADJ'.split(', '))
allTemplate = Vpatterns | Npatterns | Apatterns

# pronouns
subject_personal_pronouns = set('i you he she we they'.split())
object_personal_pronouns = set('me you him her us them'.split())
pron_refl = set('myself yourself himself herself ourself ourselves yourselves themselves'.split())


def genElement(word, lemma, tag, phrase):
    res = []
    if lemma in reservedWords: res += [ lemma ]
    if tag in {'WDT', 'WP', 'WP$', 'WRB'}: res += ['wh']
    if phrase[0] == 'H':
        if tag == 'CD': res += [ 'amount' ]
        if tag[:2] == 'VB' and lemma == 'be': res += [ 'be' ]
        if tag == 'IN':
            res += [ lemma ]
            if phrase == 'H-PP': res += [ 'prep' ]
        elif tag in {'JJ', 'JJR', 'JJS'}: res += [ 'ADJ', 'adj' ]
        elif tag == {'RB', 'RBR', 'RBS', 'RP'}: res += [ 'ADV', 'adv' ]
        elif tag in {'NN', 'NNP'}: res += [ 'N', 'n' ]
        elif tag in {'NNS', 'NNPS'}: res += [ 'N', 'n' ] # [ 'pl-n', 'N', 'n' ]
        elif tag == 'VB': res += [ 'V', 'v', 'inf' ]
        elif tag == 'VBZ': res += [ 'V', 'v' ]
        elif tag == 'VBD': res += [ 'V', 'v' ]
        elif tag == 'VBG': res += [ 'V', 'v-ing' ]
        elif tag == 'VBN': res += [ 'V-ed', 'v-ed' ]
        elif tag == 'VBP': res += [ 'V', 'v', 'inf' ]
        elif tag == 'PRP': res += [ 'n' ]
    elif phrase[0] == 'I' and not res:
        res += [ '' ]
    elif phrase == 'O':
        return []
    return res

def genPattern(template, words, lemmas):
    res = []
    headword = ''
    for tag, word, lemma in zip(template, words, lemmas):
        if tag:
            if tag[0].isupper():
                headword = (headword if headword else lemma, tag[0])
                # leave VBN as VBN in pattern
                if tag == 'V-ed':
                    res += [ word ]
                else:
                    res += [ lemma ]
            elif tag in {'prep', 'wh'}: res += [ lemma ]
            elif tag in pron_refl: res += [ oneself ]
            elif tag == 'n': res += [ 'something' ]
            else: res += [ tag ]
    return headword, ' '.join(res)

def genCollocation(template, words, lemmas):
    res = []
    for tag, word, lemma in zip(template, words, lemmas):
        if tag:
            if tag in { 'V-ed', 'v-ed', 'v-ing' }:
                res += [ word ]
            elif tag in pron_refl: res += [ oneself ]
            else: res += [ lemma ]

            # if word in intensive_personal_pronouns: res = [ 'oneself' ]
            # if word in object_personal_pronouns: res = [ 'someone' ]
            # else: res = [ 'something' ]
    return ' '.join(res)

def to_str(elements):
    return ' '.join(filter(lambda x: x[0] if x else x, elements))

def findGoodPat(words, lemmas, tags, phrases):
    def next_n_chunk_distance(phrases, n):
        count = 0
        for i, phrase in enumerate(phrases):
            if phrase[0] == 'H':
                count += 1
                if count > n:
                    return i
            elif phrase[0] == 'O':
                return i
        return len(phrases)
                
    # generate elements such as V, N, ADV...
    elements = [ genElement(*x) for x in zip(words, lemmas, tags, phrases) ]

    length = len(elements)
    minend = 0
    for i in range(length-1):
        # start from concrete elements (neither empty nor blank)
        if not(elements[i] and elements[i][0]): continue
        # start from the end to generate pattern as long as possible
        for j in range(max(i+2, minend), min(i+10, length+1))[::-1]:
            # elements[i:j] contains no empty element and does not end with blank element
            if [] in elements[i:j] or not elements[j-1][0]: continue
            # in template
            templates = [ template for template in product(*elements[i:j]) if to_str(template) in allTemplate ]

            for template in templates:
                headword, pat = genPattern(template, words[i:j], lemmas[i:j])
                headword = '%s:%s' % headword
                col = genCollocation(template, words[i:j], lemmas[i:j])
                history = ' '.join(words[:i])
                lookahead_index = j + next_n_chunk_distance(phrases[j:], 1)
                lookahead = ' '.join(words[j:lookahead_index])
                ngram = ' '.join(words[i:j])
                sent = '%s [%s] %s' % (history, ngram, lookahead)
                yield headword, pat, col, sent.strip()
                break
            if templates:
                minend = max(minend, j+1)
                # print elements[i:j]
                # print templates
                break

if __name__ == '__main__':
    for i, line in enumerate(fileinput.input()):
        # if i >= 100: continue
        if not line: continue
        line = line.decode('utf-8').strip()
        # print
        # print i, line
        # print
        words, lemmas, tags, phrases = [ x.split(' ') for x in line.split('\t') ]
        lemmas = map(unicode.lower, lemmas)

        for patInfo in findGoodPat(words, lemmas, tags, phrases):
 
            # format: headword:postag<tab>pattern<tab>collocation<tab>sentence
            print '\t'.join( info.encode('unicode_escape') for info in patInfo )
        # print