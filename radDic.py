#!/usr/bin/python
# -*- coding: utf-8 -*-

# radDic.py

import re, os, sys
import random
import Image, ImageDraw, ImageFont
try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  raise SystemExit("You need lxml to run this app!")

def kanxiRadDic(radicalList):
  newDic = open('classicalRad', 'w')
  listNewDic = []
  i = 0

  while i < 50:
    kanjiList = kanjidic2kanxi(str(i+1))
    for kanji in kanjiList:
      for character in kanjiList:
        for kanxi in character.iter('rad_value'):
          if(kanxi.get('rad_type') == 'classical'):
            if(int(kanxi.text) == i+1):
              listNewDic.append(character)
    i=i+1
    
  for character in listNewDic:
    for literal in character.iter('literal'):
      newDic.write(literal.text.encode('utf_8')+'\n')
  newDic.close()
  return

def kanjidic2(inKanji):
  kanji = re.compile(u'^%s' % inKanji, re.UNICODE)
  kanjiHit = []
  #list will be in order: 1: character, 2: KKLD indx, 3: JLPT, 4: Stroke Count
  # 5: Radical, 6: meaning, 7: onyomi, 8: kunyomi, 9: newspaper freq
  kanjidic2 = etree.parse('dictionaries/kanjidic2.xml')
  root = kanjidic2.getroot()
  for character in root:
    for literal in character.iter('literal'):
      if(re.search(kanji, literal.text)):
        kanjiHit.append(character)
        break
        
  return kanjiHit

def kanjidic2kanxi(kanxiNum):
  kanxiRe = re.compile(u'^%s$' % kanxiNum, re.UNICODE)
  kanxiHit = []
  #list will be in order: 1: character, 2: KKLD indx, 3: JLPT, 4: Stroke Count
  # 5: Radical, 6: meaning, 7: onyomi, 8: kunyomi, 9: newspaper freq
  kanjidic2 = etree.parse('dictionaries/kanjidic2.xml')
  root = kanjidic2.getroot()
  for character in root:
    for kanxi in character.iter('rad_value'):
      if(kanxi.get('rad_type') == 'classical'):
        if(re.search(kanxiRe, kanxi.text)):
          kanxiHit.append(character)
          return kanxiHit
  
  return

def radk(inKanji):
  kanji = re.compile(u'^\$ %s' % inKanji, re.UNICODE)
  radical = re.compile(u'^\$', re.UNICODE)
  radkdic = open('dictionaries/radkfile2-utf8', 'r')
  lines = []
  line = radkdic.readline().decode('utf_8')
  
  while line:
    if(re.search(kanji, line)):
      lines.append(line.strip())
      break
    line = radkdic.readline().decode('utf_8')

  radkdic.close()
  return lines

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