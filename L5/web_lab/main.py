# Laborator: functii, metode si importuri pe web
# Student: Berejnoi Alexandr

import argparse
import time

import webtools  # Exercitiu 44: importam tot modulul si scriem webtools.nume
from webtools import get_title, security_headers  # Exercitiu 45: importam doar numele dorite
from webtools import DEFAULT_HEADERS  # Exercitiu 47: importam constanta

# Exercitiu 45
# Daca main.py ar avea si o functie proprie numita get_title, ea ar inlocui functia
# importata: ultima definitie a unui nume ramane valabila si Python nu da nicio eroare.
# Apelurile get_title(...) ar rula functia din main.py, iar functia din webtools ar putea
# fi folosita doar ca webtools.get_title(...). Din acest motiv, importul "from ... import"
# poate crea confuzii cand numele se repeta


def main() -> None:
    """Citeste adresa din linia de comanda si ruleaza verificarile pe acea adresa."""
    # Exercitiu 48
    parser = argparse.ArgumentParser(description="Raport despre un site web")
    parser.add_argument("url", help="adresa site-ului, de ex. https://cybercor.org")
    args = parser.parse_args()
    url = args.url
    if not url.startswith(("http://", "https://")):
        parser.error("adresa trebuie sa inceapa cu http:// sau https://")

    # Exercitiu 44
    page = webtools.fetch(url)
    print("Titlu (webtools.get_title):", webtools.get_title(page.text))
    time.sleep(1)

    # Exercitiu 45
    print("Titlu (get_title importat):", get_title(page.text))
    print("Antete de securitate:", security_headers(url))
    time.sleep(1)

    # Exercitiu 47
    print("DEFAULT_HEADERS:", DEFAULT_HEADERS)

    # Exercitiu 49
    results = webtools.check_paths(url, ["/", "/robots.txt", "/sitemap.xml"])
    webtools.save_csv(results, "report.csv")
    print("Salvat in report.csv")
    print()

    # Exercitiu 50
    webtools.site_report(url)


if __name__ == "__main__":
    main()