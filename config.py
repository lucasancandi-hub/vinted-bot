# config.py
# Qui teniamo le impostazioni del bot Vinted.

import os

# --- 1) IL TUO BOT TELEGRAM -------------------------------------------------
# La chiave (token) del bot NON e' scritta qui (cosi' il codice puo' stare
# anche su GitHub in modo sicuro). Viene letta in due modi:
#   - in cloud (GitHub): dalla "cassaforte" dei Secret (variabile TELEGRAM_TOKEN)
#   - sul tuo PC: dal file  token.txt  nella stessa cartella (NON caricarlo online)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
if not TELEGRAM_TOKEN:
    try:
        with open(os.path.join(os.path.dirname(__file__), "token.txt"), encoding="utf-8") as _f:
            TELEGRAM_TOKEN = _f.read().strip()
    except Exception:
        pass

# Chi riceve gli avvisi (i codici Telegram). Il primo sei tu.
# Per aggiungere qualcuno: deve prima premere START sul bot, poi metti qui
# il suo codice separato da una virgola.
TELEGRAM_CHAT_IDS = [
    7093323110,   # Luca
    7358121122,   # @Banni98th
]


# --- 2) I BRAND DA SORVEGLIARE ----------------------------------------------
# Ho scelto i brand migliori per il resell e ho mirato la ricerca dove
# nascono davvero gli errori di prezzo (soprattutto i capispalla).
# Per ogni brand:
#   nome  = come lo vedi negli avvisi
#   cerca = cosa cercare su Vinted (puoi aggiungere una parola tipo "giacca"
#           per mirare il capospalla, dove ci sono gli affari veri)
#   ok    = parole che devono comparire nel brand dell'annuncio (anti-errore)
BRANDS = [
    {"nome": "Stone Island",  "cerca": "stone island",           "ok": ["stone island"]},
    {"nome": "Moncler",       "cerca": "moncler",                "ok": ["moncler"]},
    {"nome": "C.P. Company",  "cerca": "cp company",             "ok": ["c.p. company", "cp company"]},
    {"nome": "Arc'teryx",     "cerca": "arcteryx",               "ok": ["arc'teryx", "arcteryx", "arc"]},
    {"nome": "Carhartt",      "cerca": "carhartt giacca",        "ok": ["carhartt"]},
    {"nome": "The North Face","cerca": "the north face piumino", "ok": ["north face"]},
    {"nome": "Patagonia",     "cerca": "patagonia giacca",       "ok": ["patagonia"]},
    {"nome": "Ralph Lauren",  "cerca": "ralph lauren giacca",    "ok": ["ralph lauren"]},
    {"nome": "Nike",          "cerca": "nike vintage",           "ok": ["nike"]},
    {"nome": "Adidas",        "cerca": "adidas vintage",         "ok": ["adidas"]},
    {"nome": "Stussy",        "cerca": "stussy",                 "ok": ["stussy", "stüssy"]},
    {"nome": "BAPE",          "cerca": "a bathing ape",          "ok": ["bathing ape", "bape"]},
    {"nome": "Essentials",    "cerca": "fear of god essentials", "ok": ["essentials", "fear of god"]},
]


# --- 3) QUANDO E' UN AFFARE (puoi modificare questi numeri) ------------------
# Ogni quanto ricontrollare Vinted, in secondi. 120 = ogni 2 minuti.
INTERVALLO_SECONDI = 120

# Prezzo minimo perche' un annuncio venga considerato (in euro).
# Sotto questa cifra non e' roba da rivendere. Alzalo per meno avvisi.
PREZZO_MINIMO = 25

# Un affare deve costare al massimo questa frazione del prezzo medio del brand
# in quel momento. 0.55 = deve costare il 55% o meno della media.
# Abbassalo (es. 0.45) per ricevere solo gli affari piu' forti.
FRAZIONE_AFFARE = 0.55

# Al primissimo avvio, quanti affari mostrare al massimo (per non riempirti
# di messaggi tutti insieme). Dopo, ti avvisa su ogni nuovo affare.
MAX_PRIMO_GIRO = 6

# Parole che fanno SCARTARE un annuncio (roba da bambino e accessori/oggetti
# di poco valore, che falserebbero la media e non si rivendono).
ESCLUDI_PAROLE = [
    # bambino
    "bimb", "bambin", "junior", "enfant", "niñ", "nino", "kids", "baby",
    "neonato", "ragazz", "anni", "mesi", "years",
    # accessori e oggetti di poco valore
    "t-shirt", "tshirt", "t shirt", " tee", "polo", "maillot", "short",
    "calz", "sock", "chausset", "cappell", "beanie", " hat", "scarf",
    "sciarp", "guant", "glove", "cintur", "belt", "portafog", "wallet",
    "portachiav", "keychain", "adesiv", "sticker", "patch", "toppa",
    "boxer", "intim", "costume", "bikini", "ciabatt", "infradito",
    "profum", "perfume", "replica", "fake",
]
