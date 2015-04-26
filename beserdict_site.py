#!/usr/bin/python
# -*- coding: utf-8 -*-

#import time
from lxml import etree
from flask import Flask, url_for, request, render_template, redirect, session, jsonify
#import codecs
import re
import uuid

app = Flask(__name__)
app.secret_key = 'k_bXnlu654Q'
sessionData = {}    # session key -> dictionary with the data for current session
dictTree = None
lemmas = []
corpusTree = None
phrases = []

def find_entry(lemma):
    global phrases
    entryEl = find_element(lemma)
    if entryEl is None:
        return jsonify(entryHtml=u'nonono')
    lemmaSignEl = entryEl.xpath(u'Lemma.LemmaSign')
    lemmaSign = unicode(lemmaSignEl[0].xpath(u'string()'))

    homonymNumber = None
    homonymNumberEl = entryEl.xpath(u'Lemma.HomonymNumber')
    if len(homonymNumberEl) == 1:
        homonymNumber = unicode(homonymNumberEl[0].xpath(u'string()'))

    lemmaStatus = None
    lemmaStatusEl = entryEl.xpath(u'Lemma.Status')
    if len(lemmaStatusEl) == 1:
        lemmaStatus = unicode(lemmaStatusEl[0].xpath(u'string()'))


    psBlocks = []
    psBlockEls = entryEl.xpath(u'PSBlock')
    for psBlockEl in psBlockEls:
        psBlock = {u'psbPS': u'?', u'psbMU': [], u'psNounGram': [], u'idioms': [], u'values': []}
        psBlocks.append(psBlock)
        posEl = psBlockEl.xpath(u'PSBlock.PsbPS')
        if len(posEl) == 1:
            psBlock[u'psbPS'] = unicode(posEl[0].xpath(u'string()'))

        psBlockNounGrams = psBlockEl.xpath(u'PSNounGram')
        for psBlockNounGramEl in psBlockNounGrams:
            psNounGram = {u'oblStem': u''}
            psNounGramEl = psBlockNounGramEl.xpath(u'PSNounGram.OblStem')
            if len(psNounGramEl) == 1:
                psNounGram[u'oblStem'] = unicode(psNounGramEl[0].xpath(u'string()'))
            psBlock[u'psNounGram'].append(psNounGram)


        psBlockMUEls = psBlockEl.xpath(u'PsbMU')
        for psBlockMUEl in psBlockMUEls:
            psbMU = {u'psbMU': u''}
            psbMUEl = psBlockMUEl.xpath(u'PsbMU.PsbMU')
            if len(psbMUEl) == 1:
                psbMU[u'psbMU'] = unicode(psbMUEl[0].xpath(u'string()'))
            psbMU[u'psbMU'] = re.sub(u'(&lt;|&gt;)', u'', psbMU[u'psbMU'])
            psBlock[u'psbMU'].append(psbMU)

        idiomEls = psBlockEl.xpath(u'Idiom')
        for idiomEl in idiomEls:
            idiom = {u'idiomText': u'', u'idiomTr': u'', u'examples': []}
            idiomTextEl = idiomEl.xpath(u'Idiom.IdiomText')
            idiomTrEl = idiomEl.xpath(u'Idiom.IdiomTr')
            if len(idiomTextEl) == 1:
                idiom[u'idiomText'] = unicode(idiomTextEl[0].xpath(u'string()'))
            if len(idiomTrEl) == 1:
                idiom[u'idiomTr'] = unicode(idiomTrEl[0].xpath(u'string()'))
            exampleIdiomEls = idiomEl.xpath(u'Example')
            for exampleEl in exampleIdiomEls:
                example = {u'exGoesToDict': u'', u'exText': u'', u'exTrans': u''}
                exGoesToDictEl = exampleEl.xpath(u'Example.ExGoesToDict')
                exTextEl = exampleEl.xpath(u'Example.ExText')
                exTransEl = exampleEl.xpath(u'Example.ExTrans')
                example[u'exGoesToDict'] = unicode(exGoesToDictEl[0].xpath(u'string()'))
                example[u'exText'] = unicode(exTextEl[0].xpath(u'string()'))
                example[u'exTrans'] = unicode(exTransEl[0].xpath(u'string()'))
                idiom[u'examples'].append(example)
            psBlock[u'idioms'].append(idiom)

        valueEls = psBlockEl.xpath(u'Value')
        for valueEl in valueEls:
            value = {u'valNum': u'', u'valTr': u'', u'valTolk': u'', u'examples': []}
            valNumEl = valueEl.xpath(u'Value.ValNumber')
            valTrEl = valueEl.xpath(u'Value.ValTr')
            valTolkEl = valueEl.xpath(u'Value.ValTolk')
            if len(valTrEl) == 1:
                value[u'valTr'] = unicode(valTrEl[0].xpath(u'string()'))
            if len(valTolkEl) == 1:
                value[u'valTolk'] = unicode(valTolkEl[0].xpath(u'string()'))
            if len(valNumEl) == 1:
                value[u'valNum'] = unicode(valNumEl[0].xpath(u'string()'))

            exampleEls = valueEl.xpath(u'Example')
            for exampleEl in exampleEls:
                example = {u'exGoesToDict': u'', u'exText': u'', u'exTrans': u''}
                exGoesToDictEl = exampleEl.xpath(u'Example.ExGoesToDict')
                exTextEl = exampleEl.xpath(u'Example.ExText')
                exTransEl = exampleEl.xpath(u'Example.ExTrans')
                example[u'exGoesToDict'] = unicode(exGoesToDictEl[0].xpath(u'string()'))
                example[u'exText'] = unicode(exTextEl[0].xpath(u'string()'))
                example[u'exTrans'] = unicode(exTransEl[0].xpath(u'string()'))
                value[u'examples'].append(example)
            psBlock[u'values'].append(value)

    # Searching for examples from the corpus
    foundExamples = find_examples(lemma, 5)

    entry = render_template(u'entry.html', lemmaSign=lemmaSign,
                            homonymNumber=homonymNumber,
                            lemmaStatus=lemmaStatus,
                            psBlocks=psBlocks,
                            foundExamples=foundExamples)
    return entry

