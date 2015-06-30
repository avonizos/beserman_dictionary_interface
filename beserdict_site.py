#!/usr/bin/python
# -*- coding: utf-8 -*-

# import time
from lxml import etree
from flask import Flask, request, render_template, session, jsonify
import codecs
import re
import uuid
import os
from transcriptions import convert_input, convert_output

app = Flask(__name__)
app.secret_key = 'k_bXnlu654Q'
sessionData = {}    # session key -> dictionary with the data for current session
dictTree = None
lemmas = {}
corpusTree = None
phrases = []
index_corpus = {}
recently = []


def create_index(fname):
    dict = {}
    res = codecs.open('index.db', 'w', 'utf-8')
    corpusTree = etree.parse(fname)
    documents = corpusTree.xpath(u'/document/interlinear-text/paragraphs/paragraph/phrases/phrase')
    for i in range(len(documents)):
        words = documents[i].xpath(u'words//word/item[@type="txt" and @lang="udm-Latn-RU-fonipa-x-emic"]')
        for word in words:
            if word.xpath(u'string()') not in dict.keys():
                dict[word.xpath(u'string()')] = [i]
            else:
                if i not in dict[word.xpath(u'string()')]:
                    dict[word.xpath(u'string()')].append(i)
    for key in dict:
        res.write(key + u'|')
        for i in range(len(dict[key])):
            if i != len(dict[key]) - 1:
                res.write(str(dict[key][i]) + ',')
            else:
                res.write(str(dict[key][i]) + '\n')
        # print key, u'|', dict[key]
    res.close()
    return res


def find_entry(lemma, trans):
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
    n = 5
    foundExamples = find_examples(lemma, n)
    new_res = convert_output(lemmaSign, trans)
    entry = render_template(u'entry.html', lemmaSign=new_res,
                            homonymNumber=homonymNumber,
                            lemmaStatus=lemmaStatus,
                            psBlocks=psBlocks,
                            foundExamples=foundExamples,
                            )

    return entry


def find_examples(lemma, n):
    global phrases

    # case for verbs
    stem = ''
    if lemma.endswith(u'ənə'):
        stem = lemma[:-3]
    elif lemma.endswith(u'nə'):
        stem = lemma[:-2]
    found_words = []

    if stem != '':
        for word in index_corpus.keys():
            if stem in word:
                found_words.append(word)
    else:
        found_words = [lemma]

    # case for nouns
    if not found_words:
        for word in index_corpus.keys():
            if word.startswith(lemma):
                found_words.append(word)

    # print found_words

    foundPhrases = []
    prettyPhrases = []

    for lemma in found_words:
        if lemma in index_corpus.keys():
            foundIds = index_corpus[lemma]
            for i in foundIds:
                foundPhrases.append(phrases[int(i)])
    i = 1
    for foundPhrase in foundPhrases[:n]:
            wordEls = foundPhrase.xpath(u'words/word/item')
            resultPhrase = u''
            for wordEl in wordEls:
                if resultPhrase != '' and unicode(wordEl.xpath(u'string() ')) not in u'.,':
                    resultPhrase += u' '
                resultPhrase += unicode(wordEl.xpath(u'string()'))
            translationEl = foundPhrase.xpath(u'item[@type="gls" and @lang="ru"]')
            resultPhrase += u' - ' + unicode(translationEl[0].xpath(u'string() '))
            prettyPhrases.append(str(i) + '. ' + resultPhrase)
            i += 1
    return prettyPhrases


def load_corpus(fname):
    global corpusTree, phrases, index_corpus
    corpusTree = etree.parse(fname)
    phrases = corpusTree.xpath(u'/document/interlinear-text/paragraphs/paragraph/phrases/phrase')
    if not os.path.isfile('index.db'):
        print 'Making index...'
        create_index('corpus.xml')
    f = codecs.open('index.db', 'r', 'utf-8')
    find_word = re.compile('([^0-9\|, ]*)|')
    find_ids = re.compile('[0-9]+')
    for line in f:
        word = re.search(find_word, line)
        ids = re.findall(find_ids, line)
        if word is not None and ids is not None:
            index_corpus[word.group(1)] = ids


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

        transEl = lemmaEl.xpath(u'PSBlock/Value/Value.ValTr')
        trans = ''
        if transEl:
            trans = transEl[0].xpath(u'string()')
        # print unicode(lemma)
        lemmas[unicode(lemma)] = trans


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
    except KeyError:
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
    if m is not None:
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
    return render_template(u'index.html', lemmas=sorted(lemmas.keys(), key=lambda s: s.lower()))


