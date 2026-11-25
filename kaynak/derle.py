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
for i, (k, m) in enumerate(SOZ):  # temel sözlük: 1-7. seviye
    KEL.append({'k': k, 'w': bicim[k].most_common(1)[0][0], 'm': m, 'f': say[k], 'lv': min(7, i * 7 // N + 1), 'ex': ilk[k][:3], 's': sorted(sur[k])})
# Nadir kelimeler (8-10. seviye): kelime anlamı yazılmış sûrelerden, Kur'an'da en çok 3 kez geçen biçimler.
# Biçim, baştaki و/ف/ال ve sondaki zamir atılarak sayılır; anlam o âyetteki bağlamsal anlamdır.
def hs(w): return HAR.sub('', w).replace('ٱ', 'ا')  # hemze yazımı korunur (إمرا ≠ أمرا)
say2 = collections.Counter(); sur2 = collections.defaultdict(set)
for s_ in range(1, 115):
    for a_, t in T['a'][s_].items():
        for w in t.split(' '):
            if not isaret(w): say2[hs(w)] += 1; sur2[hs(w)].add(s_)
def oz(k):
    for p_ in ('وال', 'فال', 'بال', 'كال', 'لل', 'ال'):
        if k.startswith(p_) and len(k) - len(p_) >= 3: return k[len(p_):]
    if k[:1] in 'وف' and len(k) >= 4 and say2[k[1:]]: k = k[1:]  # و/ف ancak kalan kısım tek başına da geçiyorsa atılır (فريا kalır)
    for e in ('كما', 'هما', 'هم', 'كم', 'ها', 'نا', 'ني', 'ه', 'ك'):
        if k.endswith(e) and len(k) - len(e) >= 3: return k[:-len(e)]
    return k
osay = collections.Counter(); osur = collections.defaultdict(set)
for k, c in say2.items():
    osay[oz(k)] += c; osur[oz(k)] |= sur2[k]
temel = {oz(k) for k, m in SOZ} | {k for k, m in SOZ} | {oz(hs(w)) for k, m in SOZ for w in bicim[k]}
nad = {}
for s_ in range(1, 115):
    kd = os.path.join(K, 'kelime', '%03d.txt' % s_)
    if not os.path.exists(kd): continue
    o_ = json.load(open(os.path.join(KOK, 'veri', '%03d.json' % s_), encoding='utf-8'))
    for a_, m_ in enumerate(o_['k']):
        if not m_: continue
        ws = [w for w in o_['a'][a_].split(' ') if not isaret(w)]
        for n_, (w, m) in enumerate(zip(ws, m_)):
            k = oz(hs(w)); m = m.strip()
            if len(k) < 3 or osay[k] > 3 or k in temel or k in nad: continue
            if not m or m[0] in '-(' or m[0].isupper() or m[0].isdigit(): continue  # özel isim, hurûf-ı mukattaa, edat
            nad[k] = {'k': k, 'w': w, 'm': m, 'f': osay[k], 'lv': {1: 10, 2: 9}.get(osay[k], 8), 'ex': [s_, a_ + 1, n_], 's': sorted(osur[k]), 'n': 1}
KEL += list(nad.values())
json.dump(KEL, open(os.path.join(KOK, 'veri', 'kelimeler.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('kelime testi:', N, 'temel +', len(nad), 'nadir kelime')


# ---- İ'râb testi: kaynak/irab.txt → veri/irab.json ----
IR = []
# Şık havuzları sablon.html'deki TERIM'den okunur; doğru terim ve h terimleri havuzda olmalı
_tm = re.search(r'var TERIM=\{(.*?)\};', open(os.path.join(K, 'sablon.html'), encoding='utf-8').read(), re.S).group(1)
IRTUR = {k: re.findall(r"'([^']+)'", v) for k, v in re.findall(r"(\w+):\[(.*?)\]", _tm, re.S)}
for sat in open(os.path.join(K, 'irab.txt'), encoding='utf-8'):
    sat = sat.rstrip('\n')
    if not sat or sat.startswith('#'): continue
    p_ = sat.split('|')
    s_, a_, n_, t_, lv_, tur_, ac_ = p_[:7]
    h_ = [x.strip() for x in re.split('[,;]', p_[7]) if x.strip()] if len(p_) > 7 else []  # şık yapılmayacak terimler (ihtilaf)
    s_, a_ = int(s_), int(a_)
    t = T['a'][s_][a_]
    if s_ not in (1, 9) and a_ == 1: t = ' '.join(t.split(' ')[4:])
    ws = [w for w in t.split(' ') if not isaret(w)]
    m_ = None
    if re.fullmatch(r'\d+-\d+', n_): n_, m_ = map(int, n_.split('-'))  # kelime aralığı (cümle soruları)
    elif n_.isdigit(): n_ = int(n_)
    else:  # kelimenin kendisi yazılmış (harekesiz); aynı kelime birden çoksa 'كلمة#2'
        k_, _, sira_ = n_.partition('#'); bul_ = [i for i, w in enumerate(ws) if sade(w) == sade(k_)]
        assert len(bul_) >= int(sira_ or 1), ('irab kelimesi bulunamadı', s_, a_, n_)
        n_ = bul_[int(sira_ or 1) - 1]
    assert n_ < len(ws) and (m_ is None or n_ <= m_ < len(ws)), ('irab kelime sırası', s_, a_, n_, m_)
    assert tur_ in IRTUR, ('irab tür', s_, a_, tur_)
    assert t_ in IRTUR[tur_], ('irab terimi havuzda yok', s_, a_, t_)
    assert all(x in IRTUR[tur_] for x in h_), ('irab h terimi havuzda yok', s_, a_, h_)
    assert 1 <= int(lv_) <= 6, ('irab seviye', s_, a_)
    w_ = ' '.join(ws[n_:(m_ if m_ is not None else n_) + 1])
    IR.append({'s': s_, 'a': a_, 'n': n_, 'w': w_, 't': t_, 'lv': int(lv_), 'tur': tur_, 'x': ac_, **({'m': m_} if m_ is not None else {}), **({'h': h_} if h_ else {})})
json.dump(IR, open(os.path.join(KOK, 'veri', 'irab.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print("i'râb testi:", len(IR), 'soru')

# ---- Belâgat testi: kaynak/belagat.txt → veri/belagat.json ----
BL = []
for sat in open(os.path.join(K, 'belagat.txt'), encoding='utf-8'):
    sat = sat.rstrip('\n')
    if not sat or sat.startswith('#'): continue
    s_, a_, r_, t_, lv_, h_, ac_ = sat.split('|', 6)
    s_, a_ = int(s_), int(a_); b_, e_ = [int(x) for x in r_.split('-')]
    t = T['a'][s_][a_]
    if s_ not in (1, 9) and a_ == 1: t = ' '.join(t.split(' ')[4:])
    ws = [w for w in t.split(' ') if not isaret(w)]
    assert 0 <= b_ <= e_ < len(ws), ('belâgat kelime aralığı', s_, a_, r_)
    BL.append({'s': s_, 'a': a_, 'b': b_, 'e': e_, 'w': ' '.join(ws[b_:e_ + 1]), 't': t_, 'lv': int(lv_), 'h': [x for x in h_.split(';') if x], 'x': ac_})
json.dump(BL, open(os.path.join(KOK, 'veri', 'belagat.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print("belâgat testi:", len(BL), 'soru')
# Belâgat notları okuma ekranında da gösterilir: veri/NNN.json → 'bl': âyet başına [[başlangıç, bitiş, terim, açıklama], …] ya da 0
blS = collections.defaultdict(dict)
for x in BL: blS[x['s']].setdefault(x['a'], []).append([x['b'], x['e'], x['t'], x['x']])
for s_, d_ in blS.items():
    f_ = os.path.join(KOK, 'veri', '%03d.json' % s_); o_ = json.load(open(f_, encoding='utf-8'))
    o_['bl'] = [d_.get(i + 1, 0) for i in range(len(o_['a']))]
    json.dump(o_, open(f_, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

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
