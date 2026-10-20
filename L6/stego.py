# Laborator: 6. Informații invizibile: forensics și steganografie
# Student: Berejnoi Alexandr
#    Utilizare (din radacina depozitului):
#    python stego.py
#    Ascunde un mesaj in probe/foto.jpg -> stego.png, apoi il dezvaluie

from PIL import Image

STOP = b"\x00"      # marcheaza sfarsitul mesajului


# B5
def ascunde(cale_gazda, mesaj, cale_iesire="stego.png"):
    """Scrie mesajul (bytes) in ultimul bit (LSB) al fiecarui canal R, G, B"""
    img = Image.open(cale_gazda).convert("RGB")
    canale = bytearray(img.tobytes())              # R G B R G B ...

    # mesaj + terminator -> lista de biti, cel mai semnificativ intai
    biti = [(octet >> (7 - j)) & 1 for octet in mesaj + STOP for j in range(8)]
    if len(biti) > len(canale):
        raise ValueError("mesaj prea lung pentru imagine")

    for i, bit in enumerate(biti):
        canale[i] = (canale[i] & ~1) | bit         # schimbam doar ultimul bit

    Image.frombytes("RGB", img.size, bytes(canale)).save(cale_iesire)   # PNG: fara pierdere
    return len(biti)


# B6
def dezvaluie(cale_stego):
    """Inversul: aduna LSB-urile, le grupeaza cate 8 in octeti, stop la 0"""
    canale = Image.open(cale_stego).convert("RGB").tobytes()
    mesaj = bytearray()
    for i in range(0, len(canale) - 7, 8):
        octet = 0
        for canal in canale[i:i + 8]:
            octet = (octet << 1) | (canal & 1)     # adaugam ultimul bit
        if octet == 0:                             # terminatorul
            break
        mesaj.append(octet)
    return bytes(mesaj)


if __name__ == "__main__":
    secret = b"FLAG{ascuns_in_pixeli}"
    n = ascunde("probe/foto.jpg", secret, "stego.png")
    print(f"ascuns: {len(secret)} octeti ({n} biti) in stego.png")

    # imaginea se schimba cu cel mult 1 pe canal (invizibil)
    a = Image.open("probe/foto.jpg").convert("RGB").tobytes()
    b = Image.open("stego.png").convert("RGB").tobytes()
    print("diferenta maxima pe un canal:", max(abs(x - y) for x, y in zip(a, b)))

    print("dezvaluit:", dezvaluie("stego.png").decode())