# vinted.py
# Piccolo aiutante per leggere gli annunci da Vinted.

import urllib.request
import urllib.parse
import http.cookiejar
import json
import gzip

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# La "sessione" (con i cookie) verso Vinted. La creiamo alla prima richiesta.
_opener = None


def _nuovo_opener():
    """Apre la homepage di Vinted per ottenere i cookie necessari all'API."""
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    op.addheaders = [
        ("User-Agent", UA),
        ("Accept", "application/json"),
        ("Accept-Language", "it-IT,it;q=0.9"),
    ]
    op.open("https://www.vinted.it/", timeout=20).read()
    return op


def _get_json(url):
    global _opener
    if _opener is None:
        _opener = _nuovo_opener()
    risposta = _opener.open(url, timeout=20)
    grezzo = risposta.read()
    if risposta.headers.get("Content-Encoding") == "gzip":
        grezzo = gzip.decompress(grezzo)
    return json.loads(grezzo)


def cerca(brand, per_page=96):
    """Ritorna una lista di annunci (gia' puliti) per un brand."""
    global _opener
    parametri = urllib.parse.urlencode({
        "page": 1,
        "per_page": per_page,
        "order": "newest_first",
        "search_text": brand["cerca"],
    })
    url = "https://www.vinted.it/api/v2/catalog/items?" + parametri

    try:
        dati = _get_json(url)
    except Exception:
        # Se la sessione e' scaduta, la ricreiamo e riproviamo una volta.
        _opener = None
        dati = _get_json(url)

    risultati = []
    for it in dati.get("items", []):
        brand_annuncio = (it.get("brand_title") or "").lower()
        # Teniamo solo gli annunci del brand giusto.
        if not any(parola in brand_annuncio for parola in brand["ok"]):
            continue
        try:
            prezzo = float((it.get("price") or {}).get("amount"))
        except (TypeError, ValueError):
            continue
        risultati.append({
            "id": str(it.get("id")),
            "titolo": it.get("title") or "",
            "prezzo": prezzo,
            "taglia": it.get("size_title") or "",
            "brand": it.get("brand_title") or "",
            "url": it.get("url") or "",
            "foto": (it.get("photo") or {}).get("url"),
        })
    return risultati


# Se lanci direttamente questo file, fa una prova di ricerca.
if __name__ == "__main__":
    prova = cerca({"nome": "Nike", "cerca": "nike", "ok": ["nike"]}, per_page=10)
    print(f"Trovati {len(prova)} annunci Nike. Primi 3:")
    for a in prova[:3]:
        print(f"  {a['prezzo']:.2f} €  -  {a['titolo'][:60]}")