@app.route('/_get_entry')
def get_entry():
    # Consider the type of transcription
    lemma = request.args.get('lemma', u'', type=unicode).replace(u"'", u'')
    trans = request.args.get('trans', u'', type=unicode)
    req = convert_input(lemma, trans)
    entry = find_entry(req, trans)
    return jsonify(entryHtml=entry)


def search_rus(req):
    global dictTree
    results = []
    for trans in lemmas.values():
        if trans.startswith(' ' + req) or trans.startswith(req):
            results.append([key for key, value in lemmas.iteritems() if value == trans][0])
    return results


def search_elements(req):
    global dictTree
    results = []
    re_flag = 0
    nomin_flag = 0

    # case for nominalization request with -on ending
    if req.endswith(u'on') and req not in lemmas.keys():
        req = req[:-2] + u'ənə'
        nomin_flag = 1

    # case for nominalization request with -an ending
    if req.endswith(u'an') and req not in lemmas.keys():
        req = req[:-2] + u'anə'
        nomin_flag = 1

    for lemma in lemmas.keys():
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
    return results, nomin_flag


@app.route('/hidden/')
def hidden():
    return render_template(u'index.html', lemmas=sorted(lemmas.keys(), key=lambda s: s.lower()))


@app.route('/handler/', methods=['GET'])
def handler():
    htmls = ''

    divButton = '<button type="button" class="btn btn-block" id="return_all">' \
                '<span class="glyphicon glyphicon-arrow-left" aria-hidden="true"></span> Вернуть все леммы' \
                '</button>'

    req = request.args.get('word')
    lang = request.args.get('lang')

    n = 5
    recentlyHtml = ''

    if len(recently) < n:
        recently.append(req)
    else:
        recently.remove(recently[0])
        recently.append(req)

    for word in recently:
        # will work only with request = lemma cases
        if word in lemmas.keys():
            recentlyHtml += '<p><a href="javascript:void(0);" id="lemma">' + word + '</a></p>'
        else:
            recentlyHtml += '<p>' + word + '</p>'

    if lang is None:
        lang = 'bes'

    if lang == 'bes':
        trans = request.args.get('trans')
        # convert from trans -> dict
        req = convert_input(req, trans)
        results = search_elements(req)[0]

    else:
        trans = ''
        results = search_rus(req)

    if search_elements(req)[1] == 1 and results != []:
        nomin_alert = '<p id="nomin_alert">Слово образовано от:</p>'
        divButton += nomin_alert

    # print results
    if len(results) == 1:
        entry = find_entry(results[0], trans)
        if lang == 'bes':
            new_res = convert_output(results[0], trans)
        else:
            new_res = results[0]
        htmls = '<p><a href="javascript:void(0);" id="lemma">' + new_res + '</a></p>'
        return jsonify(entryAmount = len(results), entries = htmls, entryHtml = entry, divButton = divButton)
    else:
        for result in sorted(results, key=lambda s: s.lower()):
            if lang == 'bes':
                new_res = convert_output(result, trans)
            else:
                new_res = result
            htmlString = '<p><a href="javascript:void(0);" id="lemma">' + new_res + '</a></p>'
            htmls += htmlString

        return jsonify(entryAmount=len(results), entries=htmls,
                       recently=recentlyHtml, divButton=divButton)


def start_server():
    load_dictionary(u'dict.xml')
    load_corpus(u'corpus.xml')
    app.run(host='0.0.0.0', port=2019)
    # app.config['SERVER_NAME'] = '62.64.12.18:5000'
   
if __name__ == u'__main__':
    start_server()