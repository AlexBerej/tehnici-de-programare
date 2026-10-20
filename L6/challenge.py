# Laborator: 6. Informații invizibile: forensics și steganografie
# Student: Berejnoi Alexandr
#    Varful salii: challenge.bin = base64 peste XOR cu cheie de un octet
#    Utilizare (din radacina depozitului):
#    python challenge.py

import base64
import hashlib
import re
from pathlib import Path
from arsenal.forensics.decode import sparge_xor

# md5-ul textului clar, din indiciu
hint = Path("probe/challenge_hint.txt").read_text()
md5_asteptat = re.search(r"[0-9a-f]{32}", hint).group()

# 1) scoatem base64 -> octeti inca ilizibili (sunt XOR-ati)
interior = base64.b64decode(Path("probe/challenge.bin").read_bytes())
print("dupa base64:", interior)

# 2) incercam cheile XOR, 3) verificam fiecare candidat cu md5
for k, clar in sparge_xor(interior):
    ok = hashlib.md5(clar).hexdigest() == md5_asteptat
    print(f"cheie 0x{k:02x}: {clar.decode()}  md5 {'POTRIVIT' if ok else 'nu'}")
    if ok:
        break