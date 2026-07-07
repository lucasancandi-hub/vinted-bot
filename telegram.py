# telegram.py
# Piccolo aiutante per parlare con Telegram: manda affari, cancella messaggi,
# e ascolta i pulsanti (Ignora).

import urllib.request
import urllib.parse
import json
import config

API = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}"


def _post(metodo, dati):
    url = f"{API}/{metodo}"
    corpo = urllib.parse.urlencode(dati).encode("utf-8")
    with urllib.request.urlopen(url, data=corpo, timeout=30) as risposta:
        return json.loads(risposta.read())


def manda_affare(annuncio, extra=""):
    """Manda l'avviso di un affare, con foto e pulsanti Apri / Ignora."""
    tastiera = {"inline_keyboard": [
        [{"text": "🔗 Apri su Vinted", "url": annuncio["url"]}],
        [{"text": "🙈 Ignora", "callback_data": "del"}],
    ]}
    testo = (
        f"🔥 <b>Possibile affare</b>\n"
        f"{annuncio['brand']} — {annuncio['titolo'][:120]}\n"
        f"💶 <b>{annuncio['prezzo']:.2f} €</b>{extra}"
    )
    if annuncio.get("taglia"):
        testo += f"\n📏 Taglia {annuncio['taglia']}"

    dati = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(tastiera),
    }

    # Proviamo con la foto; se non va, mandiamo solo il testo.
    if annuncio.get("foto"):
        try:
            risposta = _post("sendPhoto", dict(dati, photo=annuncio["foto"], caption=testo))
            if risposta.get("ok"):
                return risposta
        except Exception:
            pass
    return _post("sendMessage", dict(dati, text=testo))


def manda_testo(testo):
    return _post("sendMessage", {"chat_id": config.TELEGRAM_CHAT_ID, "text": testo})


def cancella(chat_id, message_id):
    try:
        _post("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
    except Exception:
        pass


def rispondi_pulsante(callback_id, testo=""):
    try:
        _post("answerCallbackQuery", {"callback_query_id": callback_id, "text": testo})
    except Exception:
        pass


def prendi_aggiornamenti(offset, attesa=25):
    """Aspetta (fino a 'attesa' secondi) che qualcuno prema un pulsante."""
    dati = {"timeout": attesa, "allowed_updates": json.dumps(["callback_query"])}
    if offset:
        dati["offset"] = offset
    url = f"{API}/getUpdates?" + urllib.parse.urlencode(dati)
    try:
        with urllib.request.urlopen(url, timeout=attesa + 10) as risposta:
            return json.loads(risposta.read())
    except Exception:
        return {"ok": False, "result": []}


# Se lanci direttamente questo file, manda un messaggio di prova.
if __name__ == "__main__":
    print("Mando un messaggio di prova...")
    r = manda_testo("Ciao Luca! Sono il tuo bot Vinted. Funziono! 🛰️")
    print("Inviato!" if r.get("ok") else f"Problema: {r}")
