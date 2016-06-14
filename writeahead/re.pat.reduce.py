#!/usr/bin/env python 
# -*- coding: utf-8 -*-
from __future__ import division

import sys, fileinput
import operator
import json

from collections import Counter, defaultdict, OrderedDict
from itertools import groupby, imap, islice
from math import sqrt

# pv citeseerx.sents.tagged.h.10000.txt | sh local_mapreduce.sh 0.8m 10 'python col.map.py' 'python col.reduce.py' result_dir


class OrderedDefaultDict(OrderedDict):
    def __init__(self, default_factory=None, *args, **kwargs):
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        val = self[key] = self.default_factory()
        return val

k0 = 1
k1 = 1
U0 = 10
minCount = 10

class wordPat(Counter):
    def __init__(self):
        self.default_factory = Counter

    def __repr__(self):
        #tail = ', ...' if len(self) > 3 else ''
        items = ', \n    '.join(map(str, self.iteritems()))
        return '{}(freq = {}, avg_freq = {}, dev = {}, \n \n)'.format(self.__class__.__name__, self.freq, self.avg_freq, self.dev, items)

    def calc_metrics(self):
        self.freq = sum(self.values())
        self.avg_freq = self.freq/len(self)
        self.dev = sqrt(sum((xfreq - self.avg_freq)**2 for xfreq in self.values() )/len(self))

    def gen_goodpat(self):
        if self.freq == 0 or self.dev == 0: return
        for pat, count in self.most_common():
            if (count - self.avg_freq) / self.dev <= k0:
                break
            if count <= minCount:
                break
            yield pat, count
    

#difficulty:N	difficulty about something	difficulty about learning	difficulty about multiagent learning	1	4	8
def line_to_word(x):
    return x.strip().split('\t')[0]
    
def line_to_pat(x):
    return x.strip().split('\t')[1]
    
def line_to_col(x):
    return x.strip().split('\t')[2]
    
def line_to_ngram(x):
    return x.strip().split('\t')[3]
    
def line_to_rest(x):
    return '\t'.join(x.strip().split('\t')[2:4])

# def get_new_pattern():
#     with open('new_pat3.txt') as newpat:
#         dict_new_pat = { line.strip().split('\t')[0]:line.strip().split('\t')[1] for line in newpat.readlines() }
#     return dict_new_pat

if __name__ == '__main__':
    table = {}
#     dict_new_pat = get_new_pattern()

#     input_text = [ for line in fileinput.input() if line.split('\t')[1].split()]
# for line in fileinput.input():
#         line_list = line.split('\t')
#         if 'something' in line_list[1].split():
#             if line_list[1] in dict_new_pat:
#                 line_list[1] = dict_new_pat[line_list[1]]
#                 print ' '.join(line_list)
#             else:
#                 print line
#         else :
#             print line
    for word, lines in groupby(fileinput.input(), key=line_to_word):
        # ISSUE: The input is sorted only by key, direct groupby doesn't perform as expected - same pats are grouped
        # patInstances = [ (pat, list(instances)) for pat, instances in groupby(lines, key=line_to_pat) ]
        # FIX: sort by pat first so that instances with the same patterns would be grouped correctly
        lines = sorted(lines)

        # print lines

        patInstances = { pat: list(instances) for pat, instances in groupby(lines, key=line_to_pat) }
        patCounts = { pat: len(instances) for pat, instances in patInstances.iteritems() }

        patterns = wordPat()
        patterns.update( patCounts )
        patterns.calc_metrics()

        goodPats = list(patterns.gen_goodpat())
        
        if goodPats:
            #print
            #print '%s (%s)'%(word, sum([ count for _, count in goodPats])) #, goodPats
            #print
            table[word] = [ sum( count for _, count in goodPats ) ]
        else:
            continue
            
        for pat, count in goodPats[:7]:
            #print '\t*1*%s (%s)'%(pat, count)
            colInstances = { col: list(instances) for col, instances in groupby(patInstances[pat], key=line_to_col) }
            colCounts = { col: len(instances) for col, instances in colInstances.iteritems() }

            cols = wordPat()
            cols.update( colCounts )
            cols.calc_metrics()
            goodCols = list(cols.gen_goodpat())
            #print '\t*2*%s (%s)'%(pat, patCounts[pat]), goodCols

            # TODO: best ngram selection
            #   Ngram used to be one chunk before pattern, so it's common to see instances with the same ngram
            #   While the ngram starts from the beginning of the sentence now
            #   Is it appropriate to select the best ngram by their frequecies? while they might all be 1
            if not goodCols:
                #print '\t%s (%s)'%(pat, patCounts[pat]) #, goodCols
                #print
                bestngram = max( (len(list(instances)), ngram) for ngram, instances in groupby(patInstances[pat], key=line_to_ngram) )
                #print '\t\t%s (%s, %s)'%(bestngram[1], colCounts[col], bestngram[0])

                # ISSUE: variable 'col' not exists
                # FIX: total count
                # table[word] += [ [pat, patCounts[pat], [(bestngram[1], colCounts[col], bestngram[0])]] ]
                counts = sum( colCounts.values() )
                table[word] += [ [pat, patCounts[pat], [(bestngram[1], count, bestngram[0])]] ]

                #print
                continue
            res = []
            for col, count in goodCols[:5]:
                bestngram = max( (len(list(instances)), ngram) for ngram, instances in groupby(colInstances[col], key=line_to_ngram) )
                #print '\t\t%s (%s, %s)'%(bestngram[1], colCounts[col], bestngram[0])
                res += [(bestngram[1], colCounts[col], bestngram[0])]
            table[word] += [ [pat, patCounts[pat], res] ]
            #print
            
    #print table
    print json.dumps(table)

'''with open('test.json.txt', 'w') as outfile:
     json.dump(table, outfile)
table = {}
with open('test.json.txt', 'r') as infile:
    table = json.load(infile)
print table'''
