#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import sys, fileinput
from collections import defaultdict
from nltk.corpus import wordnet as wn
from itertools import groupby

import itertools

#difficulty:N	difficulty about something	difficulty about learning	difficulty about multiagent learning	1	4	8
def line_to_word(x):
    return x.strip().split('\t')[0]

def line_to_pat(x):
    return x.strip().split('\t')[1]


# generate linggle_dict
def generate_linggle_dict():
    linggle_data_prefix = 'linggle_result/reducer-0'

    for i in range(8):
        with open(linggle_data_prefix + str(i)) as linggle:
            for line in linggle.readlines():
                list_line = line.strip().split('\t')
                linggle_dict[list_line[0]] = list_line[1]
    # print 'linggle_dict has built!'
    #end of generate linggle dict

#wornet get word class
def checkClass(word,poss_classes):
    # print 'Comparing:'
    # print word
    # print poss_classes

    #compare to the synset
    # can upgrade here to caculate the prob for everyone
    senses = [ each_class.lexname()[5:] for each_class in wn.synsets(word, 'n')]
    # print senses
    # print

    if any(word_class in poss_classes for word_class in senses):
        # print 'True Take!'
        return True
    else:
        # print 'False break!'
        return False


if __name__ == '__main__':

    linggle_dict = defaultdict(lambda: None)
    linggle_sentence_dict = defaultdict(lambda: defaultdict(lambda: (None)))

    patInstances = {}

    for word, lines in groupby(fileinput.input(), key=line_to_word):
        # print word
        # ISSUE: The input is sorted only by key, direct groupby doesn't perform as expected - same pats are grouped
        # patInstances = [ (pat, list(instances)) for pat, instances in groupby(lines, key=line_to_pat) ]
        # FIX: sort by pat first so that instances with the same patterns would be grouped correctly
        lines = sorted(lines)

        patInstances.update({ pat: list(instances) for pat, instances in groupby(lines, key=line_to_pat) }) 
    # print patInstances
    # print
    # print 'patInstances is Built!'

    generate_linggle_dict()

    for pat in linggle_dict:
        #deal with the term with 'something' first
        if 'something' in pat:
            # get something's position
            # print
            # print pat
            sth_position = [pos for pos,word in enumerate(pat.split()) if word == 'something']

            # segment something into something
            # {1: ['communication(76.8%)', 'person(23.2%)'], 3: ['communication(76.8%)', 'substance(23.2%)']}
            possible_class = {position:linggle_dict[pat].split()[position].split('|') for position in sth_position}
            # print possible_class

            #find sentence in the sentneces dataset
            if pat in patInstances:
                # possible sentence list
                possible_instances = patInstances[pat]
                # print possible_instances
                # try to find the right sentence
                for instance in possible_instances:
                    # print instance
                    #get coll 
                    coll = instance.strip().split('\t')[2]
                    # print coll

                    #use to check if every word is suitable, if it is , then take that instance
                    true_num = 0

                    #get corresponding word at the position
                    # may have over 1 'something'
                    for position in sth_position:
                        # print position
                        word = coll.split()[position]
                        # print word
                        #get possible classes also delete the part of (50%)
                        poss_classes = [classes[:classes.index('(')] for classes in possible_class[position]]
                        #check if is the right class
                        if checkClass(word,poss_classes):
                            # linggle_sentence_dict[pat][linggle_dict[pat]] = instance
                            true_num +=1
                            break
                    # maybe have over 1 something, so we need to check it is fit or not
                    if true_num == len(sth_position):
                        linggle_sentence_dict[pat][linggle_dict[pat]] = instance.strip().split('\t')[3]
                        break
            else:
                linggle_sentence_dict[pat][linggle_dict[pat]] = 'N/A'
        else:
            linggle_sentence_dict[pat][linggle_dict[pat]] = 'N/A'

    # print linggle_sentence_dict

    for pat in linggle_sentence_dict:
        for new_pat, sentence in linggle_sentence_dict[pat].iteritems():
            print '{}\t{}\t{}'.format(pat,new_pat,sentence)


