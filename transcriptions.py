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
cyrHard2Soft = {u'а': u'я', u'э': u'е', u'ӥ': u'и', u'о': u'ё', u'у': u'ю'}
rxSoften = re.compile(u'(?<![чӟ])ʼ([аэӥоу])', flags=re.U)
rxNeutral = re.compile(u'(?<=[бвгжкмпрфхцчʼ])([эӥ])', flags=re.U)
rxCJV = re.compile(u'(?<=[бвгджзӟклмнпрстфхцчшщ])й([аэӥоу])', flags=re.U)
rxSh = re.compile(u'ш(?=[ʼяеиёю])', flags=re.U)
rxZh = re.compile(u'ж(?=[ʼяеиёю])', flags=re.U)
rxVJV = re.compile(u'(?<=[аеёиӥоӧөуыэюя])й([аэӥоу])', flags=re.U)
rxExtraSoft = re.compile(u'([дзлнст])ь\\1(?=[ьяеёию])', flags=re.U)


def convert_output(res, trans):
    if trans == 'ural':
        # rules here
        pass

    if trans == 'corpus':
        # rules here
        pass

    if trans == 'cyr':
        letters = []
        for letter in res:
            try:
                letters.append(dic2cyr[letter.lower()])
            except KeyError:
                letters.append(letter)
        res = u''.join(letters)
        res = rxSoften.sub(lambda m: cyrHard2Soft[m.group(1)], res)
        res = rxNeutral.sub(lambda m: cyrHard2Soft[m.group(1)], res)
        res = rxCJV.sub(lambda m: u'ъ' + cyrHard2Soft[m.group(1)], res)
        res = rxSh.sub(u'с', res)
        res = rxZh.sub(u'з', res)
        res = res.replace(u'ӟʼ', u'ӟ')
        res = res.replace(u'чʼ', u'ч')
        res = res.replace(u'ʼ', u'ь')
        res = rxVJV.sub(lambda m: cyrHard2Soft[m.group(1)], res)
        res = rxVJV.sub(lambda m: cyrHard2Soft[m.group(1)], res)
        res = rxExtraSoft.sub(u'\\1\\1', res)

    return res


def convert_input(req, trans):
    new_req = req
    if trans == 'ural':
        # rules here
        pass

    if trans == 'corpus':
        # rules here
        pass

    if trans == 'cyr':
        return new_req
        # for letter in req:
        #     try:
        #         new_letter = cyr_match[letter]
        #     except:
        #         continue
        #     new_req = new_req.replace(letter, new_letter)

    return new_req