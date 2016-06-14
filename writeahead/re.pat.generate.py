#!/usr/bin/env python 
# -*- coding: utf-8 -*-
from __future__ import division

import sys, fileinput
import operator
import json

from collections import Counter, defaultdict, OrderedDict
from itertools import groupby, imap, islice
from math import sqrt

from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer

import re, itertools
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


    #for disambuate

def sim(x, y):
  return x.wup_similarity(y)

def wordSim(word1, word2, pos):
  simi = [ x.wup_similarity(y) for x in wn.synsets(word1, pos) for y in wn.synsets(word2, pos) ] 
  return max(simi) if simi else 0.0

def mostInfoSubsumer(word1, word2, pos):
    res = []
    for syn1 in wn.synsets(word1, pos):
        for syn2 in wn.synsets(word2, pos):
            res += syn1.lowest_common_hypernyms(syn2)
    if res:
        return max([(s.min_depth(), s) for s in res])[1]
    else:
        return None

def disambGroup(words, senses, pos):

    normalization = [ 0.0 for w in words ]
    support = [ [ 0.0 for syn in wn.synsets(w, pos) ] for w in words ] 
    phi = [ [ 0.0 for syn in wn.synsets(w, pos) ] for w in words ]
     
    num_senses = [ len(support[i]) for i, w in enumerate(words) ]

    for i,j in itertools.product(range(len(words)), range(len(words))):
        if i >= j:
            continue
        
        cij = mostInfoSubsumer(words[i], words[j], pos)
        vij = wordSim(words[i], words[j], pos)
            
        for k in range(len(senses[i])):
            if cij and cij in senses[i][k].hypernym_paths()[0]:
                try:
                    support[i][k] += vij
                except:
                    pass
        for k2 in range(len(senses[j])):
            if cij and cij in senses[j][k2].hypernym_paths()[0]:
                try:
                    support[j][k2] += vij
                except:
                    pass
        try:
                normalization[i] += vij
                normalization[j] += vij
        except:
                pass
            

    for i, wi in enumerate(words):
        for k in range(len(phi[i])):
            if (normalization[i] > 0.0):
                phi[i][k] = support[i][k] / normalization[i]
            else:
                phi[i][k] = 1. / num_senses[i]

    res = []
    sense_cluster_dict = defaultdict(lambda:0)
    for i, wordSenseScore in enumerate(phi):
        cands = [ (score, senses[i][j]) for j, score in enumerate(wordSenseScore) ]
        if cands:
            sense = max(cands)
            sense_cluster_dict[sense[1].lexname()[5:]] += coll_count_dict[words[i]]
    
    # return res
    total_sense_count = 0
    for syn,value in sense_cluster_dict.iteritems():
        total_sense_count += value

    # to cal the probability for each class
    prob_class_dict = defaultdict(lambda:0)
    combine_prob_class_dict = defaultdict(lambda:0)
    for syn in sense_cluster_dict:
        # print '{} : [{}]\t{}'.format('Cluster',syn,sense_cluster_dict[syn]/total_sense_count)
        prob_class_dict[syn] = sense_cluster_dict[syn]/total_sense_count

    #return the heighest probability class
    #Combline the class to time, location, person, something
    # for syn in prob_class_dict:
    #     if syn != 'time' or 'person' or 'location':
    #          combine_prob_class_dict['Sth'] += prob_class_dict[syn]
    #     else:
    #         combine_prob_class_dict[syn] = prob_class_dict[syn]

    max_class = sorted(prob_class_dict.items(), key=operator.itemgetter(1),reverse = True)
    # max_class = max(combine_prob_class_dict.iteritems(), key=operator.itemgetter(1))
    # print max_class
    if max_class:
        return '|'.join(['{}({:.1f}%)'.format(word_name,word_prob*100) for word_name, word_prob in max_class[:2]])
    else:
        return ['Sth(100%)']
    #end of disambGroup


