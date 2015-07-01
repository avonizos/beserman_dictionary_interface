# coding=utf-8
import re

dic2cyr = {u'a': u'а', u'b': u'б', u'v': u'в',
           u'g': u'г', u'd': u'д', u'e': u'э',
           u'ž': u'ж', u'š': u'ш', u'ɤ': u'ӧ',
           u'ə': u'ө', u'ǯ': u'ӟ', u'č': u'ч',
           u'z': u'з', u'i': u'ӥ', u'j': u'й', u'k': u'к',
           u'l': u'л', u'm': u'м', u'n': u'н',
           u'o': u'о', u'p': u'п', u'r': u'р',
           u's': u'с', u't': u'т', u'u': u'у',
           u'c': u'ц', u'w': u'у', u'x': u'х',
           u'y': u'ы', u'f': u'ф', u'ɨ': u'ы'}
cyr2dic = {v: k for k, v in dic2cyr.iteritems()}
cyr2dic.update({u'я': u'ʼa', u'е': u'ʼe', u'и': u'ʼi',
                u'ё': u'ʼo', u'ю': u'ʼu', u'ь': u'ʼ', u'ы': u'ɨ', u'у': u'u'})
cyrHard2Soft = {u'а': u'я', u'э': u'е', u'ӥ': u'и', u'о': u'ё', u'у': u'ю'}
rxSoften = re.compile(u'(?<![чӟ])ʼ([аэӥоу])', flags=re.U)
rxCyrSoften = re.compile(u'([čǯ])(?!ʼ)', flags=re.U)
rxCyrMultSoften = re.compile(u'ʼ{2,}', flags=re.U)
rxNeutral1 = re.compile(u'(?<=[бвгжкмпрфхцчʼ])([эӥ])', flags=re.U)
rxNeutral2 = re.compile(u'([бвгжкмпрфхцчʼаоэӥуяёеию]|^)(ӥ)', flags=re.U)
rxCyrNeutral = re.compile(u'(?<=[bvgzkmprfxcw])ʼ', flags=re.U)
rxCJV = re.compile(u'(?<=[бвгджзӟклмнпрстфхцчшщ])й([аэӥоу])', flags=re.U)
rxSh = re.compile(u'ш(?=[ʼяёюие])', flags=re.U)
rxZh = re.compile(u'ж(?=[ʼяёюие])', flags=re.U)
rxVJV = re.compile(u'(?<=[аеёиӥоӧөуыэюя])й([аэӥоу])', flags=re.U)
rxJV = re.compile(u'^й([аэӥоу])', flags=re.U)
rxCyrVJV = re.compile(u'([aeiouɨəɤ])ʼ([aeouɨəɤ])', flags=re.U)
rxCyrVSoft = re.compile(u'([aeiouɨəɤ]|^)ʼ', flags=re.U)
rxCyrJV = re.compile(u'^ʼ([aeouɨəɤ])', flags=re.U)
rxExtraSoft = re.compile(u'([дзлнст])ь\\1(?=[ьяеёию])', flags=re.U)
rxCyrExtraSoft = re.compile(u'([džlnšt])\\1(?=ʼ)', flags=re.U)
rxCyrW = re.compile(u'(^|к)у(?=[аоэи])', flags=re.U)


def convert_output(res, trans):
    if trans == 'ural':
        # rules here
        pass

    if trans == 'corpus':
        res = res.replace(u'ə', u'ə̑')
        res = res.replace(u'ɤ', u'ə')
        res = res.replace(u'ɨ', u'y')
        res = res.replace(u'ʼ', u'’')

    if trans == 'cyr':
        letters = []
        for letter in res:
            try:
                letters.append(dic2cyr[letter.lower()])
            except KeyError:
                letters.append(letter)
        res = u''.join(letters)
        res = rxSoften.sub(lambda m: cyrHard2Soft[m.group(1)], res)
        res = rxSh.sub(u'с', res)
        res = rxZh.sub(u'з', res)
        res = rxNeutral1.sub(lambda m: cyrHard2Soft[m.group(1)], res)
        res = rxNeutral2.sub(u'\\1и', res)
        res = rxCJV.sub(lambda m: u'ъ' + cyrHard2Soft[m.group(1)], res)
        res = res.replace(u'ӟʼ', u'ӟ')
        res = res.replace(u'чʼ', u'ч')
        res = res.replace(u'ʼ', u'ь')
        res = rxVJV.sub(lambda m: cyrHard2Soft[m.group(1)], res)
        res = rxVJV.sub(lambda m: cyrHard2Soft[m.group(1)], res)
        res = rxJV.sub(lambda m: cyrHard2Soft[m.group(1)], res)
        res = rxExtraSoft.sub(u'\\1\\1', res)

    return res


def convert_input(req, trans):
    if trans == 'ural':
        # rules here
        pass

    if trans == 'corpus':
        req = re.sub(u'ə(?!̑)', u'ɤ', req)
        req = req.replace(u'ə̑', u'ə')
        req = req.replace(u'y', u'ɨ')
        req = req.replace(u'’', u'ʼ')

    if trans == 'cyr':
        req = rxCyrW.sub(u'\\1w', req)
        req = req.replace(u'жи', u'жӥ')
        req = req.replace(u'ши', u'шӥ')
        req = req.replace(u'же', u'жэ')
        req = req.replace(u'ше', u'шэ')
        letters = []
        for letter in req:
            try:
                letters.append(cyr2dic[letter.lower()])
            except KeyError:
                letters.append(letter)
        req = u''.join(letters)
        req = rxCyrVJV.sub(u'\\1j\\2', req)
        req = rxCyrJV.sub(u'j\\1', req)
        req = req.replace(u'ъʼ', u'j')
        req = req.replace(u'sʼ', u'šʼ')
        req = req.replace(u'zʼ', u'žʼ')
        req = rxCyrSoften.sub(u'\\1ʼ', req)
        req = rxCyrNeutral.sub(u'', req)
        req = rxCyrExtraSoft.sub(u'\\1ʼ\\1', req)
        req = req.replace(u'sšʼ', u'šʼšʼ')
        req = req.replace(u'zžʼ', u'žʼžʼ')
        req = rxCyrMultSoften.sub(u'ʼ', req)
        req = rxCyrVSoft.sub(u'\\1', req)
        return req
        # for letter in req:
        #     try:
        #         new_letter = cyr_match[letter]
        #     except:
        #         continue
        #     new_req = new_req.replace(letter, new_letter)

    return req

if __name__ == u'__main__':
    import random
    for i in range(100):
        word = u''.join(random.choice(list(u'abcdeəfgiɨjklmnoprstuvzšžɤ') +
                                      [u'dʼ', u'lʼ', u'nʼ', u'tʼ', u'šʼ', u'žʼ', u'ǯʼ', u'čʼ'])
                        for j in range(random.randint(2, 13)))
        wordNew = convert_input(convert_output(word, 'cyr'), 'cyr')
        if wordNew != word:
            print word, u'->', convert_output(word, 'cyr'), u'->', wordNew