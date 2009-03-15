#!/usr/bin/python

# renameSod.py

import re, os, sys

dicdir = 'sod-utf8/'

def searchKanjiIndex(lookup):
    kanji = re.compile('^%s' % lookup)
    
    kanjidic = open('kanjidic-utf8', 'r')
    
    for line in kanjidic.readlines():
        if(re.search(kanji, line)):
            indexHit = [x for x in line.split(' ') if x.startswith('DK')][0]

    kanjidic.close()
    return indexHit

def cutPng(f):
    kanji = f.replace('.png', '')
    return kanji

filelist = os.listdir(dicdir)

for f in filelist:
    old = dicdir+f
    new = dicdir+searchKanjiIndex(cutPng(f))+".png"
    os.rename(old, new)