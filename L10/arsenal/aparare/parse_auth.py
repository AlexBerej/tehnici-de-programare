import re
import sys
from collections import Counter

TIPAR = re.compile(r"Failed password for (?:invalid user )?(\S+) from (\S+) port")


def esec(linie):
    """Intoarce (user, ip) daca linia e un esec de autentificare, altfel None."""
    m = TIPAR.search(linie)
    if m is None:
        return None
    return (m.group(1), m.group(2))


def citeste_esecuri(cale):
    """Parcurge jurnalul si strange esecurile intr-o lista de dictionare.
    Un rand stricat e sarit; un fisier lipsa da un mesaj clar, nu un traceback."""
    esecuri = []
    try:
        f = open(cale, encoding="utf-8")
    except FileNotFoundError:
        print("nu gasesc", cale)
        return esecuri
    with f:
        for linie in f:
            r = esec(linie)
            if r is not None:
                esecuri.append({"user": r[0], "ip": r[1]})
    return esecuri


def pe_ip(esecuri):
    """Intoarce un Counter al adreselor din lista de esecuri."""
    return Counter(e["ip"] for e in esecuri)


def main():
    cale = sys.argv[1] if len(sys.argv) > 1 else "arsenal/aparare/start/auth.log"
    esecuri = citeste_esecuri(cale)
    counts = pe_ip(esecuri)
    print("Esecuri de autentificare:", len(esecuri))
    for ip, n in counts.most_common():
        print(f"  {ip}: {n}")


if __name__ == "__main__":
    main()
