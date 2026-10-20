# Laborator: 6. Informații invizibile: forensics și steganografie
# Student: Berejnoi Alexandr
#    Utilizare (din radacina la repozitoriu):
#    python -m pytest -q
#    arsenal/__init__.py si arsenal/forensics/__init__.py trebuie sa existe, chiar goale

from arsenal.forensics.decode import (desfa, ghici_strat, desfa_straturi,
                                      sparge_xor, sparge_hash)


def test_base64():
    strat, b = desfa("U2FsdXQ=")
    assert strat == "base64"
    assert b == b"Salut"


def test_ghicire():
    assert ghici_strat("%2Fetc") == "url"
    assert ghici_strat("48656c6c6f") == "hex"
    assert ghici_strat("U2FsdXQ=") == "base64"
    assert ghici_strat("Salut!") == "necunoscut"


def test_hex_si_url():
    assert desfa("48656c6c6f") == ("hex", b"Hello")
    assert desfa("%2Fetc") == ("url", b"/etc")


def test_straturi_multiple():
    # base64(base64(hex("FLAG{x}")))
    import base64
    val = base64.b64encode(base64.b64encode(b"FLAG{x}".hex().encode())).decode()
    straturi, rez = desfa_straturi(val)
    assert straturi == ["base64", "base64", "hex"]
    assert rez == b"FLAG{x}"


def test_cuvant_obisnuit_nu_e_decodat():
    straturi, rez = desfa_straturi("password")
    assert straturi == [] and rez == b"password"


def test_xor():
    clar = b"Salut lume"
    date = bytes(b ^ 0x80 for b in clar)
    assert (0x80, clar) in sparge_xor(date)


def test_hash():
    import hashlib
    h = hashlib.md5(b"dragon").hexdigest()
    assert sparge_hash(h, ["admin", "dragon"]) == "dragon"


def test_xor_cel_mai_bun_primul():
    clar = b"Un text oarecare, destul de lung ca sa fie clar."
    date = bytes(b ^ 0x80 for b in clar)
    k, gasit = sparge_xor(date)[0]
    assert k == 0x80 and gasit == clar