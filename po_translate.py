# -*- coding: utf8 -*-
'''
Created on 2010/4/27

@author: Victor-mortal
'''

import os
import sys
import urllib
import json
import logging
import optparse
import codecs
import htmllib
import time

log = logging.getLogger(__name__)

#from version import __version__

USAGE = """usage: %prog sourcePo destPo sourceLanguage destLanguage
Example: 
    mypo.po output.po zh-TW zh-CN"""

def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

def translate(message_strings, sourceLanguage, destLanguage):
    """ Translate a text
      
      @param message_strings: list of texts to translate
      @param sourceLanguage: the language original text is in
      @param destLanguage: language to translate to
      
    """
    
    query = [
        ('key', 'AIzaSyC50uIaMik-Ib2Gjo1g10VhzpDjtPhc1FM'),
        ('v', '1.0'),
        ('langpair', '%s|%s' % (sourceLanguage, destLanguage))
    ]
    for item in message_strings:
        query.append(('q', item.encode('utf8')))
    sock = urllib.urlopen(
        'https://ajax.googleapis.com/ajax/services/language/translate',
        data=urllib.urlencode(query)
    )
    text = sock.read()
    translations = json.loads(text).get('responseData')
    sock.close()
    results = {}
    for i in range(len(message_strings)):
        k = message_strings[i]
        v = translations[i].get('responseData').get('translatedText')
        results[k] = unescape(v)
    return results
    


def main():
    import polib
    
    logging.basicConfig(level=logging.INFO, 
                        format="%(levelname)s - %(message)s")
    
    parser = optparse.OptionParser(usage=USAGE)
    (_, args) = parser.parse_args()
    
    if len(args) != 4:
        parser.print_usage()
        return
    
    sourceFilePath = args[0]
    destFilePath = args[1]
    sourceLang = args[2]
    destLang = args[3]
    
    log.info('Translate %s (in %s) to %s (in %s)', 
             sourceFilePath, sourceLang, destFilePath, destLang) 
    
    def process_cache(cache):
        msgstrs = [item.msgstr for item in cache]
        results = translate(msgstrs, sourceLang, destLang)
        for item in cache:
            translated = results[item.msgstr]
            if translated is not None:
                log.info('Translated %r to %r', item.msgstr, translated)
                item.msgstr = translated
        
    
    
    po = polib.pofile(sourceFilePath)
    i = 0
    cache = []
    for entry in po:
        if not entry.msgstr.strip():
            entry.msgstr = entry.msgid.strip()
        if not entry.msgstr.strip():
            continue
        if i < 20:
            i = i + 1
            cache.append(entry)
        else:
            process_cache(cache)
            cache = []
            i = 0
            time.sleep(1)
    process_cache(cache)
    
    po.metadata['Translated-By'] = 'po_translator' #' %s' % __version__
    po.save(destFilePath)
    log.info('Done')
    

if __name__ == '__main__':
    main()
