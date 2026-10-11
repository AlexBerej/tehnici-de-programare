# Laborator: functii, metode si importuri pe web
# Student: Berejnoi Alexandr

import time
from typing import Optional

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


# Exercitiu 21, 23 si 26 (functia fetch, cu parametru implicit si adnotari de tip)
def fetch(url: str, timeout: int = TIMEOUT) -> requests.Response:
    """Descarca adresa url si returneaza obiectul raspuns (timeout implicit: 10 secunde)."""
    return requests.get(url, timeout=timeout)


# Exercitiu 22
def get_status(url: str) -> int:
    """Returneaza codul de stare HTTP pentru adresa url."""
    return fetch(url).status_code


# Exercitiu 24 si 25
def get_title(html: str) -> Optional[str]:
    """Returneaza titlul paginii (textul dintre <title> si </title>) dintr-un sir HTML.

    Returneaza None daca pagina nu are tag <title>. Functia nu face operatii de retea.
    """
    lower_html = html.lower()
    tag_start = lower_html.find("<title>")
    if tag_start == -1:
        return None
    start = tag_start + len("<title>")
    end = lower_html.find("</title>")
    return html[start:end].strip()


# Exercitiu 27
def page_exists(url: str) -> bool:
    """Returneaza True daca pagina raspunde fara eroare si False in caz contrar.

    Erorile de retea (domeniu inexistent, timeout etc.) nu opresc programul.
    """
    try:
        return fetch(url).ok
    except requests.RequestException:
        return False


# Exercitiu 28
def check_paths(base: str, paths: list) -> dict:
    """Returneaza un dictionar {cale: cod_de_stare} pentru fiecare cale din lista paths.

    Daca o cerere esueaza, valoarea pentru acea cale este None. Intre cereri
    se face o pauza de o secunda.
    """
    results = {}
    for path in paths:
        try:
            results[path] = get_status(base + path)
        except requests.RequestException:
            results[path] = None
        time.sleep(1)
    return results


# Exercitiu 29
def get_header(url: str, name: str, default: str = "lipsește") -> str:
    """Returneaza valoarea antetului name de la adresa url, sau default daca lipseste."""
    return fetch(url).headers.get(name, default)


# Exercitiu 30
def security_headers(url: str) -> dict:
    """Verifica cele cinci antete de securitate si returneaza {antet: True/False}."""
    headers = fetch(url).headers
    return {name: name in headers for name in SECURITY_HEADERS}


# Exercitiu 31
def score_headers(results: dict) -> str:
    """Primeste dictionarul din security_headers si returneaza scorul, de ex. '3/5'."""
    return f"{sum(results.values())}/{len(results)}"


# Exercitiu 32
def fetch_robots(base: str) -> Optional[str]:
    """Returneaza textul fisierului /robots.txt sau None daca fisierul lipseste."""
    try:
        response = fetch(base + "/robots.txt")
    except requests.RequestException:
        return None
    if response.status_code == 200:
        return response.text
    return None


def disallowed_paths(robots_text: Optional[str]) -> list:
    """Returneaza lista valorilor Disallow din textul robots.txt (lista goala pentru None)."""
    if robots_text is None:
        return []
    paths = []
    for line in robots_text.splitlines():
        line = line.split("#")[0].strip()  # eliminam comentariile
        if line.lower().startswith("disallow:"):
            value = line.split(":", 1)[1].strip()
            if value:  # "Disallow:" gol inseamna ca nu este interzis nimic
                paths.append(value)
    return paths


# Exercitiu 33
def response_times(*urls: str) -> dict:
    """Returneaza un dictionar {url: secunde} cu durata cererii pentru fiecare url.

    Daca o cerere esueaza, valoarea este None. Intre cereri se face o pauza de o secunda.
    """
    times = {}
    for url in urls:
        start = time.perf_counter()
        try:
            fetch(url)
            times[url] = time.perf_counter() - start
        except requests.RequestException:
            times[url] = None
        time.sleep(1)
    return times


# Exercitiu 34
def log(message: str, **details) -> None:
    """Afiseaza mesajul urmat de fiecare detaliu, in forma: mesaj | cheie=valoare | ..."""
    parts = [message] + [f"{key}={value}" for key, value in details.items()]
    print(" | ".join(parts))


# Apeluri

# Exercitiu 21
response = fetch(BASE_URL)
print(response.status_code)
time.sleep(1)

# Exercitiu 22
for path in ["/", "/robots.txt", "/sitemap.xml"]:
    print(path, get_status(BASE_URL + path))
    time.sleep(1)

# Exercitiu 23
print(fetch(BASE_URL).status_code)             # cu valoarea implicita (10 secunde)
time.sleep(1)
print(fetch(BASE_URL, timeout=3).status_code)  # cu timeout=3
time.sleep(1)

# Exercitiu 24
print(get_title(response.text))

# Exercitiu 25
help(get_title)

# Exercitiu 26
try:
    print(get_status(123))
except requests.RequestException as e:
    print("Eroare:", type(e).__name__, "-", e)
# Adnotarile de tip nu ne opresc: Python nu le verifica la rulare, ele sunt doar
# documentatie pentru oameni si pentru unelte (de ex. mypy). Apelul get_status(123)
# a pornit normal, iar eroarea vine din requests, care nu stie sa foloseasca "123" ca URL

# Exercitiu 27
print(page_exists(BASE_URL))
print(page_exists("https://this-domain-does-not-exist.invalid"))
time.sleep(1)

# Exercitiu 28
print(check_paths(BASE_URL, ["/", "/robots.txt", "/sitemap.xml"]))

# Exercitiu 29
print(get_header(BASE_URL, name="Server"))
time.sleep(1)

# Exercitiu 30
results = security_headers(BASE_URL)
print(results)
time.sleep(1)

# Exercitiu 31
print(score_headers(results))
print(score_headers(security_headers(BASE_URL)))
time.sleep(1)

# Exercitiu 32
robots = fetch_robots(BASE_URL)
print(disallowed_paths(robots))
print(disallowed_paths(None))  # functioneaza si pentru None
time.sleep(1)

# Exercitiu 33
print(response_times(BASE_URL, BASE_URL + "/robots.txt"))

# Exercitiu 34
log("verificat", url=BASE_URL, status=200)

# Verificati-va: print() doar afiseaza valoarea pe ecran, iar dupa ce functia se termina
# valoarea se pierde, programul nu o poate folosi mai departe. return trimite valoarea
# inapoi celui care a apelat functia, ca sa o poata salva intr-o variabila, sa o
# compare sau sa o dea altei functii (de ex. score_headers(security_headers(url)))