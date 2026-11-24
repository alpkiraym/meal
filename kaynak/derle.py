# Kur'ân Meali · veri derleyici
# Tanzil.net metinlerini sûre sûre JSON'a böler: veri/001.json … veri/114.json
# Kullanım: python3 kaynak/derle.py   (depo kökünden)
import json, os, re

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = os.path.join(KOK, 'kaynak')
DOSYA = {'a': 'ar.simple.txt', 'd': 'tr.diyanet.txt', 'v': 'tr.vakfi.txt', 'e': 'tr.yazir.txt', 'c': 'ar.jalalayn.txt'}
SECDE = '۩'

def isaret(w):  # yalnızca vakf/secde/hizb işaretinden oluşan parça
    return all('\u06d6' <= c <= '\u06ed' for c in w)

def oku(ad):
    v = {}
    for sat in open(os.path.join(K, ad), encoding='utf-8'):
        m = re.match(r'^(\d+)\|(\d+)\|(.*)$', sat.rstrip('\n'))
        if m:
            v.setdefault(int(m[1]), {})[int(m[2])] = m[3].strip()
    return v

T = {k: oku(f) for k, f in DOSYA.items()}
os.makedirs(os.path.join(KOK, 'veri'), exist_ok=True)
sayi = []
for s in range(1, 115):
    n = len(T['a'][s])
    for k in T:
        assert len(T[k][s]) == n, (k, s)
    o = {k: [T[k][s][i] for i in range(1, n + 1)] for k in T}
    # Besmele ilk âyetin başında geliyor (Fâtiha ve Tevbe hariç): ayrı başlık olarak gösterilir.
    if s not in (1, 9):
        k = o['a'][0].split(' ')
        assert ''.join(c for c in k[0] if not '\u064b' <= c <= '\u0652') == 'بسم' and len(k) > 4, s
        o['a'][0] = ' '.join(k[4:])
    o['s'] = [i + 1 for i, x in enumerate(o['a']) if SECDE in x]  # secde âyetleri
    # Kelime anlamları (varsa): kaynak/kelime/NNN.txt · âyet|anlam|anlam|…  (vakf işaretleri kelime sayılmaz)
    kd = os.path.join(K, 'kelime', '%03d.txt' % s)
    if os.path.exists(kd):
        km = [None] * n
        for sat in open(kd, encoding='utf-8'):
            sat = sat.rstrip('\n')
            if not sat or sat.startswith('#'): continue
            p = sat.split('|'); a = int(p[0]); m = p[1:]
            say = len([w for w in o['a'][a - 1].split(' ') if not isaret(w)])
            assert len(m) == say, ('kelime sayısı tutmuyor', s, a, len(m), say)
            km[a - 1] = m
        o['k'] = km
    json.dump(o, open(os.path.join(KOK, 'veri', '%03d.json' % s), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    sayi.append(n)
print('114 sûre yazıldı;', sum(sayi), 'âyet')

# ---- Kelime testi sözlüğü: kaynak/sozluk.txt → veri/kelimeler.json ----
import collections
HAR = re.compile('[\u064b-\u0652\u0670\u0640\u06d6-\u06ed]')
def sade(w):
    w = HAR.sub('', w)
    for x in 'أإآٱ': w = w.replace(x, 'ا')
    return w
say = collections.Counter(); bicim = collections.defaultdict(collections.Counter); ilk = {}; sur = collections.defaultdict(set)
for s_ in range(1, 115):
    for a_, t in T['a'][s_].items():
        if s_ not in (1, 9) and a_ == 1:
            k = t.split(' '); t = ' '.join(k[4:])  # besmele ayrı
        n_ = 0; uz = len([w for w in t.split(' ') if not isaret(w)])
        for w in t.split(' '):
            if isaret(w): continue
            k = sade(w); say[k] += 1; bicim[k][w] += 1; sur[k].add(s_)
            if k not in ilk or uz < ilk[k][3]: ilk[k] = [s_, a_, n_, uz]  # en kısa âyetteki örnek (âyet sorusu için)
            n_ += 1
# Fâtiha 1 besmelesi de sayılsın (yukarıda Fâtiha'da ayrılmadı)
SOZ = []
for sat in open(os.path.join(K, 'sozluk.txt'), encoding='utf-8'):
    sat = sat.strip()
    if not sat or sat.startswith('#'): continue
    k, m = sat.split('|', 1)
    assert k in say, ('sözlükte metinde olmayan kelime', k)
    SOZ.append([k, m])
assert len({k for k, m in SOZ}) == len(SOZ), 'sözlükte tekrar var'
SOZ.sort(key=lambda x: -say[x[0]])  # seviye sıklığa göre: en sık geçen = 1. seviye
N = len(SOZ); KEL = []
for i, (k, m) in enumerate(SOZ):
    KEL.append({'k': k, 'w': bicim[k].most_common(1)[0][0], 'm': m, 'f': say[k], 'lv': min(10, i * 10 // N + 1), 'ex': ilk[k][:3], 's': sorted(sur[k])})
json.dump(KEL, open(os.path.join(KOK, 'veri', 'kelimeler.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('kelime testi:', N, 'kelime;', 'seviye başına', N // 10)


# ---- İ'râb testi: kaynak/irab.txt → veri/irab.json ----
IR = []
for sat in open(os.path.join(K, 'irab.txt'), encoding='utf-8'):
    sat = sat.rstrip('\n')
    if not sat or sat.startswith('#'): continue
    s_, a_, n_, t_, lv_, tur_, ac_ = sat.split('|', 6)
    s_, a_, n_ = int(s_), int(a_), int(n_)
    t = T['a'][s_][a_]
    if s_ not in (1, 9) and a_ == 1: t = ' '.join(t.split(' ')[4:])
    ws = [w for w in t.split(' ') if not isaret(w)]
    assert n_ < len(ws), ('irab kelime sırası', s_, a_, n_)
    IR.append({'s': s_, 'a': a_, 'n': n_, 'w': ws[n_], 't': t_, 'lv': int(lv_), 'tur': tur_, 'x': ac_})
json.dump(IR, open(os.path.join(KOK, 'veri', 'irab.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print("i'râb testi:", len(IR), 'soru')

# ---- index.html ----
import base64
ADLAR = """Fâtiha|الفاتحة
Bakara|البقرة
Âl-i İmrân|آل عمران
Nisâ|النساء
Mâide|المائدة
En'âm|الأنعام
A'râf|الأعراف
Enfâl|الأنفال
Tevbe|التوبة
Yûnus|يونس
Hûd|هود
Yûsuf|يوسف
Ra'd|الرعد
İbrâhîm|إبراهيم
Hicr|الحجر
Nahl|النحل
İsrâ|الإسراء
Kehf|الكهف
Meryem|مريم
Tâhâ|طه
Enbiyâ|الأنبياء
Hac|الحج
Mü'minûn|المؤمنون
Nûr|النور
Furkân|الفرقان
Şuarâ|الشعراء
Neml|النمل
Kasas|القصص
Ankebût|العنكبوت
Rûm|الروم
Lokmân|لقمان
Secde|السجدة
Ahzâb|الأحزاب
Sebe'|سبإ
Fâtır|فاطر
Yâsîn|يس
Sâffât|الصافات
Sâd|ص
Zümer|الزمر
Mü'min|غافر
Fussılet|فصلت
Şûrâ|الشورى
Zuhruf|الزخرف
Duhân|الدخان
Câsiye|الجاثية
Ahkâf|الأحقاف
Muhammed|محمد
Fetih|الفتح
Hucurât|الحجرات
Kâf|ق
Zâriyât|الذاريات
Tûr|الطور
Necm|النجم
Kamer|القمر
Rahmân|الرحمن
Vâkıa|الواقعة
Hadîd|الحديد
Mücâdele|المجادلة
Haşr|الحشر
Mümtehine|الممتحنة
Saf|الصف
Cuma|الجمعة
Münâfikûn|المنافقون
Teğâbün|التغابن
Talâk|الطلاق
Tahrîm|التحريم
Mülk|الملك
Kalem|القلم
Hâkka|الحاقة
Meâric|المعارج
Nûh|نوح
Cin|الجن
Müzzemmil|المزمل
Müddessir|المدثر
Kıyâme|القيامة
İnsân|الإنسان
Mürselât|المرسلات
Nebe'|النبإ
Nâziât|النازعات
Abese|عبس
Tekvîr|التكوير
İnfitâr|الانفطار
Mutaffifîn|المطففين
İnşikâk|الانشقاق
Bürûc|البروج
Târık|الطارق
A'lâ|الأعلى
Ğâşiye|الغاشية
Fecr|الفجر
Beled|البلد
Şems|الشمس
Leyl|الليل
Duhâ|الضحى
İnşirâh|الشرح
Tîn|التين
Alak|العلق
Kadr|القدر
Beyyine|البينة
Zilzâl|الزلزلة
Âdiyât|العاديات
Kâria|القارعة
Tekâsür|التكاثر
Asr|العصر
Hümeze|الهمزة
Fîl|الفيل
Kureyş|قريش
Mâûn|الماعون
Kevser|الكوثر
Kâfirûn|الكافرون
Nasr|النصر
Tebbet|المسد
İhlâs|الإخلاص
Felak|الفلق
Nâs|الناس""".split('\n')
assert len(ADLAR) == 114
SURE = [[a.split('|')[0], a.split('|')[1], n] for a, n in zip(ADLAR, sayi)]
t = open(os.path.join(K, 'sablon.html'), encoding='utf-8').read()
t = t.replace('/*AMIRI*/', base64.b64encode(open(os.path.join(K, 'amiri.woff'), 'rb').read()).decode())
KELSURE = sorted(int(f[:3]) for f in os.listdir(os.path.join(K, 'kelime')) if re.match(r'^\d{3}\.txt$', f))
t = t.replace('/*KELSURE*/', json.dumps(KELSURE))
t = t.replace('/*SURELER*/', json.dumps(SURE, ensure_ascii=False, separators=(',', ':')))
t = t.replace('<!--BILDIR-->', open(os.path.join(K, 'bildir.html'), encoding='utf-8').read().strip())
t = t.replace('<!--ALTCUBUK-->', open(os.path.join(K, 'altcubuk.html'), encoding='utf-8').read().strip())
assert '/*KELSURE*/' not in t
assert '/*AMIRI*/' not in t and '/*SURELER*/' not in t and '<!--ALTCUBUK-->' not in t and '<!--BILDIR-->' not in t
open(os.path.join(KOK, 'index.html'), 'w', encoding='utf-8').write(t)
print('index.html yazıldı:', len(t)//1024, 'KB')
