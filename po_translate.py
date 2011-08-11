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

def translate(text, sourceLanguage, destLanguage):
    """Translate a text
    
    @param text: text to translate
    @param sourceLanguage: the language original text is in
    @param destLanguage: language to translate to
    """
    log.debug('Translate %s from %s to %s', text, sourceLanguage, destLanguage)
    query = dict(v='1.0',
                 q=text.encode('utf8'),
                 langpair='%s|%s' % (sourceLanguage, destLanguage))
    file = urllib.urlopen(
        'http://ajax.googleapis.com/ajax/services/language/translate',
        data=urllib.urlencode(query)
    )
    result = file.read()
    file.close()
    jsonResult = json.loads(result)
    if not jsonResult['responseData']:
        return None
    return unescape(jsonResult['responseData']['translatedText'])

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
    
    po = polib.pofile(sourceFilePath)
    for entry in po:
        if not entry.msgstr.strip():
            entry.msgstr = entry.msgid.strip()
        if not entry.msgstr.strip():
            continue
        translated = translate(entry.msgstr, sourceLang, destLang)
        if not translated:
            continue
        log.info('Translate %r to %r', entry.msgstr, translated)
        entry.msgstr = translated
            
    po.metadata['Translated-By'] = 'po_translator' #' %s' % __version__
    po.save(destFilePath)
    log.info('Done')

if __name__ == '__main__':
    main()
