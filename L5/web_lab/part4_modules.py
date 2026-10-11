# Laborator: functii, metode si importuri pe web
# Student: Berejnoi Alexandr

import hashlib
import json
import re
import socket
import ssl
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


def fetch(url: str, timeout: int = TIMEOUT) -> requests.Response:
    """Descarca adresa url si returneaza obiectul raspuns."""
    return requests.get(url, timeout=timeout)


# Exercitiu 35
parsed = urlparse("https://cybercor.org/path?x=1#top")
print(parsed.scheme)
print(parsed.netloc)
print(parsed.path)
print(parsed.query)
print(parsed.fragment)

# Exercitiu 36
for link in ["/about", "contact.html", "../index.html"]:
    print(link, "->", urljoin(BASE_URL, link))


# Exercitiu 37
def extract_links(html: str) -> list:
    """Returneaza legaturile (href) din codul HTML, fara duplicate, in ordinea din pagina."""
    links = re.findall(r'href="([^"]+)"', html)
    return list(dict.fromkeys(links))  # dict pastreaza ordinea si elimina duplicatele


page = fetch(BASE_URL)
links = extract_links(page.text)
print(len(links), "legaturi unice")
print(links)


# Exercitiu 38
def split_links(links: list, domain: str) -> tuple:
    """Imparte legaturile in doua liste: (interne, externe) in raport cu domeniul dat.

    Legaturile care nu sunt pagini web (mailto:, tel:, javascript:) sunt ignorate.
    """
    base = "https://" + domain
    internal = []
    external = []
    for link in links:
        full_url = urljoin(base, link)
        parts = urlparse(full_url)
        if parts.scheme not in ("http", "https"):
            continue
        if parts.netloc == domain:
            internal.append(full_url)
        else:
            external.append(full_url)
    return internal, external


internal_links, external_links = split_links(links, "cybercor.org")
print(len(internal_links), "interne,", len(external_links), "externe")


# Exercitiu 39
class ImageFinder(HTMLParser):
    """Parser HTML care colecteaza atributul src al fiecarui tag <img>."""

    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":  # HTMLParser transforma numele tag-urilor in litere mici
            src = dict(attrs).get("src")
            if src:  # ignoram <img> fara src
                self.images.append(src)


test_html = """
<html><body>
  <img src="/logo.png" alt="Logo">
  <IMG SRC="poza.jpg">
  <img alt="imagine fără src">
  <img src="https://cdn.example.com/banner.webp" />
  <a href="/despre">Aceasta nu este o imagine</a>
</body></html>
"""

finder = ImageFinder()
finder.feed(test_html)
print(finder.images)

assert finder.images == [
    "/logo.png",                            # imagine obisnuita
    "poza.jpg",                             # tag scris cu majuscule
    "https://cdn.example.com/banner.webp",  # tag care se inchide singur
], "Parserul nu a găsit exact imaginile așteptate"
print("Testul a trecut!")

time.sleep(1)

response = requests.get(BASE_URL, timeout=TIMEOUT)
finder = ImageFinder()
finder.feed(response.text)
print(len(finder.images), "imagini găsite")
for src in finder.images:
    print(src)
print("Tag-uri <img> in text:", response.text.lower().count("<img"))
# Daca cele doua numere difera, uitati-va in sursa paginii (Ctrl+U): unele <img> pot
# lipsi de src (de ex. imagini incarcate cu JavaScript, atribut data-src)


# Exercitiu 40
def page_fingerprint(url: str) -> str:
    """Returneaza amprenta SHA-256 (in hexazecimal) a continutului paginii."""
    response = fetch(url)
    return hashlib.sha256(response.content).hexdigest()


first = page_fingerprint(BASE_URL)
time.sleep(1)
second = page_fingerprint(BASE_URL)
print(first)
print(second)
print("Identice:", first == second)
# Amprentele ar fi diferite daca pagina se schimba intre cele doua cereri: continut
# dinamic (data si ora, contor de vizitatori, reclame, token-uri sau nonce-uri
# generate la fiecare cerere), o actualizare a site-ului sau servere diferite
# (balansare de incarcare) care trimit versiuni diferite


# Exercitiu 41
def save_headers(url: str, filename: str = "headers.json") -> dict:
    """Salveaza antetele paginii in fisierul JSON filename si le incarca inapoi."""
    response = fetch(url)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dict(response.headers), file, indent=2)
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


time.sleep(1)
loaded = save_headers(BASE_URL)
first_name = next(iter(loaded))
print(first_name + ":", loaded[first_name])


# Exercitiu 42
def resolve(hostname: str) -> Optional[str]:
    """Returneaza adresa IP a domeniului hostname, sau None daca domeniul nu se rezolva."""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None


print("Adresa IP:", resolve("cybercor.org"))


# Exercitiu 43
def cert_days_left(hostname: str) -> int:
    """Returneaza cate zile mai sunt pana la expirarea certificatului SSL al domeniului."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
            cert = secure_sock.getpeercert()
    expires_at = datetime.fromtimestamp(
        ssl.cert_time_to_seconds(cert["notAfter"]), tz=timezone.utc
    )
    return (expires_at - datetime.now(timezone.utc)).days


print("Zile pana la expirarea certificatului:", cert_days_left("cybercor.org"))
