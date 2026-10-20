# Laborator: 6. Informații invizibile: forensics și steganografie
# Student: Berejnoi Alexandr
#    Utilizare (din radacina depozitului):
#    python forensics.py
#    Lucreaza doar pe fisierele generate in probe/

import re
import zipfile
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS

GPS = 0x8825      # tag-ul blocului GPS (34853)


# B1
SEMNATURI = [
    (b"%PDF", "pdf"),
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpeg"),
    (b"GIF8", "gif"),
    (b"PK\x03\x04", "zip/docx"),
]


def tip_real(cale):
    """Tipul fisierului dupa primii octeti, nu dupa extensie"""
    with open(cale, "rb") as f:        # "rb" e obligatoriu pentru binare
        cap = f.read(8)
    for semn, nume in SEMNATURI:
        if cap.startswith(semn):
            return nume
    if all(32 <= c < 127 for c in cap):
        return "text (ascii)"
    return cap.hex()                   # necunoscut: octetii in hex


# B2
def strings(cale, minim=4):
    """Sirurile de caractere imprimabile (ca utilitarul strings)"""
    date = Path(cale).read_bytes()
    return [m.decode() for m in re.findall(rb"[ -~]{%d,}" % minim, date)]


# B3
def in_grade_zecimale(dms, ref):
    """(grade, minute, secunde) + emisfera -> grade zecimale"""
    g, m, s = (float(x) for x in dms)
    val = g + m / 60 + s / 3600
    return -val if ref in ("S", "W") else val      # S si W sunt negative


def exif_si_gps(cale):
    """Intoarce (exif ca dict cu nume, (lat, lon) sau None)"""
    exif = Image.open(cale).getexif()
    date = {TAGS.get(tag, tag): val for tag, val in exif.items()}

    gps = exif.get_ifd(GPS)
    if not gps:
        return date, None
    # cheile GPS: 1 = N/S, 2 = latitudine, 3 = E/W, 4 = longitudine
    return date, (in_grade_zecimale(gps[2], gps[1]), in_grade_zecimale(gps[4], gps[3]))


# B4
def carving_zip(cale_png, cale_zip="gasit.zip"):
    """Gaseste ZIP-ul lipit dupa sfarsitul PNG-ului, il salveaza si il citeste"""
    date = Path(cale_png).read_bytes()
    iend = date.find(b"IEND")
    start = iend + 8 if iend != -1 else 0          # IEND + 4 octeti CRC
    i = date.find(b"PK\x03\x04", start)            # cautam abia dupa PNG
    if i == -1:
        return None

    Path(cale_zip).write_bytes(date[i:])
    print(f"arhiva extrasa de la octetul {i} ({len(date) - i} octeti) -> {cale_zip}")
    with zipfile.ZipFile(cale_zip) as z:
        return {nume: z.read(nume).decode(errors="replace") for nume in z.namelist()}


if __name__ == "__main__":
    print("== B1. Tipul real ==")
    for f in ["probe/foto.jpg", "probe/ascuns.png", "probe/mesaj.txt", "probe/xor.bin"]:
        print(f"  {f:<20} -> {tip_real(f)}")

    print("\n== B2. strings din ascuns.png (ultimele 5) ==")
    for s in strings("probe/ascuns.png")[-5:]:
        print("  ", s)

    print("\n== B3. EXIF din foto.jpg ==")
    exif, coord = exif_si_gps("probe/foto.jpg")
    for k, v in exif.items():
        print(f"  {k} = {v}")
    if coord:
        lat, lon = coord
        print(f"  GPS: {lat:.6f}, {lon:.6f}")
        print(f"  harta: https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}#map=15/{lat:.4f}/{lon:.4f}")

    print("\n== B4. Carving din ascuns.png ==")
    continut = carving_zip("probe/ascuns.png")
    for nume, text in (continut or {}).items():
        print(f"  in arhiva: {nume} -> {text.strip()}")