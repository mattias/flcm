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
withSOD = 0
pathToImages = '/home/mattias/cards/'

print 'Parsing dictionaries...'
kanjidic2File = etree.parse('dictionaries/kanjidic2.xml')
jmdicFile = etree.parse('dictionaries/JMdict_e-utf8')
print '...done.'

def makeCards(inKanji):

  #start pull words from jmdic and get 6 example compounds
  jmdicInfo = jmdic(inKanji)
  commonWords = []
  commonWordsTrans = []
  commonWordsHir = []
  for entry in jmdicInfo:
    commonWords.append(entry['keb'])
    commonWordsTrans.append(entry['gloss'][:2])
    commonWordsHir.append(entry['reb'])

  words = 0
  if len(commonWords) > 6:
    words = 6
  else:
    words = len(commonWords)
  makeFront(inKanji, commonWords, words)
  makeBack(inKanji, commonWordsTrans, commonWordsHir, words)
  return

def makeFront(inKanji, commonWords, words):
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
    for kodIndex in character.getiterator('dic_ref'):
      if(kodIndex.get('dr_type') == 'halpern_kkld'):
        kodanshaIndex = kodIndex.text
    for jlptInd in character.getiterator('jlpt'):
      jlptIndex = jlptInd.text
    for sCount in character.getiterator('stroke_count'):
      strokeC = sCount.text
    for frq in character.getiterator('freq'):
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
  except IOError:
    print '... making this card without a SOD image...'
    draw.text((40,180), 'No Stroke Order Diagram Image', font=font, fill=red)
  
  #draw compunds
  font = ImageFont.truetype(fontSanSerif, 18)
  i = 0
  while i < words:
    draw.text((160, 21*(i+1)+10), str(i+1)+'. '+commonWords[i], font=font, fill=blue)
    i = i+1
    
  card.save('cards/front/DK'+kodanshaIndex+'.png')
  return

def makeBack(inKanji, commonWordsTrans, commonWordsHir, words):
  card = Image.new('RGB', cardSize, cardBg)
  draw = ImageDraw.Draw(card)

  #Draw on/kun yomi
  kanjiInfo = kanjidic2(inKanji)
  onyomi = []
  kunyomi = []
  meaning = []
  kodanshaIndex = ''
  for character in kanjiInfo:
    for on in character.getiterator('reading'):
      if(on.get('r_type') == 'ja_on'):
        onyomi.append(on.text)
    for kun in character.getiterator('reading'):
      if(kun.get('r_type') == 'ja_kun'):
        kunyomi.append(kun.text)
    for mean in character.getiterator('meaning'):
      if(not mean.get('m_lang')):
        meaning.append(mean.text)
    for kodIndex in character.getiterator('dic_ref'):
      if(kodIndex.get('dr_type') == 'halpern_kkld'):
        kodanshaIndex = kodIndex.text
  
  font = ImageFont.truetype(fontSanSerif, 18)
  draw.text((20, 170), "; ".join(onyomi[:6]), font=font, fill=blue)
  draw.text((20, 230), "; ".join(kunyomi[:6]), font=font, fill=blue)
  draw.text((20, 195), "; ".join(onyomi[6:12]), font=font, fill=blue)
  draw.text((20, 255), "; ".join(kunyomi[6:12]), font=font, fill=blue)
  font = ImageFont.truetype(fontSmall, 14)
  draw.text((20, 20), " ".join(meaning[0:1]), font=font, fill=orange)
  draw.text((20, 40), " ".join(meaning[1:2]), font=font, fill=orange)
  draw.text((20, 60), " ".join(meaning[2:3]), font=font, fill=orange)
  draw.text((20, 80), " ".join(meaning[3:4]), font=font, fill=orange)
  draw.text((20, 100), " ".join(meaning[4:5]), font=font, fill=orange)
  draw.text((20, 120), " ".join(meaning[5:6]), font=font, fill=orange)
  draw.text((20, 140), " ".join(meaning[6:7]), font=font, fill=orange)

  
  #draw compunds
  font = ImageFont.truetype(fontSmall, 14)
  i = 0
  
  while i < words:
    draw.text((220, 20+(21*(i+1))), str(i+1)+'.', font=font, fill=blue)
    draw.text((240, 20+(21*(i+1))), '('+commonWordsHir[i]+'): '+'; '.join(commonWordsTrans[i][:2]), font=font, fill=blue)
    i = i+1
  
  card.save('cards/back/DK'+kodanshaIndex+'.png')
  return

