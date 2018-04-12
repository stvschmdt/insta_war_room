#author steve schmidt
#this class object takes in a instaparse object or the
#equivalent data structures to format into the following
#   paragraph level text
#   sentence level text
#   word histogram
#   word tag dictionary
from __builtin__ import any as b_any

import csv
import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt
import collections
import networkx as nx
import ipdb


from nltk import sent_tokenize, word_tokenize, pos_tag
from collections import Counter
from unidecode import unidecode


import logger
import instaparse
import graphbuilder

class Analyzer(object):

    def __init__(self, IP, FLAGS):
        self.log = logger.Logging()
        if not FLAGS.outfile:
            self.log.error('must supply an output file')
        else:
            if FLAGS.all:
                self.paragraphs = self.create_paragraphs(IP.comments.values())
                self.num_paragraphs = len(self.paragraphs)
                self.sentences = self.create_sentences(IP.comments.values())
                self.num_sentences = len(self.sentences)
                self.words, self.pos_words = self.create_words(IP.comments.values())
                self.num_words = len(self.words)
            elif FLAGS.sent:
                self.create_sentences(IP.comments.values())
                self.words, self.pos_words = self.create_words(IP.comments.values())
                self.num_words = len(self.words)
            elif FLAGS.para:
                self.create_paragraphs(IP.comments.values())
                self.words, self.pos_words = self.create_words(IP.comments.values())
                self.num_words = len(self.words)
               
    #create paragraphs, this is probably less important than sentences
    def create_paragraphs(self, paragraphs):
        para_list = []
        for idx, para in enumerate(paragraphs):
            para = self.clean(para)
            para_list.append(para)
        self.log.info('found %s paragraphs'%len(para_list))
        self.write_data('paragraphs', para_list)
        return para_list

    #create a list of sentences used in comments - each actual sentence is a sentence, use helper function for nltk
    def create_sentences(self, sentences):
        sent_list = []
        #extra little something
        pos_tag_list = []
        #input must just be the vals of the dict = aka a list of comments
        for idx, sent in enumerate(sentences):
            try:
                #split the comments in case multiple sentences or fragments
                splitter = sent_tokenize(sent)
            except Exception as e:
                print idx
            for split in splitter:
                split = self.clean(split)
                sent_list.append(split)
        self.log.info('found %s sentences'%len(sent_list))
        self.write_data('sentences',sent_list)
        return sent_list
    
    #helper function to clean some rando off the strings before encoding
    def clean(self, tok):
        tok = tok.replace(':','')
        tok = tok.replace(';','')
        tok = tok.replace('(','')
        tok = tok.replace(')','')
        tok = tok.replace('-','')
        return tok

    def create_words(self, corpus):
        word_dict = collections.defaultdict(int)
        tag_dict = collections.defaultdict()
        #loop through corpus, clean, then split words and count em
        for idx,tok in enumerate(corpus):
            tok = self.clean(tok)
            words = word_tokenize(tok)
            for word in words:
                word_dict[word.lower()] += 1
            #get the nltk noun, verb tag out may as well
            tag_dict[idx] = pos_tag(words)
        self.log.info('found %s unique words'%len(word_dict))
        self.write_data('words',collections.OrderedDict(sorted(word_dict.items(), key=lambda val: val[1], reverse=True)))
        return collections.OrderedDict(sorted(word_dict.items(), key=lambda val: val[1], reverse=True)), tag_dict

    #return top word dict
    def top_n_words(self, n, data=None):
        if not data:
            data = self.words
        top = Counter(data)
        return top.most_common(n)

    def write_scrape_file(self, l_clique):
        with open('scrape_file.txt', 'w') as f:
            for l in l_clique:
                f.write('{}\n'.format(unidecode(l)))

    def write_data(self, filename, data):
        filename = filename + '.csv'
        with open(filename, 'w') as f:
            if type(data) == list:
                for d in data:
                    f.write('{}\n'.format(str(d)))
            else:
                writer = csv.writer(f)
                for k, v in data.items():
                    writer.writerow([k.encode('utf-8')] + [v])
        self.log.info('wrote %s lines to %s'%(len(data), filename))

    def write_clique_list(self, filename, cliqs):
        filename = filename + '.csv'
        with open(filename, 'w') as f:
            for cliq in cliqs:
                f.write(','.join(cliq).encode('utf-8') +'\n')