def find_examples(lemma, n):
    foundPhrases = []
    prettyPhrases = []
    for phrase in phrases:
        wordEls = phrase.xpath(u'words/word/item')
        for wordEl in wordEls:
            if lemma == unicode(wordEl.xpath(u'string()')):
                foundPhrases.append(phrase)

    for foundPhrase in foundPhrases[:n]:
        wordEls = foundPhrase.xpath(u'words/word/item')
        resultPhrase = u''
        for wordEl in wordEls:
            if resultPhrase != '' and unicode(wordEl.xpath(u'string() ')) not in u'.,':
                resultPhrase += u' '
            resultPhrase += unicode(wordEl.xpath(u'string()'))
        translationEl = foundPhrase.xpath(u'item[@type="gls" and @lang="ru"]')
        resultPhrase += u' - ' + unicode(translationEl[0].xpath(u'string() '))
        prettyPhrases.append(resultPhrase)
    return prettyPhrases

def load_corpus(fname):
    global corpusTree, phrases
    corpusTree = etree.parse(fname)
    phrases = corpusTree.xpath(u'/document/interlinear-text/paragraphs/paragraph/phrases/phrase')

def load_dictionary(fname):
    global dictTree, lemmas
    dictTree = etree.parse(fname)
    lemmaEls = dictTree.xpath(u'/root/Lemma')
    for lemmaEl in lemmaEls:
        lemmaSignEl = lemmaEl.xpath(u'Lemma.LemmaSign')
        if len(lemmaSignEl) != 1:
            continue
        lemma = lemmaSignEl[0].xpath(u'string()')
        if u'[' in unicode(lemma):
            continue
        homonymNumberEl = lemmaEl.xpath(u'Lemma.HomonymNumber')
        if len(homonymNumberEl) == 1:
            lemma += u' (' + homonymNumberEl[0].xpath(u'string()') + u')'
        # print unicode(lemma)
        lemmas.append(unicode(lemma))


def initialize_session():
    global sessionData
    session[u'session_id'] = str(uuid.uuid4())
    sessionData[session[u'session_id']] = {}

    
def get_session_data(fieldName):
    global sessionData
    try:
        dictCurData = sessionData[session[u'session_id']]
        requestedValue = dictCurData[fieldName]
        return requestedValue
    except:
        return None


def set_session_data(fieldName, value):
    global sessionData
    if u'session_id' not in session:
        initialize_session()
    sessionData[session[u'session_id']][fieldName] = value


def in_session(fieldName):
    global sessionData
    if u'session_id' not in session:
        return False
    return fieldName in sessionData[session[u'session_id']]


def find_element(lemma):
    global dictTree
    homonymNum = 0
    m = re.search(u'^(.+) \\(([0-9]+)\\)$', lemma, flags=re.U)
    if m != None:
        lemma = m.group(1)
        homonymNum = int(m.group(2))
    try:
        if homonymNum <= 0:
            entryEl = dictTree.xpath(u'/root/Lemma[Lemma.LemmaSign/text()=\'' +
                                     lemma + u'\']')[0]
        else:
            entryEl = dictTree.xpath(u'/root/Lemma[Lemma.LemmaSign/text()=\'' +
                                     lemma +
                                     u'\' and Lemma.HomonymNumber/text()=\'' +
                                     str(homonymNum) + u'\']')[0]
    except:
        return None
    return entryEl

@app.route('/')
def index():
    global lemmas
    return render_template(u'index.html', lemmas=lemmas)

@app.route('/_get_entry')
def get_entry():
    lemma = request.args.get('lemma', u'', type=unicode).replace(u"'", u'')
    entry = find_entry(lemma)
    return jsonify(entryHtml=entry)

def search_elements(req):
    global dictTree
    results = []
    re_flag = 0
    for lemma in lemmas:
        if lemma.startswith(req):
            results.append(lemma)
        else:
            for symbol in req:
                if symbol in u'[]()|*.^$?+\\//':
                    re_flag = 1
            if re_flag == 1:
                regexp_request = re.search(req, lemma, flags=re.U)
                if regexp_request is not None:
                    results.append(lemma)
    return results

@app.route('/handler/', methods=['GET'])
def handler():
    htmls = ''
    req = request.args.get('word')
    results = search_elements(req)
    divButton = '<button type="button" class="btn btn-block" id="return_all">' \
                '<span class="glyphicon glyphicon-arrow-left" aria-hidden="true"></span> Вернуть все леммы' \
                '</button>'
    #print results
    if len(results) == 1:
        entry = find_entry(results[0])
        htmls = '<p><a href="javascript:void();" id="lemma">' + results[0] + '</a></p>'
        return jsonify(entryAmount = len(results), entries = htmls, entryHtml = entry, divButton = divButton)
    else:
        for result in results:
            htmlString = '<p><a href="javascript:void();" id="lemma">' + result + '</a></p>'
            htmls += htmlString
        return jsonify(entryAmount = len(results), entries = htmls, divButton = divButton)


def start_server():
    load_dictionary(u'dict.xml')
    load_corpus(u'corpus.xml')
    app.run(host='0.0.0.0', port=2019)
    #app.config['SERVER_NAME'] = '62.64.12.18:5000'
   
if __name__ == u'__main__':
    start_server()

