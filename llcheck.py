import subprocess 
import tempfile
import re
import pickle
import fileinput

WORDLIST_PATH = "familia_romana_wordlist.txt"
WWORDS_PATH = "/home/laptop/Downloads/words"
#ALREADY_DEFINED_PATH = "/home/laptop/prog/exodus_book/lexicon_nomacros.tex"
ALREADY_DEFINED_PATH = "/home/laptop/prog/exodus_book/lexicon.tex"

flatten = lambda t: [item for sublist in t for item in sublist]

def demacronize(s):
    s = s.replace("ā", "a")
    s = s.replace("ē", "e")
    s = s.replace("ī", "i")
    s = s.replace("ō", "o")
    s = s.replace("ū", "u")
    return s

def load_lexicon(path):
    def cleanup(s):
        s = s[10:].strip()
        s = s.replace("{","==")
        s = s.replace(":","")
        s = s.replace("}","")
        s = s.split("==")
        return s

    f = open(path)
    lexicon_lines = f.readlines()
    lexicon_lines = map(cleanup, lexicon_lines)
    lexicon_lines = map(lambda l: (demacronize(re.search(r'[a-zāēīōūĀĒĪŌŪ]*', l[0]).group(0)), l[1], l[0]), lexicon_lines)
    ldict = {}
    for l in lexicon_lines:
        if l[0] not in ldict:
            form = get_word_forms(l[0])
            if form != None:
                form = form[0]
            ldict[form] = (l[0], l[1], l[2])
    return ldict

def first(f, l):
    for x in l:
        if f(x):
            return x
    return None

def get_word_forms(s):
    results = subprocess.run(["./words", s], cwd=WWORDS_PATH, stdout=subprocess.PIPE, universal_newlines=True)
    results = results.stdout.split("\n")
    results = filter(lambda line: "[" in line, results)
    results = map(lambda s: s.strip(), results)
    results = list(results)
    if results == []:
        return None
    else:
        return results

def clean_list(words):
    words = map(lambda l: l.strip(), words)
    words = filter(lambda l: len(l) > 0, words)
    words = list(set(words))
    words = map(get_word_forms, words)
    words = filter(lambda r: r != None, words)
    words = flatten(list(words))
    return sorted(words)

def check_word(word_list, word):
    quewords = ["usque"]
    if word[-3:] == "que" and word not in quewords:
        word = word[:-3]
    word = word.replace("æ","ae")
    word = word.replace("Æ", "Ae")
    forms = get_word_forms(word)
    if forms == None:
        return "proper/unknown"
    for f in forms:
        if f in word_list:
            return "yes"
    return "no"

def in_lexicon(lexicon, word):
    forms = get_word_forms(word)
    if forms == None:
        return False
    return forms[0] in lexicon

def trim_text(text):
    text = text.replace(".","")
    text = text.replace(",","")
    text = text.replace(":","")
    text = text.replace(";","")
    text = text.replace("?","")
    text = text.replace("æ","ae")
    return text

def undipth(text):
    return text.lower().replace("æ","ae").replace("ā","a").replace("ū","u").replace("ī","i").replace("ō","o").replace("ē","e").replace("j","i").replace("J","j")

def lexize(text, lexicon, wordlist):
    forms_added = []
    text = text.split()
    for word in text:
        if word[-1] in ".,;":
            wcheck = undipth(word[:-1])
        else:
            wcheck = undipth(word)

        if check_word(wordlist, wcheck) != "no":
            print(word, end=" ")
            continue

        if wcheck.lower() not in ["in", "nōn", "per"] and re.search(r'[a-zA-Z]*', wcheck).group(0) == wcheck:
            forms = get_word_forms(wcheck)
            if forms != None and forms[0] in lexicon:
                dict_form, definition, orig = lexicon[forms[0]]
                if dict_form not in forms_added:
                    forms_added.append(dict_form)
                    mnote = '\\mpp{%s:}{%s}' % (orig, definition)
                    print(mnote + word, end=" ")
                else:
                    print(word, end=" ")
            else:
                if check_word(wordlist, wcheck) == "no":
                    if wcheck not in forms_added:
                        forms_added.append(wcheck)
                        print('\\mpp{????}{????}%s' % word, end=" ")
                    else:
                        print(word, end=" ")
                else:
                    print(word, end=" ")
        else:
            print(word, end=" ")

def main():
    f = open(WORDLIST_PATH, "r")
    words = f.readlines()
    f.close()

    ldict = load_lexicon(ALREADY_DEFINED_PATH)

    #word_list = clean_list(words)
    #pickle.dump(word_list, open("words.p", "wb"))

    word_list = pickle.load(open("words.p", "rb"))

    sentence = " ".join(fileinput.input()).replace("j","i").replace("J","I")
    lexize(sentence, ldict, word_list)
    #sentence = trim_text(sentence)
    #results = []
    #for w in list(set(sentence.split())):
    #    try:
    #        int(w)
    #        continue
    #    except:
    #        res = check_word(word_list, w)
    #        if res == "no":
    #            if in_lexicon(lexicon, w):
    #                w += "*"
    #            results.append(w)
    #results.sort()
    #for r in results:
    #    print(r)


if __name__ == "__main__":
    main()