if __name__ == '__main__':
    #argument parser - demand an infile to avoid overwriting data
    parser = argparse.ArgumentParser()
    parser.add_argument('-of', dest='outfile', default='../data/', help='supply outfile to save data into')
    parser.add_argument('-if', dest='infile', default='../data/', help='supply infile for instaparse')
    parser.add_argument('-graphics', dest='graphics', default=False, action='store_true', help='turn graphics on / off')
    parser.add_argument('-create', dest='create', default=True, action='store_true', help='create full dictionary')
    parser.add_argument('-all', dest='all', default=True, action='store_true', help='create all dictionarys')
    parser.add_argument('-hop', dest='hop', default=None, help='first hop to analyze')
    #store in FLAGS
    FLAGS = parser.parse_args()
    #instaparse object
    if not (FLAGS.outfile and FLAGS.infile):
        print 'USAGE: must supply outfile to save data'
    else:
        # this is the main instaparse
        ip = instaparse.InstaParse(FLAGS.infile, FLAGS)
        top_word = ip.top_n_hashtags(1)[0]
        print top_word
        if FLAGS.hop == None:
            fitness = instaparse.InstaParse('../data/fitness/fitness.json', FLAGS)
            gym = instaparse.InstaParse('../data/gym/gym.json', FLAGS)
            bodybuilding = instaparse.InstaParse('../data/gym/gym.json', FLAGS)
            quitsugar = instaparse.InstaParse('../data/quitsugar/quitsugar.json', FLAGS)
            health = instaparse.InstaParse('../data/health/health.json', FLAGS)
            nutrition = instaparse.InstaParse('../data/nutrition/nutrition.json', FLAGS)
        else:
            hop = instaparse.InstaParse('../data/' + str(top_word) + '.json', FLAGS)
            
        #return dictionary
        data = ip.get_data()
        fitness_data = ip.get_data()
        gym_data = ip.get_data()
        bodybuilding_data = ip.get_data()
        quitsugar_data = ip.get_data()
        health_data = ip.get_data()
        nutrition_data = ip.get_data()
        #build analyzer object to test
        f = Analyzer(ip, FLAGS)	
        fitness_f = Analyzer(fitness, FLAGS)
        gym_f = Analyzer(gym, FLAGS)
        bodybuilding_f = Analyzer(bodybuilding, FLAGS)
        quitsugar_f = Analyzer(quitsugar, FLAGS)
        health_f = Analyzer(health, FLAGS)
        nutrition_f = Analyzer(nutrition, FLAGS)
        #grab top tags to eliminate things like 1 or 2 freq items
        top_tags = [ t for t,c in ip.tags.items() if c >= 5 ]
        fitness_top_tags = [ t for t,c in fitness.tags.items() if c >= 10 ]
        gym_top_tags = [ t for t,c in gym.tags.items() if c >= 10 ]
        bodybuilding_top_tags = [ t for t,c in bodybuilding.tags.items() if c >= 10 ]
        quitsugar_top_tags = [ t for t,c in quitsugar.tags.items() if c >= 10 ]
        health_top_tags = [ t for t,c in health.tags.items() if c >= 10 ]
        nutrition_top_tags = [ t for t,c in nutrition.tags.items() if c >= 10 ]
        
        #build a networkx graph
        graph = graphbuilder.GraphBuilder()
        graph.edges_from_text(ip.d_insta, top_tags, 'cravecrush')
        wts = nx.get_node_attributes(graph.G,'weight')
        dp = nx.spring_layout(graph.G)
        nx.draw_networkx_labels(graph.G,dp,font_size=8,font_family='sans-serif')
        nx.draw(graph.G, dp,node_size=11,node_color='black',edge_color='y')
        plt.savefig('origin.png')
        if FLAGS.graphics:
            plt.show()

        #add on hop data
        graph.edges_from_text(fitness.d_insta, fitness_top_tags, 'fitness')
        graph.edges_from_text(gym.d_insta, gym_top_tags, 'gym')
        graph.edges_from_text(bodybuilding.d_insta, bodybuilding_top_tags, 'bodybuilding')
        graph.edges_from_text(quitsugar.d_insta, quitsugar_top_tags, 'quitsugar')
        graph.edges_from_text(health.d_insta, health_top_tags, 'health')
        graph.edges_from_text(nutrition.d_insta, nutrition_top_tags, 'nutrition')

        # connected components
        ccs = list(nx.connected_component_subgraphs(graph.G))
        print 'connected components:', len(ccs)

        # density of graph
        print 'density of G: ',nx.density(graph.G)

        # clique analysis
        cliq_list = sorted(list(nx.find_cliques(graph.G)), key=lambda val: len(val),reverse=True)
        print ('found %s cliques'%len(cliq_list))
        skips = ['crave', 'crush']
        cliques = []
        for c in cliq_list:
            cliq_set = set()
            for word in c:
                if b_any(x in word for x in skips):
                    pass
                else:
                    cliq_set.add(word)
            cliques.append(cliq_set)
        #f.write_clique(next_scrapings)
        #nx.make_max_clique_graph(graph.G)


        # ____________ make these functions _________________

        pos = nx.spring_layout(graph.G, scale=20, k=7)
        elarge=[(u,v) for (u,v,d) in graph.G.edges(data=True) if d['weight'] > 35]
        esmall=[(u,v) for (u,v,d) in graph.G.edges(data=True) if d['weight'] <= 35]
        #ipdb.set_trace()
        fitness=[n for n in graph.G.nodes(data=True) if n[1]['cluster'] == 'fitness']
        gym=[n for n in graph.G.nodes(data=True) if n[1]['cluster'] == 'gym']
        bodybuilding=[n for n in graph.G.nodes(data=True) if n[1]['cluster'] == 'bodybuilding']
        quitsugar=[n for n in graph.G.nodes(data=True) if n[1]['cluster'] == 'quitsugar']
        health=[n for n in graph.G.nodes(data=True) if n[1]['cluster'] == 'health']
        nutrition=[n for n in graph.G.nodes(data=True) if n[1]['cluster'] == 'nutrition']
        crave=[n for n in graph.G.nodes(data=True) if n[1]['cluster'] == 'cravecrush']
        colors = []
        for n in graph.G.nodes(data=True):
            if n[1]['cluster'] == 'cravecrush':
                colors.append('black')
            elif n[1]['cluster'] == 'fitness':
                colors.append('red')
            elif n[1]['cluster'] == 'gym':
                colors.append('orange')
            elif n[1]['cluster'] == 'bodybuilding':
                colors.append('cyan')
            elif n[1]['cluster'] == 'quitsugar':
                colors.append('blue')
            elif n[1]['cluster'] == 'health':
                colors.append('green')
            elif n[1]['cluster'] == 'nutrition':
                colors.append('magenta')
        e_color = []
        for u,v,d in graph.G.edges(data=True):
            if d['weight'] > 20:
                e_color.append('blue')
            else:
                e_color.append('yellow')

        # ____________________________________________________
        if FLAGS.graphics:
            #nx.draw_networkx_nodes(graph.G,pos,node_list=crave, node_color='green', node_size=20)
            #nx.draw_networkx_nodes(graph.G,pos,node_list=fitness, node_color='red', node_size=20)
            nx.draw_networkx_edges(graph.G,pos,edgelist=elarge, width=.1, edge_color='blue')
            nx.draw_networkx_edges(graph.G,pos,edgelist=esmall, alpha=0.1, width=.1, edge_color='yellow',style='dotted')
            nx.draw_networkx_labels(graph.G,pos, font_size=7,font_family='sans-serif')
            nx.draw(graph.G, pos, prog='fdp',node_color=colors, font_weight='heavy',alpha=.5,edge_color=e_color,node_shape='s',node_size=20, style='dashed')
            plt.axis('off')
            plt.legend(scatterpoints=1)
            plt.savefig('nodes.png')
            plt.show()
        
        
        f.write_clique_list('cliques',cliques)
        f.write_data('neighbors',graph.node_report(graph.G))
