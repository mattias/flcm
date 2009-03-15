#!/usr/bin/python
# -*- coding: utf-8 -*-

# flcm.py
import re, os, sys
import random
import Image, ImageDraw, ImageFont
try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  raise SystemExit("You need lxml to run this app!")


sodPath = 'dictionaries/sod-utf8/'
fontSerif = '/usr/share/fonts/truetype/kochi/kochi-mincho.ttf'
fontSanSerif = '/usr/share/fonts/truetype/kochi/kochi-gothic.ttf'
fontSmall = '/usr/share/fonts/truetype/freefont/FreeSans.ttf'

def makeCards(inKanji):
  f = 0
  makeFront(inKanji)
  print str(f+1)+' : Front Done'
  b = 0
  makeBack(inKanji)
  print str(b+1)+' : Back Done'
  f = f+1
  b = b+1
  return

def makeFront(inKanji):
  kanji = re.compile(u'%s' % inKanji, re.UNICODE)
  card = Image.new('RGB', (500, 300), (255,255,255))
  draw = ImageDraw.Draw(card)
    
  # Draw the kanji on to the front card
  font = ImageFont.truetype(fontSerif, 102)
  draw.text((30, 30), inKanji, font=font, fill=(69,174,235))
    
  # Get various field infos and draw it to the card
  kanjiInfo = kanjidic2(inKanji)
  kodanshaIndex = ''
  jlptIndex = ''
  strokeC = ''
  radIndex = ''
  freq = ''
  for character in kanjiInfo:
    for kodIndex in character.iter('dic_ref'):
      if(kodIndex.get('dr_type') == 'halpern_kkld'):
        kodanshaIndex = kodIndex.text
    for jlptInd in character.iter('jlpt'):
      jlptIndex = jlptInd.text
    for sCount in character.iter('stroke_count'):
      strokeC = sCount.text
    for radInd in character.iter('rad_value'):
      if(radInd.get('rad_type') == 'classical'):
        radIndex = radInd.text
    for frq in character.iter('freq'):
      freq = frq.text
  
  font = ImageFont.truetype(fontSmall, 18)
  draw.text((325, 20), 'KKLD Index: '+kodanshaIndex, font=font, fill=(69,174,235))
  font = ImageFont.truetype(fontSmall, 12)
  draw.text((430, 45), 'JLPT'+jlptIndex, font=font, fill=(69,174,235))
  draw.text((40, 140), 'Stroke Count: '+strokeC, font=font, fill=(69,174,235))
  draw.text((40, 10), 'Frequency: '+freq, font=font, fill=(69,174,235))

  #open SOD and put it at bottom of card
  try:
    sod = Image.open(sodPath+'DK'+kodanshaIndex+'.png')
    card.paste(sod, (40, 180))
  except IOError, e:
    print e
    draw.text((40,180), 'No Stroke Order Diagram Image', font=font, fill=(255,0,0))
  
  #start pull words from jmdic and get 6 example compounds
  jmdicInfo = jmdic(inKanji)
  commonWords = []
  commonWordsChoice = []
  duplicate = 0

  for entry in jmdicInfo:
    for elem in entry.iter('ke_pri'):
      if((elem.text == 'ichi1' or elem.text == 'news1' or elem.text == 'spec1' or elem.text == 'gai1')):
        for tag in entry.iter('keb'):
          if(re.search(kanji, tag.text)):
            for words in commonWords:
              duplicate = 0
              if(words == tag.text):
                duplicate = 1
            if(duplicate != 1):
              commonWords.append(tag.text)
  
  font = ImageFont.truetype(fontSanSerif, 18)
  i = 0
  if(len(commonWords) > 6):
    words = 6
    while i < words:
      rand = random.randint(0, len(commonWords)-1)
      for rands in commonWordsChoice:
        duplicate = 0
        if(rands == rand):
          duplicate = 1
      
      while duplicate == 1:
        rand = random.randint(0, len(commonWords)-1)
      commonWordsChoice.append(rand)
      draw.text((160, 21*(i+1)+10), str(i+1)+'. '+commonWords[rand], font=font, fill=(69,174,235))
      i=i+1
  else:
    words = len(commonWords)
    while i < words:
      draw.text((160, 21*(i+1)+10), str(i+1)+'. '+commonWords[i], font=font, fill=(69,174,235))
      i=i+1
  #get that radical!
  radInfo = radfile(radIndex)
  if(len(radInfo) > 0):
    draw.text((340, 150), 'Radical: ', font=font, fill=(69,174,235))
    font = ImageFont.truetype(fontSanSerif, 52)
    draw.text((420, 115), radInfo, font=font, fill=(69,174,235))
    
  card.save('cards/testfront.png')
  return

def makeBack(inKanji):
  card = Image.new('RGB', (500, 300), (255,255,255))
  draw = ImageDraw.Draw(card)
  kanjiInfo = kanjidic(inKanji)
  on = []
  kun = []
  english = []
  #for li in kanjiInfo:
      #on.append([x for x in li.split(' ') if is_on(x[0])][0])
  #print on
  card.save('cards/testback.png')
  return

def jmdic(inKanji):
  lists = []
  kanji = re.compile(u'%s' % inKanji, re.UNICODE)
  jmdic = etree.parse('dictionaries/JMdict_e-utf8')
  root = jmdic.getroot()
  for entry in root:
    for keb in entry.iter('keb'):
      if(re.search(kanji, keb.text)):
        lists.append(entry)
        
  return lists

def kanjidic2(inKanji):
  kanji = re.compile(u'^%s' % inKanji, re.UNICODE)
  kanjiHit = []
  kanjidic2 = etree.parse('dictionaries/kanjidic2.xml')
  root = kanjidic2.getroot()
  for character in root:
    for literal in character.iter('literal'):
      if(re.search(kanji, literal.text)):
        kanjiHit.append(character)
        return kanjiHit
  
  return kanjiHit

def kanjidic(inKanji):
  kanji = re.compile(u'^%s' % inKanji, re.UNICODE)
  kanjidic = open('dictionaries/kanjidic-utf8', 'r')
  lines = []
  line = kanjidic.readline().decode('utf_8')

  while line:
    if(re.search(kanji, line)):
      lines.append(line.strip())
      break
      
    line = kanjidic.readline().decode('utf_8')
      
  
  kanjidic.close()
  return lines

def radfile(radNum):
  raddic = open('dictionaries/classicalRad', 'r')
  radHit = ''
  radList = []
  line = raddic.readline().decode('utf_8')
  while line:
    radList.append(line.strip())
    
    line = raddic.readline().decode('utf_8')
    
  radHit = radList[int(radNum)-1]
  
  raddic.close()
  return radHit

def radkfile(inKanji, radNum):
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

def is_latin(s):
  return all(lambda x: 31 < ord(x) < 127, s)

def is_katakana(reading):
  return bool (reading) and chr(u"ァ") <= chr(reading[0]) <= chr(u"ヺ")

def is_on(reading):
  return is_katakana(reading)

def is_kun(reading):
  return not (is_latin(reading) or is_on(reading))

inKanji = u'車'.strip()
i = 0

makeCards(inKanji)