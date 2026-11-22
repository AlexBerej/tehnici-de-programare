import argparse, json, os


def citeste_linii(cale):
    with open(cale, encoding="utf-8") as f:
        linii = [l.strip() for l in f
                 if l.strip() and not l.strip().startswith("#")]
    return linii


def nume(cale):
    return cale.rsplit("/")[-1]


GTFO = {"find", "vim.basic", "vim", "nmap", "cp", "bash",
        "less", "awk", "python3", "perl"}


def suid_constatari(cale):
    cai = citeste_linii(cale)
    cai_set = sorted(set(cai))
    return [{"cale": c, "nume": nume(c),
             "risc": "mare" if nume(c) in GTFO else "normal"}
            for c in cai_set]


def sudo_constatari(cale):
    out = []
    for ln in citeste_linii(cale):
        user, drept = ln.split(" : ", 1)
        out.append({"user": user.strip(), "drept": drept.strip(),
                    "risc": "mare" if "NOPASSWD" in drept else "normal"})
    return out


def cron_constatari(cale):
    out = []
    for ln in citeste_linii(cale):
        campuri = ln.split()
        user = campuri[5]
        comanda = " ".join(campuri[6:])
        out.append({"user": user, "comanda": comanda})
    return out


def enumereaza(d):
    return {
        "suid": suid_constatari(os.path.join(d, "suid.txt")),
        "sudo": sudo_constatari(os.path.join(d, "sudo.txt")),
        "cron": cron_constatari(os.path.join(d, "crontab.txt")),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("capturi")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    raport = enumereaza(a.capturi)

    if a.json:
        print(json.dumps(raport, indent=2, ensure_ascii=False))
        return

    # A1 - lista
    cai = citeste_linii(os.path.join(a.capturi, "suid.txt"))
    print("A1  linii SUID:", len(cai))

    # A2 - multimea
    nume_unice = {nume(c) for c in cai}
    print("A2  SUID distincte:", len(nume_unice))

    # A3 - lista de dictionare
    suid = raport["suid"]
    mari = [c for c in suid if c["risc"] == "mare"]
    print("A3  {} SUID, {} cu risc mare: {}".format(
        len(suid), len(mari), sorted(c["nume"] for c in mari)))

    # A5 - rezumat pe categorii
    print("A5  rezumat pe categorii:")
    for categorie, lista in raport.items():
        m = [c for c in lista if c.get("risc") == "mare"]
        print("    {}: {} gasite, {} cu risc mare".format(categorie, len(lista), len(m)))
    utilizatori = {d["user"] for d in raport["sudo"] + raport["cron"]}
    print("    utilizatori implicati:", ", ".join(sorted(utilizatori)))

    with open("enum.json", "w", encoding="utf-8") as f:
        json.dump(raport, f, indent=2, ensure_ascii=False)
    print("Raport salvat in enum.json")


if __name__ == "__main__":
    main()
