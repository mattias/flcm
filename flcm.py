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
blue = (21,38,195)
orange = (211,100,59)
red = (255,0,0)
cardBg = (255,255,255)
cardSize = (800, 300)
withSOD = 1

def makeCards(inKanji):

  #start pull words from jmdic and get 6 example compounds
  kanji = re.compile(u'%s' % inKanji, re.UNICODE)
  jmdicInfo = jmdic(inKanji)
  commonWords = []
  commonWordsTrans = []
  commonWordsChoice = []
  commonWordsHir = []
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
              temp = []
              for gloss in entry.iter('gloss'):
                temp.append(gloss.text)
              commonWordsTrans.append(temp)
              temp = []
              for hiragana in entry.iter('reb'):
                temp.append(hiragana.text)
              commonWordsHir.append(temp)
      
  i = 0
  if(len(commonWords) > 6):
    words = 6
    """while i < words:
      rand = random.randint(0, len(commonWords)-1)
      for rands in commonWordsChoice:
        duplicate = 0
        if(rands == rand):
          duplicate = 1
      
      while duplicate == 1:
        rand = random.randint(0, len(commonWords)-1)"""
    while i < words:
      commonWordsChoice.append(i)
      i=i+1
  else:
    words = len(commonWords)
    while i < words:
      commonWordsChoice.append(i)
      i=i+1

  makeFront(inKanji, commonWordsChoice, commonWords)
  makeBack(inKanji, commonWordsChoice, commonWordsTrans, commonWordsHir)
  return

def makeFront(inKanji, commonWordsChoice, commonWords):
  kanji = re.compile(u'%s' % inKanji, re.UNICODE)
  card = Image.new('RGB', cardSize, cardBg)
  draw = ImageDraw.Draw(card)
    
  # Draw the kanji on to the front card
  font = ImageFont.truetype(fontSerif, 102)
  draw.text((30, 30), inKanji, font=font, fill=orange)
    
  # Get various field infos and draw it to the card
  kanjiInfo = kanjidic2(inKanji)
  kodanshaIndex = ''
  jlptIndex = ''
  strokeC = ''
  freq = ''
  for character in kanjiInfo:
    for kodIndex in character.iter('dic_ref'):
      if(kodIndex.get('dr_type') == 'halpern_kkld'):
        kodanshaIndex = kodIndex.text
    for jlptInd in character.iter('jlpt'):
      jlptIndex = jlptInd.text
    for sCount in character.iter('stroke_count'):
      strokeC = sCount.text
    for frq in character.iter('freq'):
      freq = frq.text
  
  font = ImageFont.truetype(fontSmall, 18)
  draw.text((625, 20), 'KKLD Index: '+kodanshaIndex, font=font, fill=blue)
  font = ImageFont.truetype(fontSmall, 12)
  draw.text((730, 45), 'JLPT'+jlptIndex, font=font, fill=blue)
  draw.text((40, 140), 'Stroke Count: '+strokeC, font=font, fill=blue)
  draw.text((40, 10), 'Frequency: '+freq, font=font, fill=blue)

  #open SOD and put it at bottom of card
  try:
    sod = Image.open(sodPath+'DK'+kodanshaIndex+'.png')
    card.paste(sod, (40, 180))
  except IOError, e:
    print e
    draw.text((40,180), 'No Stroke Order Diagram Image', font=font, fill=red)
  
  #draw compunds
  font = ImageFont.truetype(fontSanSerif, 18)
  i = 0
  while i < len(commonWordsChoice):
    draw.text((160, 21*(i+1)+10), str(i+1)+'. '+commonWords[commonWordsChoice[i]], font=font, fill=blue)
    i = i+1
    
  card.save('cards/front/DK'+kodanshaIndex+'.png')
  return

def makeBack(inKanji, commonWordsChoice, commonWordsTrans, commonWordsHir):
  card = Image.new('RGB', cardSize, cardBg)
  draw = ImageDraw.Draw(card)

  #Draw on/kun yomi
  kanjiInfo = kanjidic2(inKanji)
  onyomi = []
  kunyomi = []
  meaning = []
  kodanshaIndex = ''
  for character in kanjiInfo:
    for on in character.iter('reading'):
      if(on.get('r_type') == 'ja_on'):
        onyomi.append(on.text)
    for kun in character.iter('reading'):
      if(kun.get('r_type') == 'ja_kun'):
        kunyomi.append(kun.text)
    for mean in character.iter('meaning'):
      if(not mean.get('m_lang')):
        meaning.append(mean.text)
    for kodIndex in character.iter('dic_ref'):
      if(kodIndex.get('dr_type') == 'halpern_kkld'):
        kodanshaIndex = kodIndex.text
  
  font = ImageFont.truetype(fontSanSerif, 18)
  draw.text((20, 170), "; ".join(onyomi[:6]), font=font, fill=blue)
  draw.text((20, 230), "; ".join(kunyomi[:6]), font=font, fill=blue)
  draw.text((20, 195), "; ".join(onyomi[6:12]), font=font, fill=blue)
  draw.text((20, 255), "; ".join(kunyomi[6:12]), font=font, fill=blue)
  font = ImageFont.truetype(fontSmall, 14)
  draw.text((20, 60), " ".join(meaning[:1]), font=font, fill=orange)

  
  #draw compunds
  font = ImageFont.truetype(fontSmall, 14)
  i = 0
  while i < len(commonWordsChoice):
    draw.text((220, 20+(21*(i+1))), str(i+1)+'.', font=font, fill=blue)
    draw.text((240, 20+(21*(i+1))), '('+'; '.join(commonWordsHir[commonWordsChoice[i]][:1])+'): '+'; '.join(commonWordsTrans[commonWordsChoice[i]][:1]) , font=font, fill=blue)
    i = i+1
  
  card.save('cards/back/DK'+kodanshaIndex+'.png')
  return

def jmdic(inKanji):
  lists = []
  kanji = re.compile(u'%s' % inKanji, re.UNICODE)
  jmdic = etree.parse('dictionaries/JMdict_e-utf8')
  root = jmdic.getroot()
  i = 0
  for entry in root:
    if( i < 6 ):
      for keb in entry.iter('keb'):
        if(re.search(kanji, keb.text)):
          lists.append(entry)
          i = i+1
    else:
      break
  return lists

def kanjidic2(inKanji):
  kanji = re.compile(u'^%s' % inKanji, re.UNICODE)
  kanjiHit = []
  kanjidic2 = etree.parse('dictionaries/kanjidic2.xml')
  root = kanjidic2.getroot()
  stop = 0
  
  for character in root:
    for literal in character.iter('literal'):
      if(re.search(kanji, literal.text)):
        kanjiHit.append(character)
        stop = 1
    if(stop == 1):
      break
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


kanjis = etree.parse('dictionaries/kanjidic2.xml')
root = kanjis.getroot()

for char in root.iter('character'):
  writeThis = 0
  for kodIndex in char.iter('dic_ref'):
    if(kodIndex.get('dr_type') == 'halpern_kkld'):
      if(withSOD == 1):
        try:
          sod = Image.open(sodPath+'DK'+kodIndex.text+'.png')
          writeThis = 1
        except IOError:
          writeThis = 0
          continue
    if(writeThis == 1):
      for literal in char.iter('literal'):
        print 'Creating DK'+kodIndex.text+'.png... ('+literal.text+')'
        makeCards(literal.text)
        print 'Done.'