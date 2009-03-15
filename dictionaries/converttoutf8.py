#!/usr/bin/python

# converttoutf8.py

import codecs

f = codecs.open('radkfile2', 'rb', encoding='euc_jp')
fnew = codecs.open('radkfile2-utf8', 'wb', encoding='utf_8')
fnew.write(f.read(-1))
f.close()
fnew.close()
