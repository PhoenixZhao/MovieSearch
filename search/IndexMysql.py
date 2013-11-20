#!/usr/bin/env python
# -*- coding: utf-8 -*-
#coding:utf-8

import sys, os, lucene, threading, time
from datetime import datetime

#from lucene import \
#    NumericField


from java.io import File
from java.util import Map,HashMap
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
#from org.apache.lucene.analysis.cn import ChineseAnalyzer
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, FloatField,IntField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.search.similarities import BM25Similarity

from org.apache.lucene.analysis.miscellaneous import PerFieldAnalyzerWrapper

import MySQLdb as mdb


from sqlConstants import *

#what need to do 
#step 1. change config below
#step 2. make right connection to the sql
#step 3. choose right table
#step 4. select the field of the table you need to index or store


#------step 1------
#---start config---

#the dir to store the index file
INDEX_DIR = "/home/env-shared/NGfiles/lucene_index"
#the field name you want to index
FIELD = 'summary'

#---end config---



class Ticker(object):
    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

def CreateAWrapper():

        # Map<String,Analyzer> analyzerPerField = new HashMap<String,Analyzer>();


        analyzerPerField = HashMap()
        #为所有的域设置不同的analyzer  
        analyzerPerField.put('rating_max', StandardAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('rating_average', StandardAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('rating_stars', StandardAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('rating_min', StandardAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('reviews_count', StandardAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('wish_count', StandardAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('year', StandardAnalyzer(Version.LUCENE_CURRENT))

        analyzerPerField.put('title', SmartChineseAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('original_title', SmartChineseAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('summary', SmartChineseAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('aka', SmartChineseAnalyzer(Version.LUCENE_CURRENT))

        analyzerPerField.put('genres', WhitespaceAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('casts', WhitespaceAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('countries', WhitespaceAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('summary_segmentation', WhitespaceAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('subtype', WhitespaceAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('directors', WhitespaceAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('user_tags', WhitespaceAnalyzer(Version.LUCENE_CURRENT))
        analyzerPerField.put('others_like', WhitespaceAnalyzer(Version.LUCENE_CURRENT))

        #analyzerPerField.put('douban_site', StandardAnalyzer(Version.LUCENE_CURRENT))注释起来的都是没必要分析的
        #analyzerPerField.put('image_small', StandardAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('image_large', StandardAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('image_medium', StandardAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('subject_url', StandardAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('subject_id', StandardAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('mobile_url', StandardAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('do_count', StandardAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('seasons_count', StandardAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('schedule_url', StandardAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('episodes_count', StandardAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('current_season', new KeywordAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('collect_count', new KeywordAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('comments_count', StandardAnalyzer(Version.LUCENE_CURRENT))
        #analyzerPerField.put('ratings_count', StandardAnalyzer(Version.LUCENE_CURRENT))

        aWapper = PerFieldAnalyzerWrapper(SmartChineseAnalyzer(Version.LUCENE_CURRENT),analyzerPerField)

        return aWapper

class IndexMySql(object):
    """Usage: python IndexFiles.py"""

    def __init__(self, storeDir, aWrapper):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        store = SimpleFSDirectory(File(storeDir))
        aWrapper = LimitTokenCountAnalyzer(aWrapper, 1048576)
        bm25Sim = BM25Similarity(2.0,0.75) #BM25 with these default values: k1 = 1.2, b = 0.75.
        config = IndexWriterConfig(Version.LUCENE_CURRENT, aWrapper)
        config.setSimilarity(bm25Sim)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)


        self.indexTable(writer)
        ticker = Ticker()
        print 'commit index'
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexTable(self, writer):

        #connection 
        con = None

        #define the index of all the fields
        #---------step 2----------
        con = mdb.connect('localhost','root','testgce','douban_movie_v2')

        #t_num = FieldType.NumericType it is wrong!!
        t_num = FieldType()
        t_num.setStored(False)

        t1 = FieldType()
        t1.setIndexed(True)
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS)
        
        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        t3 = FieldType()
        t3.setIndexed(True)
        t3.setStored(True)
        t3.setTokenized(True)
        t3.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS)

        with con:
            # Careful with codecs
            con.set_character_set('utf8')

            cur = con.cursor()
            # Aagin the codecs
            cur.execute('SET NAMES utf8;')
            cur.execute('SET CHARACTER SET utf8;')
            cur.execute('SET character_set_connection=utf8;')
            
            #------step 3------
            cur.execute("SELECT * FROM movie_items")

            numrows = int(cur.rowcount)
            print 'numrows:',numrows
            for i in range(numrows):
                row = cur.fetchone()

                #------step 4------
                summary = row[SUMMARY]  
                subject_id = row[SUBJECT_ID]


                print 'id'+subject_id
                #print 'summary'+summary+'end'

                doc = Document()
                #fields which should not be analyzed
                doc.add(FloatField("rating_average",float(row[RATING_AVERAGE]),Field.Store.NO))
                doc.add(FloatField("rating_stars", float(row[RATING_STARS]), Field.Store.NO))
                doc.add(IntField("reviews_count", int(row[REVIEWS_COUNT]), Field.Store.NO))
                #doc.add(FloatField("year", float(row[YEAR]), Field.Store.NO))
                doc.add(IntField("collect_count", int(row[COLLECT_COUNT]), Field.Store.NO))
                doc.add(IntField("subject_id", int(subject_id), Field.Store.YES))
                doc.add(IntField("comments_count", int(row[COMMENTS_COUNT]), Field.Store.NO))
                doc.add(IntField("ratings_count", int(row[RATINGS_COUNT]), Field.Store.NO))
                doc.add(Field("image_small", row[IMAGE_SMALL], t1))

                #fields which should be analyzed with WhitespaceAnalyzer
                doc.add(Field("countries", row[COUNTRIES].replace('..',' '), t3))
                doc.add(Field("casts",     row[CASTS].replace('..',' '),     t3))
                doc.add(Field("genres",    row[GENRES].replace('..',' '),    t3))
                doc.add(Field("subtype",   row[SUBTYPE].replace('..',' '),   t2))
                doc.add(Field("directors", row[DIRECTORS].replace('..',' '), t3))

                user_tags_str = ''
                others_like_str = ''
                '''
                print 'user_tags'+row[USER_TAGS]
                print 'others_like'+row[OTHERS_LIKE]
                
                if row[USER_TAGS]!='':
                    for tag_pair in row[USER_TAGS].split('..'):
                        if tag_pair!='':#字符串的最后一个字符是:，这样split之后最后一个元素是空字符
                            user_tags_str = user_tags_str +' '+tag_pair.split(':')[0]
                if row[OTHERS_LIKE]!='':
                    for like_pair in row[OTHERS_LIKE].split('..'):
                        if like_pair!='':
                            others_like_str = others_like_str +' '+like_pair.split(':')[1]
                '''

                print user_tags_str
                print others_like_str


                doc.add(Field("user_tags", user_tags_str, t3))
                doc.add(Field("others_like", others_like_str, t3))

                #fields which should be analyzed with good analyzer
                doc.add(Field("title", row[TITLE], t3))                
                doc.add(Field("original_title", row[ORIGINAL_TITLE], t2))
                doc.add(Field("summary_segmentation", row[SUMMARY_SEGMENTATION], t2))
                doc.add(Field("aka", row[AKA], t2))

                if len(summary) > 0:
                    print subject_id +'--->'+':\n    '+ row[TITLE]
                    try:
                        summary_unicoded = unicode(summary, 'utf-8') #test the encoding 
                    except Exception,e:
                        print "Decode Failed: ", e
                    doc.add(Field('summary', summary, t2))
                else:
                    print "warning:\n" + subject_id +'---> No content!'
                writer.addDocument(doc)



if __name__ == '__main__':
    if len(sys.argv) !=1:
        print IndexMySql.__doc__
        sys.exit(1)
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    start = datetime.now()
    #try:
    CreateAWrapper()

    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    aWrapper = CreateAWrapper()
    IndexMySql(os.path.join(base_dir, INDEX_DIR), aWrapper)
    end = datetime.now()
    print end - start
    #except Exception, e:
    #    print "Failed: ", e
    #    raise e
