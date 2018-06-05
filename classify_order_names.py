#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
import os
import lib
import random
import jieba

class Keyword():
    def __init__(self, word, category, weight):
        self.word = word
        self.category = category
        self.weight = weight
    def __str__(self):
        return self.word + "," + self.category + "," + str(self.weight)

def to_int(number):
    try:
        return int(number)
    except ValueError:
        return 0

def read_keywords(inputFileName):
    assert(os.path.exists(inputFileName))
    keywords = []
    ifile = open(inputFileName, "r")
    for (index, string) in enumerate(ifile):
        tempArray = string.strip("\n").split(",")
        if (len(tempArray) != 3):
            print string.strip("\n")
            continue
        word = lib.toString(tempArray[0])
        category = tempArray[1]
        weight = to_int(tempArray[2])
        keywords.append(Keyword(word, category, weight))
    ifile.close()
    return keywords

def get_order_names(inputFileName):
    assert(os.path.exists(inputFileName))
    header = ""
    lines = []
    ifile = open(inputFileName, "r")
    for (index, string) in enumerate(ifile):
        if (index == 0):
            header = string.strip("\n")
        else:
            lines.append(string.strip("\n").lower())
    ifile.close()

    assert("order_name" in header)
    order_name_index = header.split(",").index("order_name")
    return map(lambda line: lib.toString(line.split(",")[order_name_index]), lines)

class WordWeight():
    def __init__(self, word, weight):
        self.word = word
        self.weight = weight
    def __str__(self):
        return self.word + "," + str(self.weight)

def keywords_to_dictionary(keywords):
    dictionary = dict()
    for keyword in keywords:
        word = keyword.word
        category = keyword.category
        weight = keyword.weight
        if (not category in dictionary):
            temp = []
            temp.append(WordWeight(word, weight))
            dictionary[category] = temp
        else:
            dictionary[category].append(WordWeight(word, weight))
    return dictionary

def dictionary_to_string(dictionary):
    categories = dictionary.keys()
    result = ""
    for key in categories:
        result += key + ":" + ";".join(map(str, dictionary[key])) + "\n"
    return result

def print_dictionary(dictionary, outputFileName):
    result = dictionary_to_string(dictionary)
    ofile = open(outputFileName, "w")
    ofile.write(result)
    ofile.close()

def cut_words(order_name, excluded_words):
    words = jieba.cut(order_name, cut_all = False)
    words = map(lib.toString, ",".join(words).split(","))
    words = filter(lambda word: not word in excluded_words, words)
    return words

def get_word_weight(word, weighted_word_list):
    weight = 0
    for i in range(len(weighted_word_list)):
        if (word == weighted_word_list[i].word):
            weight += weighted_word_list[i].weight
    return weight

'''
def get_order_weight(order_name, dictionary, excluded_words):
    words = cut_words(order_name, excluded_words)
    splitted_words = "/".join(words) 
    result = dict()
    for key in dictionary.keys():
        result[key] = 0
        weighted_word_list = dictionary[key]
        for i in range(len(words)):
            result[key] += get_word_weight(words[i], weighted_word_list)
    pairs = sorted(result.iteritems(), key = lambda (k, v): (v, k))
    pairs.reverse()
    return filter(lambda pair: pair[1] > 0, pairs), lib.toString(splitted_words)

def classify(order_name, dictionary):
    weights = get_order_weight(order_name, dictionary)
    max_weight = 0
    for key in weights.keys():
        if (max_weight < weights[key]):
            max_weight = weights[key]
    key_results = []
    for key in weights.keys():
        if (weights[key] == max_weight):
            key_results.append(key)
    return ",".join(key_results)

def classify_orders(order_names, dictionary, excluded_words, outputFileName):
    ofile = open(outputFileName, "w")
    for i in range(len(order_names)):
        weights, order_name_splitted = get_order_weight(order_names[i], dictionary, excluded_words)
        weight_string = ";".join(map(lambda pair: pair[0] + "," + str(pair[1]), weights))
        ofile.write(order_name_splitted + "|->" + weight_string + "\n")
    ofile.close()
'''

def read_excluded_words(inputFileName):
    assert(os.path.exists(inputFileName))
    excluded_words = []
    ifile = open(inputFileName, "r")
    string = ifile.readline()
    ifile.close()
    string = string.decode("utf-8")
    for i in range(len(string)):
        excluded_words.append(lib.toString(string[i]))
    return excluded_words

def get_order_weight(order_name, dictionary):
    order_name = order_name.lower()
    keys = dictionary.keys()
    weights = dict()
    for key in keys:
        weighted_word_list = dictionary[key]
        for i in range(len(weighted_word_list)):
            if (weighted_word_list[i].word in order_name):
                if (key in weights):
                    weights[key] += weighted_word_list[i].weight
                else:
                    weights[key] = weighted_word_list[i].weight
    pairs = sorted(weights.iteritems(), key = lambda (key, value): value)
    pairs.reverse()
    s = 0
    for i in range(len(pairs)):
        s += pairs[i][1]
    pairs = map(lambda pair: (pair[0], "%.2f"%(float(pair[1])/float(s))), pairs)
    return pairs

def classify_orders(order_names, dictionary, outputFileName):
    ofile = open(outputFileName, "w")
    numberOfIntervals = 100
    interval = len(order_names)/numberOfIntervals
    for i in range(len(order_names)):
        if (i%interval == 0):
            print "Step index = " + str(i/interval + 1) + ", total = " + str(numberOfIntervals)
        weights = get_order_weight(order_names[i], dictionary)
        ofile.write(order_names[i] + "|->" + ";".join(map(lambda pair: pair[0] + "," + str(pair[1]), weights)) + "\n")
    ofile.close()

def main():
    import sys

    excluded_words = read_excluded_words("excluded_words.txt")
    keywordFileName = "keyword_category_weight.txt"
    keywords = read_keywords(keywordFileName)
    dictionary = keywords_to_dictionary(keywords)
    print_dictionary(dictionary, "keywords.dic")
    '''order_name = "九阳（Joyoung）DJ13B-C659SG多功能全钢免滤豆浆机红色经典 C662SG、C656SG升级版"
    print order_name
    weights = get_order_weight(order_name, dictionary)
    print "\n".join(map(lambda pair: pair[0] + ": " + str(pair[1]), weights))'''
    #weights = get_order_weight(order_name, dictionary, excluded_words)
    print "Getting order names ... "
    order_names = get_order_names("train.csv")
    print "Order names obatined. "
    print "Classifying orders ... "
    classify_orders(order_names, dictionary, "order_names_classified.txt")
    print "Classification done. "
    #classify_orders(order_names, dictionary, excluded_words, "order_names_classified.txt")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
