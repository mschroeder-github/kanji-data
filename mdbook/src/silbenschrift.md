<audio id="audioPlayer"></audio>
<script>
    const audioElement = document.getElementById('audioPlayer');

    function loadAndPlay(button, src) {
        audioElement.src = src;
        audioElement.load();
        audioElement.play();
    }
</script>

# Japanische Silbenschrift & Aussprache

Wie Eingangs erwähnt gibt es zwei Silbenschriften, die durch ihren recht logischen Aufbau leicht zu lernen sind.
Doch es benötigt zuerst noch eine Umschrift.

## Transkription

Eine [Transkription](https://de.wikipedia.org/wiki/Transkription_(Schreibung)) ist eine Umschrift:
Es wird ein Schriftsystem (Skript) in ein anderes übertragen (*trans*feriert).
Diese neue Umschrift hilft dem Lernenden zu verstehen, wie die eigentliche Schrift ausgesprochen wird.
Dadurch soll es dem Nicht-Muttersprachler eine halbwegs richtige Aussprache von Wörtern ermöglichen.

Das Umschreiben wäre so, wie wenn man einen Japaner bittet, alle japanischen Silben vorzulesen.
Eine Deutscher soll das Gehörte in Kleinbuchstaben aufschreiben.
Wenn der Deutsche das Aufgeschriebene liest, klingt es sehr ähnlich zur Aussprache des Japaners.

Diesen Vorgang hat bestimmt [James Hepburn](https://de.wikipedia.org/wiki/James_Curtis_Hepburn) auch durchlaufen, um sein erstes Japanisch-Englisch Wörterbuch 1867 herausgeben zu können.
Er war aber Amerikaner, weshalb er möglicherweise die japanischen Laute anders wahrgenommen und umgeschrieben hat, als es ein Deutscher tun würde.
Neben seinem [Hepburn-Transkriptionsystem](https://de.wikipedia.org/wiki/Hepburn-System) gibt es noch [weitere](https://de.wikipedia.org/wiki/Japanische_Transkription): das Yale-System, das Kunrei-System und das Nippon-System.

Da das Hepburn-System am nächsten an der deutschen Aussprache liegt, sollte man mit diesem lernen.
Doch es gibt ein paar Besonderheiten, die zu beachten sind.

Die Umschrift ist als Hilfsmittel gedacht und sollte nicht als eigene Schrift gelernt und verwendet werden.
Sobald man durch diese Hilfsschrift die Laute der Silben erlernt hat, sollte man sich immer in den echten japanischen Schriften bewegen.
Aus diesem Grund wird Transkriptionstext in diesem Kapitel folgendermaßen dargestellt: *japanisch*<span class="ts">|umschrift</span>.
Der senkrechte Strich (|) soll als Trenner zwischen japanischer Schrift und Umschrift dienen.
Japanische Begriffe werden so per <span class="ts">|umschrift</span> geschrieben, wobei die linke Seite leer bleibt, sollten die japanischen Zeichen noch nicht eingeführt sein.

## Silbenschrift & Aussprache

<table style="border-width: 0px !important; width: 100%">
    <tr>
        <td style="width: 30%; vertical-align: top;">
            <br/>
            <img src="kana.png">
        </td>
        <td style="vertical-align: top">

**Erste Spalte:**
Tatsächlich sind auch die Zeichen der ersten Silbenschriften Abwandlungen von chinesischen Zeichen (blau), die für die Aussprache genutzt werden.
Über die chinesische Grasschrift (rot) sind so Zeichen für die erste Silbenschrift entstanden (schwarz).

**Zweite Spalte:**
Auch die Zeichen der zweiten Silbenschriften sind aus chinesischen Zeichen (blau) durch Entnahme von Elementen (rot) und Vereinfachungen entstanden (schwarz).

Da die Zeichen eigentlich mit Pinsel gemalt werden, haben Linien variierende Anfänge, Breiten und Enden.
Die letzten Zeichen haben vereinfachte Formen, die man üblicherweise in der Computer-Schriftart findet: あ und ア.
        </td>
    </tr>
</table>

Die beiden Silbenschriften werden <span class="ts">|kana</span> genannt.

> Merksatz: Das Gesprochene wird in einer Schrift **kana**lisiert.

Die [erste Silbenschrift](https://de.wikipedia.org/wiki/Hiragana) ist <span class="ts">|hiragana</span> (linke Seite im Bild) und die [zweite Silbenschrift](https://de.wikipedia.org/wiki/Katakana) ist <span class="ts">|katakana</span> (rechte Seite im Bild).

> Merksatz: <span class="ts">|hiragana</span> wird **hier** in Japan geschrieben, mit <span class="ts">|katakana</span> werden Fremdworte **kata**logisiert.

Nicht wundern: <span class="ts">|hira**ga**na</span> meint <span class="ts">|**ka**na</span>, wird nur zwecks besseren Aussprechens von Japanern mit *g* statt *k* geschrieben und ausgesprochen.

Im Folgenden werden die beide Silbenschriften mit je 46 Grundsilben (Monographen) als Tabelle vorgestellt.
Darauf folgen noch Zusammensetzungen (Digraphen, je 21), zwei angebrachte kleine Zeichen, die die Aussprache verändern (Diakritika, je 25) sowie eine Kombination daraus (je 12).

### Grundsilben (Monographen)

<!--
immer aussprache mitnehmen
einfache aussprache mit farben: weiß, gelb (warn), rot (danger)
-->

Silben werden aus Konsonanten (im Zeilenkopf, links) und den bekannten Vokalen (im Spaltenkopf, oben) gebildet.
In den Zellen steht links das <span class="ts">|hiragana</span> Zeichen und rechts das <span class="ts">|katakana</span> Zeichen.
Bestimmte Kombinationen bei **y** und und **w** werden nicht mehr verwendet, daher sind sie ausgelassen.
Das **n** bildet eine eigene Silbe, was zuerst ungewohnt für deutsche Muttersprachler ist.

<table class="centered-table">
    <thead>
        <tr>
            <th></th>
            <th>a</th>
            <th>i</th>
            <th>u</th>
            <th>e</th>
            <th>o</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <th></th>
            <td>
                あ<span class="ts">|a</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/a.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ア<span class="ts">|a</span>
            </td>
            <td>
                い<span class="ts">|i</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/i.wav')">
                    <i class="fas fa-play"></i>
                </button>
                イ<span class="ts">|i</span>
            </td>
            <td>
                う<span class="ts">|u</span>
                <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/u.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ウ<span class="ts">|u</span>
            </td>
            <td>
                え<span class="ts">|e</span>
                <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/e.wav')">
                    <i class="fas fa-play"></i>
                </button>
                エ<span class="ts">|e</span>
            </td>
            <td>
                お<span class="ts">|o</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/o.wav')">
                    <i class="fas fa-play"></i>
                </button>
                オ<span class="ts">|o</span>
            </td>
        </tr>
        <tr>
            <th>k</th>
            <td>
                か<span class="ts">|ka</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ka.wav')">
                    <i class="fas fa-play"></i>
                </button>
                カ<span class="ts">|ka</span>
            </td>
            <td>
                き<span class="ts">|ki</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ki.wav')">
                    <i class="fas fa-play"></i>
                </button>
                キ<span class="ts">|ki</span>
            </td>
            <td>
                く<span class="ts">|ku</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ku.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ク<span class="ts">|ku</span>
            </td>
            <td>
                け<span class="ts">|ke</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ke.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ケ<span class="ts">|ke</span>
            </td>
            <td>
                こ<span class="ts">|ko</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ko.wav')">
                    <i class="fas fa-play"></i>
                </button>
                コ<span class="ts">|ko</span>
            </td>
        </tr>
        <tr>
            <th>s</th>
            <td>
                さ<span class="ts">|sa</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/sa.wav')">
                    <i class="fas fa-play"></i>
                </button>
                サ<span class="ts">|sa</span>
            </td>
            <td>
                し<span class="ts">|shi</span>
                <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/shi.wav')">
                    <i class="fas fa-play"></i>
                </button>
                シ<span class="ts">|shi</span>
            </td>
            <td>
                す<span class="ts">|su</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/su.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ス<span class="ts">|su</span>
            </td>
            <td>
                せ<span class="ts">|se</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/se.wav')">
                    <i class="fas fa-play"></i>
                </button>
                セ<span class="ts">|se</span>
            </td>
            <td>
                そ<span class="ts">|so</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/so.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ソ<span class="ts">|so</span>
            </td>
        </tr>
        <tr>
            <th>t</th>
            <td>
                た<span class="ts">|ta</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ta.wav')">
                    <i class="fas fa-play"></i>
                </button>
                タ<span class="ts">|ta</span>
            </td>
            <td>
                ち<span class="ts">|chi</span>
                <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/chi.wav')">
                    <i class="fas fa-play"></i>
                </button>
                チ<span class="ts">|chi</span>
            </td>
            <td>
                つ<span class="ts">|tsu</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/tsu.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ツ<span class="ts">|tsu</span>
            </td>
            <td>
                て<span class="ts">|te</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/te.wav')">
                    <i class="fas fa-play"></i>
                </button>
                テ<span class="ts">|te</span>
            </td>
            <td>
                と<span class="ts">|to</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/to.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ト<span class="ts">|to</span>
            </td>
        </tr>
        <tr>
            <th>n</th>
            <td>
                な<span class="ts">|na</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/na.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ナ<span class="ts">|na</span>
            </td>
            <td>
                に<span class="ts">|ni</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ni.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ニ<span class="ts">|ni</span>
            </td>
            <td>
                ぬ<span class="ts">|nu</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/nu.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ヌ<span class="ts">|nu</span>
            </td>
            <td>
                ね<span class="ts">|ne</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ne.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ネ<span class="ts">|ne</span>
            </td>
            <td>
                の<span class="ts">|no</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/no.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ノ<span class="ts">|no</span>
            </td>
        </tr>
        <tr>
            <th>h</th>
            <td>
                は<span class="ts">|ha</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ha.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ハ<span class="ts">|ha</span>
            </td>
            <td>
                ひ<span class="ts">|hi</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/hi.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ヒ<span class="ts">|hi</span>
            </td>
            <td>
                ふ<span class="ts">|fu</span>
                <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/hu.wav')">
                    <i class="fas fa-play"></i>
                </button>
                フ<span class="ts">|fu</span>
            </td>
            <td>
                へ<span class="ts">|he</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/he.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ヘ<span class="ts">|he</span>
            </td>
            <td>
                ほ<span class="ts">|ho</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ho.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ホ<span class="ts">|ho</span>
            </td>
        </tr>
        <tr>
            <th>m</th>
            <td>
                ま<span class="ts">|ma</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ma.wav')">
                    <i class="fas fa-play"></i>
                </button>
                マ<span class="ts">|ma</span>
            </td>
            <td>
                み<span class="ts">|mi</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/mi.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ミ<span class="ts">|mi</span>
            </td>
            <td>
                む<span class="ts">|mu</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/mu.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ム<span class="ts">|mu</span>
            </td>
            <td>
                め<span class="ts">|me</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/me.wav')">
                    <i class="fas fa-play"></i>
                </button>
                メ<span class="ts">|me</span>
            </td>
            <td>
                も<span class="ts">|mo</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/mo.wav')">
                    <i class="fas fa-play"></i>
                </button>
                モ<span class="ts">|mo</span>
            </td>
        </tr>
        <tr>
            <th>y</th>
            <td>
                や<span class="ts">|ya</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ya.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ヤ<span class="ts">|ya</span>
            </td>
            <td>
                </td>
            <td>
                ゆ<span class="ts">|yu</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/yu.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ユ<span class="ts">|yu</span>
            </td>
            <td>
                </td>
            <td>
                よ<span class="ts">|yo</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/yo.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ヨ<span class="ts">|yo</span>
            </td>
        </tr>
        <tr>
            <th>r</th>
            <td>
                ら<span class="ts">|ra</span>
                <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/ra.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ラ<span class="ts">|ra</span>
            </td>
            <td>
                り<span class="ts">|ri</span>
                <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/ri.wav')">
                    <i class="fas fa-play"></i>
                </button>
                リ<span class="ts">|ri</span>
            </td>
            <td>
                る<span class="ts">|ru</span>
                <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/ru.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ル<span class="ts">|ru</span>
            </td>
            <td>
                れ<span class="ts">|re</span>
                <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/re.wav')">
                    <i class="fas fa-play"></i>
                </button>
                レ<span class="ts">|re</span>
            </td>
            <td>
                ろ<span class="ts">|ro</span>
                <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/ro.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ロ<span class="ts">|ro</span>
            </td>
        </tr>
        <tr>
            <th>w</th>
            <td>
                わ<span class="ts">|wa</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/wa.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ワ<span class="ts">|wa</span>
            </td>
            <td>
            </td>
            <td>
            </td>
            <td>
            </td>
            <td>
                を<span class="ts">|wo</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/o.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ヲ<span class="ts">|wo</span>
            </td>
        </tr>
        <tr>
            <th>*</th>
            <td colspan="5">
                ん<span class="ts">|n</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/n.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ン<span class="ts">|n</span>
            </td>
        </tr>
    </tbody>
</table>


In der Mitte jeder Tabellenzelle befindet sich eine Schaltfläche, um die Aussprache abzuspielen.
Der Lernende sollte sich Zeit nehmen, die Laute mehrmals anzuhören.
Wer tiefer absteigen möchte, kann das [Internationalen Phonetischen Alphabet](https://de.wikipedia.org/wiki/Liste_der_IPA-Zeichen) konsultieren und über [Wiktionary](https://de.wiktionary.org/wiki/%E3%81%86) (z.B. von う<span class="ts">|u</span>) die Aussprache überprüfen.
Im Folgenden sind ein paar Besonderheiten herausgestellt (die Schaltflächen sind hervorgehoben).

* Das う<span class="ts">|u</span> ist ein ungerundetes Gegenstück zum deutschen *u*, was in Richtung *ü* geht.
* Das え<span class="ts">|e</span> klingt wie *ä*.
* Bei し<span class="ts">|shi</span> ist es nicht *sie* sondern *schi*.
* Bei ち<span class="ts">|chi</span> ist es nicht *tie* oder *chi* sondern *tschi*.
* Bei ふ<span class="ts">|fu</span> ist es zwischen [*hu* und *fu*](https://de.wikipedia.org/wiki/Stimmloser_bilabialer_Frikativ).
* Bei den **r** Lauten ist es ein Zungenschlag erzeugtes *r*, was sich wie ein *l* anhört, aber kein *l* ist.

<!-- TODO: ist wo nun o oder wo ausgesprochen? -->

#### Ähnlich aussehende <span class="ts">|hiragana</span> Zeichen

Hier ein paar Merksätze, um recht ähnlich aussehende Silben besser auseinander halten zu können.

> Der Unterschied zwischen め<span class="ts">|me</span> und ぬ<span class="ts">|nu</span> ist die geschwungene **Nu**del.

> Der Unterschied zwischen ろ<span class="ts">|ro</span> und る<span class="ts">|ru</span> ist wieder die **ru**nde Nudel.

> Der Unterschied zwischen ま<span class="ts">|ma</span> und ほ<span class="ts">|ho</span> ist der extra **ho**chkantstrich (|).

> Der Unterschied zwischen は<span class="ts">|ha</span> und ほ<span class="ts">|ho</span> ist der obere **ho**rizontalstrich (&ndash;).

> Der Unterschied zwischen わ<span class="ts">|wa</span> und ね<span class="ts">|ne</span> ist ei**ne** Schleife.

#### Ähnlich aussende <span class="ts">|katakana</span> Zeichen

Merksatz, um die ノ<span class="ts">|no</span> ähnlichen Silben nebeneinander zu sehen.
<table>
    <tr>
        <td>
            no,
        </td>
        <td>
            so
        </td>
        <td>
            <span class="gray">'</span>n
        </td>
        <td>
            shi
        </td>
        <td>
            t<span class="gray">su</span>
        </td>
    </tr>
    <tr>
        <td>ノ</td>
        <td>ソ</td>
        <td>ン</td>
        <td>シ</td>
        <td>ツ</td>
    </tr>
</table>

Merksatz, um die フ<span class="ts">|fu</span> ähnlichen Silben nebeneinander zu sehen.
<table>
    <tr>
        <td>fu<span class="gray">**,</span></td>
        <td>ra<span class="gray">te</span></td>
        <td>wo</td>
        <td><span class="gray">und</span></td>
        <td>wa<span class="gray">-</span></td>
        <td><span class="gray">-r</span>u<span class="gray">m</span></td>
    </tr>
    <tr>
        <td>フ</td>
        <td>ラ</td>
        <td>ヲ</td>
        <td></td>
        <td>ワ</td>
        <td>ウ</td>
    </tr>
</table>

> Der Unterschied zwischen ク<span class="ts">|ku</span> und ケ<span class="ts">|ke</span> ist der Ha**ke**n.

<!--
> Der Unterschied zwischen マ<span class="ts">|ma</span> ヌ<span class="ts">|nu</span> ist

> Der Unterschied zwischen ナ<span class="ts">|na</span> チ<span class="ts">|chi</span> ist
-->

### Zusammensetzungen (Digraphen)

<!-- Digraphen ya yu yo -->

Das や<span class="ts">|ya</span>, ゆ<span class="ts">|yu</span> und よ<span class="ts">|yo</span> kann kleingeschrieben werden: ゃ<span class="ts" style="font-size: smaller;">|ya</span>, ゅ<span class="ts" style="font-size: smaller;">|yu</span> und ょ<span class="ts" style="font-size: smaller;">|yo</span>.
Zusammen mit den Konsonanten (außer **w**) entstehen neue Zusammensetzungen, die eigenständige Silben ergeben.

<table class="centered-table">
  <thead>
    <tr>
      <th>
      </th>
      <th>ya</th>
      <th>yu</th>
      <th>yo</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>k</th>
      <td> きゃ<span class="ts">|kya</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/kya.wav')">
        <i class="fas fa-play">
        </i>
        </button> キャ<span class="ts">|kya</span>
      </td>
      <td> きゅ<span class="ts">|kyu</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/kyu.wav')">
        <i class="fas fa-play">
        </i>
        </button> キュ<span class="ts">|kyu</span>
      </td>
      <td> きょ<span class="ts">|kyo</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/kyo.wav')">
        <i class="fas fa-play">
        </i>
        </button> キョ<span class="ts">|kyo</span>
      </td>
    </tr>
    <tr>
      <th>s</th>
      <td> しゃ<span class="ts">|sha</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/sha.wav')">
        <i class="fas fa-play">
        </i>
        </button> シャ<span class="ts">|sha</span>
      </td>
      <td> しゅ<span class="ts">|shu</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/shu.wav')">
        <i class="fas fa-play">
        </i>
        </button> シュ<span class="ts">|shu</span>
      </td>
      <td> しょ<span class="ts">|sho</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/sho.wav')">
        <i class="fas fa-play">
        </i>
        </button> ショ<span class="ts">|sho</span>
      </td>
    </tr>
    <tr>
      <th>t</th>
      <td> ちゃ<span class="ts">|cha</span>
      <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/cha.wav')">
        <i class="fas fa-play">
        </i>
        </button> チャ<span class="ts">|cha</span>
      </td>
      <td> ちゅ<span class="ts">|chu</span>
      <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/chu.wav')">
        <i class="fas fa-play">
        </i>
        </button> チュ<span class="ts">|chu</span>
      </td>
      <td> ちょ<span class="ts">|cho</span>
      <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/cho.wav')">
        <i class="fas fa-play">
        </i>
        </button> チョ<span class="ts">|cho</span>
      </td>
    </tr>
    <tr>
      <th>n</th>
      <td> にゃ<span class="ts">|nya</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/nya.wav')">
        <i class="fas fa-play">
        </i>
        </button> ニャ<span class="ts">|nya</span>
      </td>
      <td> にゅ<span class="ts">|nyu</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/nyu.wav')">
        <i class="fas fa-play">
        </i>
        </button> ニュ<span class="ts">|nyu</span>
      </td>
      <td> にょ<span class="ts">|nyo</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/nyo.wav')">
        <i class="fas fa-play">
        </i>
        </button> ニョ<span class="ts">|nyo</span>
      </td>
    </tr>
    <tr>
      <th>h</th>
      <td> ひゃ<span class="ts">|hya</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/hya.wav')">
        <i class="fas fa-play">
        </i>
        </button> ヒャ<span class="ts">|hya</span>
      </td>
      <td> ひゅ<span class="ts">|hyu</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/hyu.wav')">
        <i class="fas fa-play">
        </i>
        </button> ヒュ<span class="ts">|hyu</span>
      </td>
      <td> ひょ<span class="ts">|hyo</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/hyo.wav')">
        <i class="fas fa-play">
        </i>
        </button> ヒョ<span class="ts">|hyo</span>
      </td>
    </tr>
    <tr>
      <th>m</th>
      <td> みゃ<span class="ts">|mya</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/mya.wav')">
        <i class="fas fa-play">
        </i>
        </button> ミャ<span class="ts">|mya</span>
      </td>
      <td> みゅ<span class="ts">|myu</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/myu.wav')">
        <i class="fas fa-play">
        </i>
        </button> ミュ<span class="ts">|myu</span>
      </td>
      <td> みょ<span class="ts">|myo</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/myo.wav')">
        <i class="fas fa-play">
        </i>
        </button> ミョ<span class="ts">|myo</span>
      </td>
    </tr>
    <tr>
      <th>r</th>
      <td> りゃ<span class="ts">|rya</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/rya.wav')">
        <i class="fas fa-play">
        </i>
        </button> リャ<span class="ts">|rya</span>
      </td>
      <td> りゅ<span class="ts">|ryu</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ryu.wav')">
        <i class="fas fa-play">
        </i>
        </button> リュ<span class="ts">|ryu</span>
      </td>
      <td> りょ<span class="ts">|ryo</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ryo.wav')">
        <i class="fas fa-play">
        </i>
        </button> リョ<span class="ts">|ryo</span>
      </td>
    </tr>
  </tbody>
</table>

Bei der Aussprache ist zu beachten:
* Bei der **t** Reihe z.B. ちゃ<span class="ts">|cha</span> wie ein *tscha* aussprechen, nicht wie *Charme* und nicht wie *Charisma*.

### Angebrachte kleine Zeichen (Diakritika)

Ein [diakritisches Zeichen](https://de.wikipedia.org/wiki/Diakritisches_Zeichen) sind angebrachte kleinen Zeichen, die eine abweichende Aussprache anzeigen.
Im deutschen Alphabet kennen wir die Umlaut-Punkte:
Damit wird z.B. der *A* Buchstabe wiederverwendet und ein neuer Laut durch hinzugefügte Zeichen erzeugt: *Ä*.

In der japanischen Schrift gibt es ein kleines angebrachtes Zeichen, dass wie Anführungszeichen (Gänsefüßchen) Oben aussieht:
<span style="border: 1px solid gray; font-size: 20px;">&#x3099;</span>.
Es wandelt stimmlose Konsonanten (nur Luftstrom) in stimmhafte Konsonanten (Ton mit Stimmlippen) um.

Für **h** gibt es zwei Varianten, da man mit den Lippen **b** aber auch **p** formen kann. Für **p** Laute wird ein Kreis verwendet: <span style="border: 1px solid gray; font-size: 20px;">&#x309A;</span>.

> Merksatz: Wird der Buchstabe **h** unten mit extra Strichen (&#x3099;) geschlossen, entsteht der Buchstabe **b**. Die horizontale Spiegelung ist **p** und wird durch einen **P**unkt oben (&#x309A;) markiert.

<table class="centered-table">
    <thead>
        <tr>
            <th></th>
            <th>a</th>
            <th>i</th>
            <th>u</th>
            <th>e</th>
            <th>o</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <th>k <i class="fa fa-arrow-right"></i> g</th>
            <td>
                が<span class="ts">|ga</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ga.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ガ<span class="ts">|ga</span>
            </td>
            <td>
                ぎ<span class="ts">|gi</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/gi.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ギ<span class="ts">|gi</span>
            </td>
            <td>
                ぐ<span class="ts">|gu</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/gu.wav')">
                    <i class="fas fa-play"></i>
                </button>
                グ<span class="ts">|gu</span>
            </td>
            <td>
                げ<span class="ts">|ge</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ge.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ゲ<span class="ts">|ge</span>
            </td>
            <td>
                ご<span class="ts">|go</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/go.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ゴ<span class="ts">|go</span>
            </td>
        </tr>
        <tr>
            <th>s <i class="fa fa-arrow-right"></i> z</th>
            <td>
                ざ<span class="ts">|za</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/za.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ザ<span class="ts">|za</span>
            </td>
            <td>
                じ<span class="ts">|ji</span>
                <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/ji.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ジ<span class="ts">|ji</span>
            </td>
            <td>
                ず<span class="ts">|zu</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/zu.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ズ<span class="ts">|zu</span>
            </td>
            <td>
                ぜ<span class="ts">|ze</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ze.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ゼ<span class="ts">|ze</span>
            </td>
            <td>
                ぞ<span class="ts">|zo</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/zo.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ゾ<span class="ts">|zo</span>
            </td>
        </tr>
        <tr>
            <th>t <i class="fa fa-arrow-right"></i> d</th>
            <td>
                だ<span class="ts">|da</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/da.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ダ<span class="ts">|da</span>
            </td>
            <td>
                ぢ<span class="ts">|ji</span>
                <button class="play-btn  play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/ji.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ヂ<span class="ts">|ji</span>
            </td>
            <td>
                づ<span class="ts">|zu</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/zu.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ヅ<span class="ts">|zu</span>
            </td>
            <td>
                で<span class="ts">|de</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/de.wav')">
                    <i class="fas fa-play"></i>
                </button>
                デ<span class="ts">|de</span>
            </td>
            <td>
                ど<span class="ts">|do</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/do.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ド<span class="ts">|do</span>
            </td>
        </tr>
        <tr>
            <th>h <i class="fa fa-arrow-right"></i> b</th>
            <td>
                ば<span class="ts">|ba</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/ba.wav')">
                    <i class="fas fa-play"></i>
                </button>
                バ<span class="ts">|ba</span>
            </td>
            <td>
                び<span class="ts">|bi</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/bi.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ビ<span class="ts">|bi</span>
            </td>
            <td>
                ぶ<span class="ts">|bu</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/bu.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ブ<span class="ts">|bu</span>
            </td>
            <td>
                べ<span class="ts">|be</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/be.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ベ<span class="ts">|be</span>
            </td>
            <td>
                ぼ<span class="ts">|bo</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/bo.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ボ<span class="ts">|bo</span>
            </td>
        </tr>
        <tr>
            <th>h <i class="fa fa-arrow-right"></i> p</th>
            <td>
                ぱ<span class="ts">|pa</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/pa.wav')">
                    <i class="fas fa-play"></i>
                </button>
                パ<span class="ts">|pa</span>
            </td>
            <td>
                ぴ<span class="ts">|pi</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/pi.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ピ<span class="ts">|pi</span>
            </td>
            <td>
                ぷ<span class="ts">|pu</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/pu.wav')">
                    <i class="fas fa-play"></i>
                </button>
                プ<span class="ts">|pu</span>
            </td>
            <td>
                ぺ<span class="ts">|pe</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/pe.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ペ<span class="ts">|pe</span>
            </td>
            <td>
                ぽ<span class="ts">|po</span>
                <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/po.wav')">
                    <i class="fas fa-play"></i>
                </button>
                ポ<span class="ts">|po</span>
            </td>
        </tr>
    </tbody>
</table>

Folgendes ist zu beachten:
* Bei **s** <i class="fa fa-arrow-right"></i> **z** wird es nicht **zi** sondern **ji** mit der Aussprache wie *dji*.
* Bei **t** <i class="fa fa-arrow-right"></i> **d** wird es nicht **di** sondern **ji** mit der Aussprache wie *dji*.
* Nicht wundern: In modernem japanisch werden folgende Silbenpaare tatsächlich [gleich ausgesprochen](https://japanese.stackexchange.com/a/1255) :
  * じ<span class="ts">|ji</span> und ぢ<span class="ts">|ji</span>
  * ず<span class="ts">|zu</span> und づ<span class="ts">|zu</span>

<br/>

Die kleinen angebrachten Zeichen können auch auf die Zusammensetzungen angewandt werden.

<table class="centered-table">
  <thead>
    <tr>
      <th>
      </th>
      <th>ya</th>
      <th>yu</th>
      <th>yo</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>k <i class="fa fa-arrow-right"></i> g</th>
      <td> ぎゃ<span class="ts">|gya</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/gya.wav')">
        <i class="fas fa-play">
        </i>
        </button> ギャ<span class="ts">|gya</span>
      </td>
      <td> ぎゅ<span class="ts">|gyu</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/gyu.wav')">
        <i class="fas fa-play">
        </i>
        </button> ギュ<span class="ts">|gyu</span>
      </td>
      <td> ぎょ<span class="ts">|gyo</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/gyo.wav')">
        <i class="fas fa-play">
        </i>
        </button> ギョ<span class="ts">|gyo</span>
      </td>
    </tr>
    <tr>
      <th>s <i class="fa fa-arrow-right"></i> z</th>
      <td> じゃ<span class="ts">|ja</span>
      <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/ja.wav')">
        <i class="fas fa-play">
        </i>
        </button> ジャ<span class="ts">|ja</span>
      </td>
      <td> じゅ<span class="ts">|ju</span>
      <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/ju.wav')">
        <i class="fas fa-play">
        </i>
        </button> ジュ<span class="ts">|ju</span>
      </td>
      <td> じょ<span class="ts">|jo</span>
      <button class="play-btn play-btn-warn" onclick="loadAndPlay(this, 'hiragana_reading/jo.wav')">
        <i class="fas fa-play">
        </i>
        </button> ジョ<span class="ts">|jo</span>
      </td>
    </tr>
    <tr>
      <th>h <i class="fa fa-arrow-right"></i> b</th>
      <td> びゃ<span class="ts">|bya</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/bya.wav')">
        <i class="fas fa-play">
        </i>
        </button> ビャ<span class="ts">|bya</span>
      </td>
      <td> びゅ<span class="ts">|byu</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/byu.wav')">
        <i class="fas fa-play">
        </i>
        </button> ビュ<span class="ts">|byu</span>
      </td>
      <td> びょ<span class="ts">|byo</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/byo.wav')">
        <i class="fas fa-play">
        </i>
        </button> ビョ<span class="ts">|byo</span>
      </td>
    </tr>
    <tr>
      <th>h <i class="fa fa-arrow-right"></i> p</th>
      <td> ぴゃ<span class="ts">|pya</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/pya.wav')">
        <i class="fas fa-play">
        </i>
        </button> ピャ<span class="ts">|pya</span>
      </td>
      <td> ぴゅ<span class="ts">|pyu</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/pyu.wav')">
        <i class="fas fa-play">
        </i>
        </button> ピュ<span class="ts">|pyu</span>
      </td>
      <td> ぴょ<span class="ts">|pyo</span>
      <button class="play-btn" onclick="loadAndPlay(this, 'hiragana_reading/pyo.wav')">
        <i class="fas fa-play">
        </i>
        </button> ピョ<span class="ts">|pyo</span>
      </td>
    </tr>
  </tbody>
</table>

Folgendes ist zu beachten:
* Als deutscher Muttersprachler ist man verleitet じゃ<span class="ts">|ja</span> wie *ja*gt, じゅ<span class="ts">|ju</span> wie *ju*ng und じょ<span class="ts">|jo</span> wie *jo*deln auszusprechen.
Es ist aber immer ein *d*/*t* am Anfang, also じゃ<span class="ts">|ja</span> eher wie *Ja*ckett, じゅ<span class="ts">|ju</span> eher wie *Ju*nkie und じょ<span class="ts">|jo</span> eher wie *Jo*b.

### Besonderheiten

Anhand des Wortes がっこう<span class="ts">|gakkou</span> <button class="play-btn" onclick="loadAndPlay(this, 'word_reading/gakkou.mp3')"><i class="fas fa-play"></i></button> (dt. Schule) können wir noch zwei Besonderheiten erklären.

1. Es gibt das kleine っ<span class="ts" style="font-size: smaller">|tsu</span>, welches einen doppelten Konsonanten und kleine Pause erzeugt.
Anstatt *gako* wird es *gak-ko*.
2. Ist ein う<span class="ts">|u</span> nach einem *o* Laut, wird das *o* verlängert, wie wenn wir *oh* sagen.
Daher ist in der Aufnahme kein *u* am Ende zu hören, sondern ein langes *oh*.

<!-- とう lang gezogen:  hinter einem o ein u zur Verlängerung verwendet -->
<!-- kleines tsu (zwei tt) っ doppelter Konsonant -->
<!-- kleines a,e,i,o,u   tippe l + a　-->
<!-- kata: ー　lang gezogen　-->

### Fazit

Mit den Silben aus den Tabellen lassen sich nahezu alle japanischen Wörter bilden.
Nun können wir auch ひらがな<span class="ts">|hiragana</span> in ひらがな<span class="ts">|hiragana</span> und カタカナ<span class="ts">|katakana</span> in カタカナ<span class="ts">|katakana</span> schreiben.

[Ein paar Wörter](https://de.wikipedia.org/wiki/Liste_deutscher_W%C3%B6rter_aus_dem_Japanischen) aus dem Japanischen werden auch in der deutschen Sprache verwendet.
Man kann sie nun in echter japanischer Schrift schreiben:
* ぼんさい<span class="ts">|bonsai</span> - wörtlich: Topfpflanzung
* えもじ<span class="ts">|emoji</span> - Piktogramm (in elektronischen Textnachrichten)
* じゅうどう<span class="ts">|juudou</span> - wörtlich: sanfter Weg
* カラオケ<span class="ts">|karaoke</span> - wörtlich: leeres Orchester
* おりがみ<span class="ts">|origami</span> - wörtlich: Papierfalten
* さむらい<span class="ts">|samurai</span> - wörtlich: Dienender
* たまごっち<span class="ts">|tamagocchi</span> - ein Elektronikspielzeug
* つなみ<span class="ts">|tsunami</span> - wörtlich: Hafenwelle
* やくざ<span class="ts">|yakuza</span> - japanische Mafia

Mithilfe der Tabellen kann mühselig die einzelnen Silben nachgeschlagen werden.
Doch nicht nur das Lesen und Umschreiben ist wichtig:
Der Lernende sollte so früh wie möglich in die Lage versetzt werden, selbst die Schrift schreiben zu können.

## Selbst Schreiben Können

<!-- beispiel machen: animiertes gif -->

Hat man die Umschrift gelernt, kann man mit einer normalen deutschen Tastatur und der richtigen Einstellung selbst ひらがな<span class="ts">|hiragana</span> und カタカナ<span class="ts">|katakana</span> tippen.

### Online

Die [Input Tools von Google](https://www.google.com/inputtools/try/) können online ausprobiert werden.
Stellt man die Sprache auf Japanisch, kann man das Verhalten der Tastatur testen.
Auch [Yavego](https://www.yavego.com/tastatur-japanisch/) bietet eine Japanische Tastatur online an.

Doch besser ist es für sein Betriebsystem die richtige Eingabemethode einzustellen.

### Windows

In Windows kann über [Microsoft IME](https://support.microsoft.com/de-de/windows/microsoft-ime-f%C3%BCr-japanisch-da40471d-6b91-4042-ae8b-713a96476916) (Input Method Editor) die Tastatur auf Japanische Eingabe gestellt werden.
Am besten man folgt einer [Einstellungsanleitung](https://learn.microsoft.com/de-de/globalization/input/japanese-ime).

![](windows-keyboard-layouts.png)

Nachdem Japanisch eingestellt ist, kann man ひらがな<span class="ts">|hiragana</span> eintippen.

![](windows-ime.png)

### Unix

In Unix Systemen gibt es die [Universal Input Method (UIM)](https://wiki.archlinux.org/title/Uim).
Dort kann mit [Anthy](https://en.wikipedia.org/wiki/Anthy) die Japanische Eingabe hinzugefügt werden.

[Mozc](https://wiki.archlinux.org/title/Mozc) ist von Google und für mehrere Betriebsysteme implementiert worden.
Auch [Ubuntu](https://help.ubuntu.com/community/JapaneseInput) untersützt Mozc in seiner Distribution.

<!--
### Android

Die Google-Tastatur [Gboard](https://play.google.com/store/apps/details?id=com.google.android.inputmethod.latin) unterstützt auch Japanisch.
-->

### Generelle Nutzungshinweise

Verschiedene Eingabemethoden verhalten sich möglicherweise unterschiedlich.
Im Folgenden eine kurze Erklärung der Nutzung, wie es in den meisten Tastaturen der Fall sein müsste.
* Schreibe die Umschrift, wie in den Tabellen oben gezeigt.
Es entstehen die Silben, sobald sie vollständig geschrieben werden.
Beispielsweise entsteht きゃ<span class="ts">|kya</span>, sobald der letzte Buchstabe <kbd>ky**a**</kbd> getippt ist.
* Erst durch Drücken der <kbd>Eingabetaste</kbd> wird das geschriebene Wort in den Text übernommen.
* Durch das Drücken von <kbd>Leerzeichen</kbd> oder <kbd><i class="fa fa-arrow-down"></i></kbd> kann man durch verschiedene Formen wechseln.
Näheres dazu im nächsten Kapitel.
* Manche Tastaturen erlauben durch Drücken von Funktionstasten das Wort in seiner Schrift zu ändern (am Beispiel がっこう<span class="ts">|gakkou</span>).
  * <kbd>F6</kbd> ひらがな<span class="ts">|hiragana</span>-Modus: がっこう<span class="ts">|gakkou</span>
  * <kbd>F7</kbd> カタカナ<span class="ts">|katakana</span>-Modus: ガッコウ<span class="ts">|gakkou</span>
  * <kbd>F8</kbd> カタカナ<span class="ts">|katakana</span>-Halbe-Weite-Modus: ｶﾞｯｺｳ<span class="ts">|gakkou</span>
* Da mit <kbd>n</kbd> entweder ein **n** Laut wie z.B. な<span class="ts">|na</span> gemeint sein könnte oder einfach ん<span class="ts">|n</span>, muss man bei ん<span class="ts">|n</span> <kbd>nn</kbd> tippen.
* Tippe zweimal den selben Konsonanten, um ein kleines っ<span class="ts" style="font-size: smaller">|tsu</span> zu erhalten.
Alternativ kann man <kbd>ltsu</kbd> schreiben.
Das <kbd>l</kbd> steht für das englische Wort *lower* (dt. kleiner).



<br/>

Silben tippen zu können und die Tabellen gesehen und verstanden zu haben, ist ein erster wichtiger Schritt.
Doch das hilft einem Anfänger trotzdem nicht, nun die Silbenschriften einfach lesen zu können.
Es erfordert nun das Lernen von Silbe zu Aussprache bzw. Transkription.

## Lernen durch Wiederholung

Der Lernende sollte sich nun ständig fordern, alle Silben der beiden Schriften ひらがな<span class="ts">|hiragana</span> und カタカナ<span class="ts">|katakana</span> lesen und umschreiben zu müssen, damit sich die Aussprache und Transkription im Gedächtnis festigt.

Nutzt man die [Anki](https://apps.ankiweb.net/) Lernkartei-Applikation, gibt es bereits gut gemachte [Kartenstapel](https://ankiweb.net/shared/decks?search=kana) für die Schriften.
* [Japanische Silben: Kana (Hiragana und Katakana)](https://ankiweb.net/shared/info/978901593) - deutsch
* [Tofugu: Learn Hiragana Deck](https://ankiweb.net/shared/info/1081858108) & [Tofugu: Learn Katakana Deck](https://ankiweb.net/shared/info/1027153995) - englisch, aber mit Merksätzen, Merkbildern und Aussprache Aufnahmen.
Daher auch empfohlen.

Für Android-Handys gibt es auch einige Apps im [Google Playstore](https://play.google.com/store/search?q=kana).
Ob als [Abfragetests](https://apkpure.com/kana-town-learn-japanese-hir/fr.koridev.kanatown) oder [spielerisch](https://play.google.com/store/apps/details?id=com.kazzuyak.kanagame), wichtig ist, dass man ständig gefordert wird zu einer Silbe die Umschrift tippen zu müssen.
[Spiele für den PC](https://store.steampowered.com/search/?term=kana) gibt es natürlich auch.

Lernende tendieren wegen der starken Nutzung von ひらがな<span class="ts">|hiragana</span> das カタカナ<span class="ts">|katakana</span> eher zu vernachlässigen.
Ich empfehle beide Schriften als gleich wichtig anzusehen und im Lernaufwand genau 50% ひらがな<span class="ts">|hiragana</span> und 50% カタカナ<span class="ts">|katakana</span> einzusetzen.
Man wird sich sonst beim Lesen von echten japanischen Texten immer ärgern, noch fundamentale Wissenslücken zu haben.

Es sollten auch immer alle Silben gelernt werden.
Dadurch wird das Gehirn darauf trainiert z.B. Ausschau nach dem &#x3099; Zeichen zu halten.
Zudem gewöhnt man sich daran, die angehangenen ゃ<span class="ts" style="font-size: smaller;">|ya</span>, ゅ<span class="ts" style="font-size: smaller;">|yu</span> und ょ<span class="ts" style="font-size: smaller;">|yo</span> als eine Silbeneinheit zu betrachten und auszusprechen.

Dieser Abschnitt im Kapitel ist kurz, da hier nun die Arbeit des Lernenden im Vordergrund steht.
Die Silben-Aussprache-Paare müssen verinnerlicht werden, da sie fundamental sind für den weiteren Lernweg.


## Fazit

Mithilfe der Umschrift (Transkription) ist es möglich die aus chinesischen Zeichen stammende japanische Silbenschriften ひらがな<span class="ts">|hiragana</span> und カタカナ<span class="ts">|katakana</span> sowie ihre ungefähre Aussprache zu vermitteln.
In Tabellen wurden die Grundsilben, die Zusammensetzungen und Silben mit angebrachten Zeichen zusammengefasst.
Durch Abspielschaltflächen konnte man die einzelnen Silben durch Hören nachvollziehen.
Der Lernende sollte zudem in der Lage sein, durch eine ausgewählte Eingabemethode die Silben selbst schreiben zu können.
Am längsten müsste Zeit in das Lernen durch ständige Wiederholung gegangen sein, welches den Lernenden nun ermöglichen sollte, in Silbenschrift geschriebene Wörter entziffern zu können.

### Kleiner Test

Der Lernende sollte erst zum nächsten Kapitel übergehen, wenn alle Silben gelesen werden können.
Im Folgenden ist ein kleiner Test, um das selbst überprüfen zu können.
Nach jedem neuen Laden der Seite (<kbd>F5</kbd>) mischt sich eine neue ひらがな (links) und カタカナ (rechts) Silbenliste.
Durch Darüberhalten mit der Maus wird die Transkription aufgedeckt.
Erst wenn der Lernende bei wirklich allen Silben richtig lag, sollte das nächste Kapitel besucht werden.
Wurde ein Fehler gemacht, ist es nicht schlimm weiterhin beim [Lernen durch Wiederholung](#lernen-durch-wiederholung) zu bleiben.

<table>
    <tr>
        <td><ul id="hiragana-list"></ul></td>
        <td><ul id="katakana-list"></ul></td>
    </tr>
</table>




<script>
    const hiraganaToAscii = {
        'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
        'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
        'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
        'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
        'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
        'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
        'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
        'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
        'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
        'わ': 'wa', 'を': 'wo', 'ん': 'n',
        'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
        'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
        'だ': 'da', 'ぢ': 'ji', 'づ': 'zu', 'で': 'de', 'ど': 'do',
        'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
        'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
        'きゃ': 'kya', 'きゅ': 'kyu', 'きょ': 'kyo',
        'しゃ': 'sha', 'しゅ': 'shu', 'しょ': 'sho',
        'ちゃ': 'cha', 'ちゅ': 'chu', 'ちょ': 'cho',
        'にゃ': 'nya', 'にゅ': 'nyu', 'にょ': 'nyo',
        'ひゃ': 'hya', 'ひゅ': 'hyu', 'ひょ': 'hyo',
        'みゃ': 'mya', 'みゅ': 'myu', 'みょ': 'myo',
        'りゃ': 'rya', 'りゅ': 'ryu', 'りょ': 'ryo',
        'ぎゃ': 'gya', 'ぎゅ': 'gyu', 'ぎょ': 'gyo',
        'じゃ': 'ja', 'じゅ': 'ju', 'じょ': 'jo',
        'びゃ': 'bya', 'びゅ': 'byu', 'びょ': 'byo',
        'ぴゃ': 'pya', 'ぴゅ': 'pyu', 'ぴょ': 'pyo'
    };
    const katakanaToAscii = {
        'ア': 'a', 'イ': 'i', 'ウ': 'u', 'エ': 'e', 'オ': 'o',
        'カ': 'ka', 'キ': 'ki', 'ク': 'ku', 'ケ': 'ke', 'コ': 'ko',
        'サ': 'sa', 'シ': 'shi', 'ス': 'su', 'セ': 'se', 'ソ': 'so',
        'タ': 'ta', 'チ': 'chi', 'ツ': 'tsu', 'テ': 'te', 'ト': 'to',
        'ナ': 'na', 'ニ': 'ni', 'ヌ': 'nu', 'ネ': 'ne', 'ノ': 'no',
        'ハ': 'ha', 'ヒ': 'hi', 'フ': 'fu', 'ヘ': 'he', 'ホ': 'ho',
        'マ': 'ma', 'ミ': 'mi', 'ム': 'mu', 'メ': 'me', 'モ': 'mo',
        'ヤ': 'ya', 'ユ': 'yu', 'ヨ': 'yo',
        'ラ': 'ra', 'リ': 'ri', 'ル': 'ru', 'レ': 're', 'ロ': 'ro',
        'ワ': 'wa', 'ヲ': 'wo', 'ン': 'n',
        'ガ': 'ga', 'ギ': 'gi', 'グ': 'gu', 'ゲ': 'ge', 'ゴ': 'go',
        'ザ': 'za', 'ジ': 'ji', 'ズ': 'zu', 'ゼ': 'ze', 'ゾ': 'zo',
        'ダ': 'da', 'ヂ': 'ji', 'ヅ': 'zu', 'デ': 'de', 'ド': 'do',
        'バ': 'ba', 'ビ': 'bi', 'ブ': 'bu', 'ベ': 'be', 'ボ': 'bo',
        'パ': 'pa', 'ピ': 'pi', 'プ': 'pu', 'ペ': 'pe', 'ポ': 'po',
        'キャ': 'kya', 'キュ': 'kyu', 'キョ': 'kyo',
        'シャ': 'sha', 'シュ': 'shu', 'ショ': 'sho',
        'チャ': 'cha', 'チュ': 'chu', 'チョ': 'cho',
        'ニャ': 'nya', 'ニュ': 'nyu', 'ニョ': 'nyo',
        'ヒャ': 'hya', 'ヒュ': 'hyu', 'ヒョ': 'hyo',
        'ミャ': 'mya', 'ミュ': 'myu', 'ミョ': 'myo',
        'リャ': 'rya', 'リュ': 'ryu', 'リョ': 'ryo',
        'ギャ': 'gya', 'ギュ': 'gyu', 'ギョ': 'gyo',
        'ジャ': 'ja', 'ジュ': 'ju', 'ジョ': 'jo',
        'ビャ': 'bya', 'ビュ': 'byu', 'ビョ': 'byo',
        'ピャ': 'pya', 'ピュ': 'pyu', 'ピョ': 'pyo'
    };


    function getRandomHiragana(n, kana, classname) {
        const keys = Object.keys(kana);
        const selectedKeys = [];

        while (selectedKeys.length < n) {
            const randomKey = keys[Math.floor(Math.random() * keys.length)];
            if (!selectedKeys.includes(randomKey)) {
                selectedKeys.push(randomKey);
            }
        }

        const ul = document.getElementById(classname);
        ul.innerHTML = ''; // Clear the existing list

        selectedKeys.forEach(key => {
            const li = document.createElement('li');
            var asciiValue = kana[key];
            var needed = 4 - asciiValue.length;

            key = key.padEnd(3, '　');

            for(var i = 0; i < needed; i++){
                asciiValue += '&nbsp;';
            }
            li.innerHTML = `${key} <span class="spoiler">${asciiValue}</span>`;
            ul.appendChild(li);
        });
    }

    getRandomHiragana(20, hiraganaToAscii, 'hiragana-list');
    getRandomHiragana(20, katakanaToAscii, 'katakana-list');
</script>
