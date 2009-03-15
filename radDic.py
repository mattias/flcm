#!/usr/bin/python
# -*- coding: utf-8 -*-

# radDic.py

import re, os, sys
import random
try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  raise SystemExit("You need lxml to run this app!")

def kanxiRadDic(radicalList):
  newDic = open('classicalRad', 'w')
  kanjidicRadList = kanjidic2rads()
  listNewDic = []
  i = 0

  while i < 214:
    kanjiList = kanjidic2kanxi(str(i+1), radicalList, kanjidicRadList)
    for kanji in kanjiList:
      for character in kanjiList:
        for kanxi in character.iter('rad_value'):
          if(kanxi.get('rad_type') == 'classical'):
            if(int(kanxi.text) == i+1):
              for char in character:
                for literal in char.iter('literal'):
                    newDic.write(literal.text.encode('utf_8')+'\n')
                    print literal.text+' : Done!'
                    i=i+1

  newDic.close()
  return
def kanjidic2rads():
  kanjidic2 = etree.parse('dictionaries/kanjidic2.xml')
  root = kanjidic2.getroot()
  
  radList = []
  for character in root:
    for literal in character.iter('literal'):
      i = 0
      while i < 214:
        if(literal.text.strip() == radicalList[i][2].strip()):
          print str(i+1)+' : Found radical '+literal.text.strip()+', appending it to list!'
          radList.append(character)
        else:
          i = i+1
        i = i+1
  print len(radList)
  return radList
def kanjidic2kanxi(kanxiNum, radicalList, kanjidicRadList):
  kanxiRe = re.compile(u'^%s$' % kanxiNum, re.UNICODE)
  kanxiHit = []
  for character in kanjidicRadList:
    for kanxi in character.iter('rad_value'):
      if(kanxi.get('rad_type') == 'classical'):
        if(re.search(kanxiRe, kanxi.text)):
          kanxiHit.append(character)
          print kanxiNum + ' / 214'
          return kanxiHit
  
  return kanxiHit

def makeList():
  radical = re.compile(u'^\$', re.UNICODE)
  radkdic = open('dictionaries/radkfile2-utf8', 'r')
  radList = []
  line = radkdic.readline().decode('utf_8')
  
  while line:
    if(re.search(radical, line)):
      radList.append(line.strip())
    line = radkdic.readline().decode('utf_8')
    
  radkdic.close()
  return radList

radicalList = makeList()
  
kanxiRadDic(radicalList)
