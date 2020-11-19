import subprocess 
import tempfile
import re
import pickle

WORDLIST_PATH = "familia_romana_wordlist.txt"
WWORDS_PATH = "/home/laptop/Downloads/words"
ALREADY_DEFINED_PATH = "/home/laptop/prog/exodus_book/lexicon_nomacros.tex"

flatten = lambda t: [item for sublist in t for item in sublist]

def load_lexicon(path):
    f = open(path)
    lexicon_lines = f.readlines()
    lexicon_lines = map(lambda l: l[10:].strip(), lexicon_lines)
    lexicon_lines = map(lambda l: l.replace("{","=="), lexicon_lines)
    lexicon_lines = map(lambda l: l.replace(":",""), lexicon_lines)
    lexicon_lines = map(lambda l: l.replace("}",""), lexicon_lines)
    lexicon_lines = map(lambda l: l.split("=="), lexicon_lines)
    lexicon_lines = map(lambda l: re.search(r'[a-z]*', l[0]).group(0), lexicon_lines)
    return list(lexicon_lines)

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
    for f in forms:
        if f in word_list:
            return True
    return False

def in_lexicon(lexicon, word):
    forms = get_word_forms(word)
    for f in forms:
        if f in lexicon:
            return True
        else:
            if word == "comedere":
                print("%s not in lexicon" % f)
                exit()
    return False

def main():
    f = open(WORDLIST_PATH, "r")
    words = f.readlines()
    f.close()

    lexicon = load_lexicon(ALREADY_DEFINED_PATH)
    lexicon = map(lambda w: get_word_forms(w), lexicon)
    lexicon = filter(lambda w: w != None, lexicon)
    lexicon = map(lambda w: w[0], lexicon)
    lexicon = list(lexicon)
    lexicon.sort()

    word_list = clean_list(words)
    pfile = open("pickled_words.pkl", "wb")
    pickle.dump(pfile, word_list)
    pfile.close()
    exit()
    sentence = "10 Ait Moyses : Obsecro, Domine, non sum eloquens ab heri et nudiustertius : et ex quo locutus es ad servum tuum, impeditioris et tardioris linguæ sum. 11 Dixit Dominus ad eum : Quis fecit os hominis ? aut quis fabricatus est mutum et surdum, videntem et cæcum ? nonne ego ? 12 Perge, igitur, et ego ero in ore tuo : doceboque te quid loquaris. 13 At ille : Obsecro, inquit, Domine, mitte quem missurus es. 14 Iratus Dominus in Moysen, ait : Aaron frater tuus Levites, scio quod eloquens sit : ecce ipse egreditur in occursum tuum, vidensque te lætabitur corde. 15 Loquere ad eum, et pone verba mea in ore ejus : et ego ero in ore tuo, et in ore illius, et ostendam vobis quid agere debeatis. 16 Ipse loquetur pro te ad populum, et erit os tuum : tu autem eris ei in his quæ ad Deum pertinent. 17 Virgam quoque hanc sume in manu tua, in qua facturus es signa. 18 Abiit Moyses, et reversus est ad Jethro socerum suum, dixitque ei : Vadam et revertar ad fratres meos in Ægyptum, ut videam si adhuc vivant. Cui ait Jethro : Vade in pace.  "
    sentence = sentence.replace(".","")
    sentence = sentence.replace(",","")
    sentence = sentence.replace(":","")
    sentence = sentence.replace("?","")
    results = []
    for w in list(set(sentence.split())):
        try:
            int(w)
            continue
        except:
            res = check_word(word_list, w)
            if res == False:
                if in_lexicon(lexicon, w):
                    w += "*"
                results.append(w)
    results.sort()
    for r in results:
        print(r)



main()