def jmdic(inKanji):
  listCommon = []
  listUnCommon = []
  lists = []
  listsRet = []
  kanji = re.compile(u'%s' % inKanji, re.UNICODE)
  root = jmdicFile.getroot()
  for entry in root:
    common = 0
    for elem in entry.getiterator('ke_pri'):
      if elem.text == 'ichi1' or elem.text == 'news1' or elem.text == 'spec1' or elem.text == 'gai1':
        common = 1
    if common == 1:
      for keb in entry.getiterator('keb'):
        this = {}
        glossList = []
        if(re.search(kanji, keb.text)):
          this['keb'] = keb.text
          for gloss in entry.getiterator('gloss'):
            glossList.append(gloss.text)
          this['gloss'] = glossList
          for hiragana in entry.getiterator('reb'):
            this['reb'] = hiragana.text
          listCommon.append(this)
    else:
      for keb in entry.getiterator('keb'):
        this = {}
        glossList = []
        if(re.search(kanji, keb.text)):
          this['keb'] = keb.text
          for gloss in entry.getiterator('gloss'):
            glossList.append(gloss.text)
          this['gloss'] = glossList
          for hiragana in entry.getiterator('reb'):
            this['reb'] = hiragana.text
          listUnCommon.append(this)
  
  lists = listCommon
  lists += listUnCommon
  
  [listsRet.append(elem) for elem in lists if elem not in listsRet]
  
  return listsRet

def kanjidic2(inKanji):
  kanji = re.compile(u'^%s' % inKanji, re.UNICODE)
  kanjiHit = []
  stop = 0
  root = kanjidic2File.getroot()
  for character in root:
    for literal in character.getiterator('literal'):
      if(re.search(kanji, literal.text)):
        kanjiHit.append(character)
        stop = 1
    if(stop == 1):
      break
  return kanjiHit

def merge(seq):
  merged = []
  for s in seq:
    for x in s:
      merged.append(x)
  return merged

"""root = kanjidic2File.getroot()
done = 1
ankiImport = open('ankiImport', 'w')

if withSOD == 1:
  totalCards = 1513
else:
  totalCards = 2230
  
for char in root.getiterator('character'):
  writeThis = 0
  for kodIndex in char.getiterator('dic_ref'):
    if(kodIndex.get('dr_type') == 'halpern_kkld'):
      if(withSOD == 1):
        try:
          sod = Image.open(sodPath+'DK'+kodIndex.text+'.png')
          writeThis = 1
        except IOError:
          writeThis = 0
          continue
      else:
        writeThis = 1
      if(writeThis == 1):
        for literal in char.getiterator('literal'):
          print 'Creating DK'+kodIndex.text+'.png... ('+literal.text+')'
          makeCards(literal.text)
          ankiImport.write('<img src="'+pathToImages+'front/DK'+kodIndex.text+'.png" />; <img src="'+pathToImages+'back/DK'+kodIndex.text+'.png" />\n')
          print str(done)+' / '+str(totalCards)+' Done.'
          done += 1
          
ankiImport.close()"""

kanjis = open('kanjis', 'r')

line = kanjis.readline().decode('utf_8')
i = 0
while(line):
  i += 1
  line = kanjis.readline().decode('utf_8')

kanjis.close()

kanjis = open('kanjis', 'r')

line = kanjis.readline().decode('utf_8')

while(line):
  print str(i)+' cards left to make...'
  makeCards(line.strip());
  print line.strip()+' created.'
  i -= 1
  line = kanjis.readline().decode('utf_8')

kanjis.close()