if __name__ == '__main__':
    table = {}
    with open('new_pat_test.txt','w') as output_pat_file:
        for word, lines in groupby(fileinput.input(), key=line_to_word):
            # ISSUE: The input is sorted only by key, direct groupby doesn't perform as expected - same pats are grouped
            # patInstances = [ (pat, list(instances)) for pat, instances in groupby(lines, key=line_to_pat) ]
            # FIX: sort by pat first so that instances with the same patterns would be grouped correctly
            lines = sorted(lines)
                                            # Eric 2016/5/24
            print
            print
            print lines[0]
            print 

            # print lines
            lines_modify = []
            if 'something' in [line.split('\t')[1].split() for line in lines][0]:
                
                for pat, instances in groupby(lines, key=line_to_pat):
                    print '\t'+pat
                    # print [ins for ins in instances]
                    # something position
                    adjusted_pat = pat.split()

                    sth_position = [pos for pos,word in enumerate(pat.split()) if word == 'something']
                    pat_leng = len(pat.split())

                    instances = list(instances)

                    print '\tLengh of Pattern : '+ str(pat_leng)

                    print 
                    # maybe have a lot of sth, we need to disambiguate every sth
                    for every_sth_word in sth_position:
                        group_num = sth_position.index(every_sth_word)
                        # print sth_position.find(every_sth_word)
                        print '\tPosition of sth :' + str(every_sth_word)

                        coll_count_dict = defaultdict(lambda : 0)

                        sth_words = []
                        # remove groupby
                        for instance in instances:

                            coll = instance.strip().split('\t')[2]
                            # print '\t\t\t' + coll
                            if len(coll.split()) != pat_leng : continue
                            print '\t\t\t' + coll
                            
                            pattern_seperate = [coll_seperate for coll_seperate in coll.split()]      
                            sth_words += [pattern_seperate[every_sth_word]]
                            coll_count_dict[pattern_seperate[every_sth_word]] +=1
                        
                        # group by same words
                        sth_words = [word for word,aa in groupby(sth_words)]
                        senses =  [ wn.synsets(word, 'n') for word in sth_words ]
                        # senses =  [ wn.synsets(word, 'n') for word in sth_words ]


                        if not senses:
                            print '\t\t' + 'Sth'
                            print '*************************------*************************'
                            adjusted_pat[every_sth_word] = 'Sth(Dismatch)'
                        elif not senses[0]:
                            print '\t\t' + 'Sth'
                            print '*************************------*************************'
                            adjusted_pat[every_sth_word] = 'Sth(Dismatch)'
                        else:
                            print '\t\t' + str(senses)
                            print disambGroup(sth_words,senses,'n')

                            adjusted_pat[every_sth_word] = disambGroup(sth_words,senses,'n')

                    new_pat = ' '.join(adjusted_pat)
                    # print pat
                    # print new_pat

                    print '{}\t{}'.format(pat,new_pat)
                    output_pat_file.write('{}\t{}\n'.format(pat,new_pat))

                # re-assembly the lines 
                # lines_temp = instances.split('\t')
                # lines_temp[1] = new_pat
                # lines_modify = '\t'.join(lines_temp)     

                # print lines_modify
                    # print '\t'+str(every_sth_word)
                    # print '\t\t'+str(senses)


                    # end of Eric
                    
        # patInstances = { pat: list(instances) for pat, instances in groupby(lines, key=line_to_pat) }
        # print 
        # print '****************'
        # print patInstances
        # print '****************'
        # patCounts = { pat: len(instances) for pat, instances in patInstances.iteritems() }

#         patterns = wordPat()
#         patterns.update( patCounts )
#         patterns.calc_metrics()

#         goodPats = list(patterns.gen_goodpat())
        
#         if goodPats:
#             #print
#             #print '%s (%s)'%(word, sum([ count for _, count in goodPats])) #, goodPats
#             #print
#             table[word] = [ sum( count for _, count in goodPats ) ]
#         else:
#             continue
            
#         for pat, count in goodPats[:7]:
#             #print '\t*1*%s (%s)'%(pat, count)
#             colInstances = { col: list(instances) for col, instances in groupby(patInstances[pat], key=line_to_col) }
#             colCounts = { col: len(instances) for col, instances in colInstances.iteritems() }

#             cols = wordPat()
#             cols.update( colCounts )
#             cols.calc_metrics()
#             goodCols = list(cols.gen_goodpat())
#             #print '\t*2*%s (%s)'%(pat, patCounts[pat]), goodCols

#             # TODO: best ngram selection
#             #   Ngram used to be one chunk before pattern, so it's common to see instances with the same ngram
#             #   While the ngram starts from the beginning of the sentence now
#             #   Is it appropriate to select the best ngram by their frequecies? while they might all be 1
#             if not goodCols:
#                 #print '\t%s (%s)'%(pat, patCounts[pat]) #, goodCols
#                 #print
#                 bestngram = max( (len(list(instances)), ngram) for ngram, instances in groupby(patInstances[pat], key=line_to_ngram) )
#                 #print '\t\t%s (%s, %s)'%(bestngram[1], colCounts[col], bestngram[0])

#                 # ISSUE: variable 'col' not exists
#                 # FIX: total count
#                 # table[word] += [ [pat, patCounts[pat], [(bestngram[1], colCounts[col], bestngram[0])]] ]
#                 counts = sum( colCounts.values() )
#                 table[word] += [ [pat, patCounts[pat], [(bestngram[1], count, bestngram[0])]] ]

#                 #print
#                 continue
#             res = []
#             for col, count in goodCols[:5]:
#                 bestngram = max( (len(list(instances)), ngram) for ngram, instances in groupby(colInstances[col], key=line_to_ngram) )
#                 #print '\t\t%s (%s, %s)'%(bestngram[1], colCounts[col], bestngram[0])
#                 res += [(bestngram[1], colCounts[col], bestngram[0])]
#             table[word] += [ [pat, patCounts[pat], res] ]
#             #print
            
#     #print table
#     print json.dumps(table)

# '''with open('test.json.txt', 'w') as outfile:
#      json.dump(table, outfile)
# table = {}
# with open('test.json.txt', 'r') as infile:
#     table = json.load(infile)
# print table'''
