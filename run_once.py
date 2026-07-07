# run_once.py
# Versione "un colpo solo" del bot, pensata per il cloud (GitHub Actions):
# fa UN singolo controllo di tutti i brand, gestisce i pulsanti "Ignora"
# arrivati nel frattempo, salva la memoria e si chiude.
#
# GitHub la lancia da solo ogni ~10 minuti.

import bot
import telegram


def gestisci_pulsanti():
    """Controlla se hai premuto 'Ignora' e cancella quei messaggi."""
    aggiornamenti = telegram.prendi_aggiornamenti(None, attesa=3)
    ultimo = None
    for u in aggiornamenti.get("result", []):
        ultimo = u["update_id"]
        cb = u.get("callback_query")
        if cb and cb.get("data") == "del":
            msg = cb.get("message", {})
            telegram.cancella(msg.get("chat", {}).get("id"), msg.get("message_id"))
            telegram.rispondi_pulsante(cb["id"], "Ignorato 🙈")
    # Confermiamo a Telegram di aver letto, cosi' non li rivediamo al giro dopo.
    if ultimo is not None:
        telegram.prendi_aggiornamenti(ultimo + 1, attesa=0)


def main():
    gestisci_pulsanti()
    memoria = bot.carica_memoria()
    primo_giro = (len(memoria) == 0)
    inviati = bot.un_giro(memoria, primo_giro)
    print(f"Controllo finito. Avvisi inviati: {inviati}.")


if __name__ == "__main__":
    main()
