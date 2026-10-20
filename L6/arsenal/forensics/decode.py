# Laborator: 6. Informații invizibile: forensics și steganografie
# Student: Berejnoi Alexandr
#    Utilizare:
#    python arsenal/forensics/decode.py "U2FsdXQ="
#    python arsenal/forensics/decode.py probe/mesaj.txt --fisier
#    python arsenal/forensics/decode.py probe/xor.bin --fisier --xor
#    python arsenal/forensics/decode.py probe/hashuri.txt --fisier --hash probe/wordlist.txt

import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

# fisa.json langa decode.py
FISA = Path(__file__).resolve().with_name("fisa.json")


# A1
def salut():
    s = "Salut"
    b = s.encode()                 # str -> bytes
    print(b, b[0])                 # b'Salut' 83
    h = b.hex()                    # bytes -> text hex
    print(h, bytes.fromhex(h))     # 53616c7574 b'Salut'


# A2
URL = re.compile(r"%[0-9a-fA-F]{2}")
HEX = re.compile(r"[0-9a-fA-F]+")
B64 = re.compile(r"[A-Za-z0-9+/]+={0,2}")


def ghici_strat(s):
    """Clasifica dupa forma. Ordinea conteaza: url, hex, base64"""
    s = s.strip()
    if URL.search(s):
        return "url"
    if HEX.fullmatch(s) and len(s) % 2 == 0:
        return "hex"
    if B64.fullmatch(s) and len(s) % 4 == 0:
        return "base64"
    return "necunoscut"


# A3
def desfa(s):
    """Desface UN strat. Intoarce (strat, rezultat_bytes)."""
    s = s.strip()
    strat = ghici_strat(s)
    try:
        if strat == "base64":
            return strat, base64.b64decode(s, validate=True)
        if strat == "hex":
            return strat, bytes.fromhex(s)
        if strat == "url":
            return strat, unquote(s).encode()
    except ValueError:             # binascii.Error e in ValueError
        pass
    return "necunoscut", s.encode()


# A4
def citibil(b):
    """True daca toti octetii sunt {32..126} sau spatii albe uzuale."""
    return len(b) > 0 and all(32 <= c < 127 or c in (9, 10, 13) for c in b)


def desfa_straturi(val, max_pasi=8):
    """Desface in bucla, cat timp stratul e recunoscut si da text citibil"""
    straturi = []
    curent = val.strip()
    for _ in range(max_pasi):          # max_pasi: sa nu intram in loop infinit
        strat, b = desfa(curent)
        # fara "citibil", un cuvant ca "password" ar fi decodat in garbage
        if strat == "necunoscut" or not citibil(b):
            break
        straturi.append(strat)
        curent = b.decode()
    return straturi, curent.encode()


# A5
def scor_text(b):
    """Cat de mult seamana cu text: ponderea literelor si a spatiilor"""
    return sum(chr(c).isalpha() or c == 32 for c in b) / len(b)


def sparge_xor(date):
    """Incearca cele 256 de chei. Intoarce [(cheie, clar)], cel mai bun primul"""
    gasite = []
    for k in range(256):
        clar = bytes(b ^ k for b in date)
        if citibil(clar):
            gasite.append((k, clar))
    # mai multe chei pot da text imprimabil, deci le ordonam dupa scor
    gasite.sort(key=lambda x: scor_text(x[1]), reverse=True)
    return gasite


# A6
ALGO = {32: "md5", 40: "sha1", 64: "sha256"}      # algoritmul dupa lungime


def algoritm(h):
    return ALGO.get(len(h.strip()))


def sparge_hash(tinta, cuvinte):
    """Hashuieste fiecare cuvant si compara cu tinta. Intoarce parola sau None"""
    tinta = tinta.strip().lower()
    alg = algoritm(tinta)
    if alg is None:
        return None
    for cuv in cuvinte:
        cuv = cuv.strip()
        if hashlib.new(alg, cuv.encode()).hexdigest() == tinta:
            return cuv
    return None


# A7
def main():
    p = argparse.ArgumentParser(description="Decoder universal: straturi, XOR, hash")
    p.add_argument("intrare", help="un sir sau o cale (cu --fisier)")
    p.add_argument("--fisier", action="store_true", help="intrarea e o cale de fisier")
    p.add_argument("--xor", action="store_true", help="sparge XOR cu cheie de un octet")
    p.add_argument("--hash", metavar="WORDLIST", help="sparge hash-uri cu dictionarul dat")
    a = p.parse_args()

    # sirul sau continutul fisierului, ca octeti
    date = Path(a.intrare).read_bytes() if a.fisier else a.intrare.encode()

    if a.xor:
        gasite = sparge_xor(date)
        if not gasite:
            print("nicio cheie nu da text citibil")
            return
        k, clar = gasite[0]
        print(f"cheie: {k} (0x{k:02x})  ->  {clar.decode()}")
        print(f"({len(gasite)} chei dau octeti imprimabili; o afisez pe cea mai probabila)")
        fisa = {"strat": "xor-1-octet", "cheie": k, "rezultat": clar.decode()}

    elif a.hash:
        cuvinte = Path(a.hash).read_text(encoding="latin1").splitlines()
        sparte = {}
        for h in date.decode().split():        # un hash pe linie
            parola = sparge_hash(h, cuvinte)
            print(f"{h}  [{algoritm(h)}]  ->  {parola or 'negasit'}")
            sparte[h] = parola
        fisa = {"strat": "hash-dictionar", "rezultat": sparte}

    else:
        straturi, rez = desfa_straturi(date.decode(errors="replace"))
        strat = " -> ".join(straturi) or "necunoscut"
        print("straturi:", strat)
        print("rezultat:", rez.decode(errors="replace"))
        fisa = {"strat": strat, "rezultat": rez.decode(errors="replace")}

    FISA.write_text(json.dumps(fisa, ensure_ascii=False, indent=2), encoding="utf-8")
    print("fisa salvata:", FISA)


if __name__ == "__main__":
    main()