# Kur'ân Meali · veri derleyici
# Tanzil.net metinlerini sûre sûre JSON'a böler: veri/001.json … veri/114.json
# Kullanım: python3 kaynak/derle.py   (depo kökünden)
import json, os, re

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = os.path.join(KOK, 'kaynak')
DOSYA = {'a': 'ar.simple.txt', 'd': 'tr.diyanet.txt', 'v': 'tr.vakfi.txt', 'e': 'tr.yazir.txt', 'c': 'ar.jalalayn.txt'}
SECDE = '۩'

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
    json.dump(o, open(os.path.join(KOK, 'veri', '%03d.json' % s), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    sayi.append(n)
print('114 sûre yazıldı;', sum(sayi), 'âyet')

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
t = t.replace('/*SURELER*/', json.dumps(SURE, ensure_ascii=False, separators=(',', ':')))
t = t.replace('<!--ALTCUBUK-->', open(os.path.join(K, 'altcubuk.html'), encoding='utf-8').read().strip())
assert '/*AMIRI*/' not in t and '/*SURELER*/' not in t and '<!--ALTCUBUK-->' not in t
open(os.path.join(KOK, 'index.html'), 'w', encoding='utf-8').write(t)
print('index.html yazıldı:', len(t)//1024, 'KB')
