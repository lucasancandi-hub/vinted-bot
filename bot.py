# bot.py
# Il "motore" del bot Vinted: ogni pochi minuti guarda gli annunci dei brand
# scelti, calcola il prezzo medio di ognuno, e ti avvisa su Telegram quando
# spunta un pezzo molto sotto la media (un affare / errore di prezzo).
#
# Per avviarlo:  python C:\Users\Luca\vinted-bot\bot.py
# Per fermarlo:  chiudi la finestra, oppure premi CTRL+C.

import sys
import os
import time
import json
import threading

import config
import telegram
import vinted

# File dove ricordiamo gli annunci gia' segnalati (id -> prezzo),
# cosi' non ripetiamo lo stesso avviso.
FILE_MEMORIA = os.path.join(os.path.dirname(__file__), "visti.json")

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def carica_memoria():
    if os.path.exists(FILE_MEMORIA):
        try:
            with open(FILE_MEMORIA, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def salva_memoria(memoria):
    # Teniamo solo gli ultimi 5000, cosi' il file non cresce all'infinito.
    if len(memoria) > 5000:
        memoria = dict(list(memoria.items())[-5000:])
    with open(FILE_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f)


def mediana(valori):
    v = sorted(valori)
    n = len(v)
    if n == 0:
        return 0
    if n % 2:
        return v[n // 2]
    return (v[n // 2 - 1] + v[n // 2]) / 2


def ascolta_pulsanti():
    """Gira in sottofondo: quando premi 'Ignora', cancella quel messaggio."""
    offset = None
    while True:
        aggiornamenti = telegram.prendi_aggiornamenti(offset)
        for u in aggiornamenti.get("result", []):
            offset = u["update_id"] + 1
            cb = u.get("callback_query")
            if not cb:
                continue
            if cb.get("data") == "del":
                msg = cb.get("message", {})
                telegram.cancella(msg.get("chat", {}).get("id"), msg.get("message_id"))
                telegram.rispondi_pulsante(cb["id"], "Ignorato 🙈")


def da_scartare(titolo):
    """Vero se il titolo contiene una parola da escludere (bimbo/accessori)."""
    t = titolo.lower()
    return any(parola in t for parola in config.ESCLUDI_PAROLE)


def e_un_affare(prezzo, media):
    return (prezzo >= config.PREZZO_MINIMO
            and prezzo <= media * config.FRAZIONE_AFFARE)


def un_giro(memoria, primo_giro):
    """Un controllo completo su tutti i brand. Ritorna quanti avvisi ha mandato."""
    inviati = 0
    for indice, brand in enumerate(config.BRANDS):
        if indice > 0:
            time.sleep(2)  # piccola pausa per non stressare Vinted
        try:
            annunci = vinted.cerca(brand)
        except Exception as errore:
            print(f"  problema con {brand['nome']}: {errore}")
            continue

        # Togliamo roba da bambino e accessori: falserebbero la media.
        annunci = [a for a in annunci if not da_scartare(a["titolo"])]

        if len(annunci) < 8:
            print(f"[{time.strftime('%H:%M')}] {brand['nome']}: pochi annunci utili")
            continue

        media = mediana([a["prezzo"] for a in annunci])
        print(f"[{time.strftime('%H:%M')}] {brand['nome']}: {len(annunci)} annunci, media {media:.0f}€")

        for a in annunci:
            if not e_un_affare(a["prezzo"], media):
                continue
            # Gia' visto a questo prezzo (o piu' alto)? Non ripetere.
            visto = memoria.get(a["id"])
            if visto is not None and a["prezzo"] >= visto - 0.01:
                continue
            # Al primo giro non superare il limite: gli altri li "ricordiamo"
            # in silenzio per avvisarti solo sui prossimi nuovi affari.
            if primo_giro and inviati >= config.MAX_PRIMO_GIRO:
                memoria[a["id"]] = a["prezzo"]
                continue

            sconto = round((1 - a["prezzo"] / media) * 100)
            extra = f"  (−{sconto}% sulla media di {media:.0f}€)"
            try:
                telegram.manda_affare(a, extra)
                inviati += 1
                print(f"    -> AFFARE {brand['nome']}: {a['prezzo']:.0f}€ ({sconto}% sotto)")
                time.sleep(1)
            except Exception as errore:
                print(f"    errore invio: {errore}")
            memoria[a["id"]] = a["prezzo"]

    salva_memoria(memoria)
    return inviati


def main():
    if not config.TELEGRAM_TOKEN or "METTI" in config.TELEGRAM_TOKEN:
        print("!! Manca il TOKEN del bot in config.py.")
        print("   Apri config.py e incolla il token dato da BotFather.")
        return

    # Avviamo in sottofondo l'ascolto dei pulsanti "Ignora".
    threading.Thread(target=ascolta_pulsanti, daemon=True).start()

    memoria = carica_memoria()
    primo_giro = (len(memoria) == 0)

    nomi = ", ".join(b["nome"] for b in config.BRANDS)
    telegram.manda_testo("🛰️ Bot Vinted avviato! Cerco affari su: " + nomi)
    print("Bot avviato. Premi CTRL+C per fermare.\n")

    while True:
        n = un_giro(memoria, primo_giro)
        primo_giro = False
        print(f"...aspetto {config.INTERVALLO_SECONDI // 60} min (avvisi mandati: {n}).\n")
        time.sleep(config.INTERVALLO_SECONDI)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot fermato. A presto!")
