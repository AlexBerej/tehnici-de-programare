# Laborator: functii, metode si importuri pe web
# Student: Berejnoi Alexandr
# Modulul meu: toate functiile reutilizabile

import csv
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

TIMEOUT = 10  # secunde

# Exercitiu 47
DEFAULT_HEADERS = {"User-Agent": "WebLab-X-Y"}

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


# Exercitiu 44 (fetch, get_status, get_title, security_headers) + 47 (DEFAULT_HEADERS)
def fetch(url: str, timeout: int = TIMEOUT) -> requests.Response:
    """Descarca adresa url (cu antetele din DEFAULT_HEADERS) si returneaza raspunsul."""
    return requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)


def get_status(url: str) -> int:
    """Returneaza codul de stare HTTP pentru adresa url."""
    return fetch(url).status_code


def get_title(html: str) -> Optional[str]:
    """Returneaza titlul paginii (textul dintre <title> si </title>), sau None."""
    lower_html = html.lower()
    tag_start = lower_html.find("<title>")
    if tag_start == -1:
        return None
    start = tag_start + len("<title>")
    end = lower_html.find("</title>")
    return html[start:end].strip()


def security_headers(url: str) -> dict:
    """Verifica cele cinci antete de securitate si returneaza {antet: True/False}."""
    headers = fetch(url).headers
    return {name: name in headers for name in SECURITY_HEADERS}


# Functii din partile anterioare, folosite de site_report
def score_headers(results: dict) -> str:
    """Primeste dictionarul din security_headers si returneaza scorul, de ex. '3/5'."""
    return f"{sum(results.values())}/{len(results)}"


def check_paths(base: str, paths: list) -> dict:
    """Returneaza {cale: cod_de_stare} pentru fiecare cale (None daca cererea esueaza)."""
    results = {}
    for path in paths:
        try:
            results[path] = get_status(urljoin(base, path))
        except requests.RequestException:
            results[path] = None
        time.sleep(1)
    return results


def fetch_robots(base: str) -> Optional[str]:
    """Returneaza textul fisierului /robots.txt sau None daca fisierul lipseste."""
    try:
        response = fetch(urljoin(base, "/robots.txt"))
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
        line = line.split("#")[0].strip()
        if line.lower().startswith("disallow:"):
            value = line.split(":", 1)[1].strip()
            if value:
                paths.append(value)
    return paths


def extract_links(html: str) -> list:
    """Returneaza legaturile (href) din codul HTML, fara duplicate, in ordinea din pagina."""
    return list(dict.fromkeys(re.findall(r'href="([^"]+)"', html)))


def split_links(links: list, domain: str) -> tuple:
    """Imparte legaturile in (interne, externe) in raport cu domeniul dat."""
    base = "https://" + domain
    internal = []
    external = []
    for link in links:
        full_url = urljoin(base, link)
        parts = urlparse(full_url)
        if parts.scheme not in ("http", "https"):
            continue  # mailto:, tel:, javascript: nu sunt pagini web
        if parts.netloc == domain:
            internal.append(full_url)
        else:
            external.append(full_url)
    return internal, external


def resolve(hostname: str) -> Optional[str]:
    """Returneaza adresa IP a domeniului hostname, sau None daca domeniul nu se rezolva."""
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None


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


def redirect_chain(url: str) -> list:
    """Porneste de la varianta http:// a site-ului si returneaza lista redirectionarilor.

    Fiecare element are forma '301 -> https://exemplu.ro/'. Lista este goala daca
    nu exista redirectionari.
    """
    host = urlparse(url).netloc
    response = fetch("http://" + host)
    steps = response.history + [response]
    return [f"{now.status_code} -> {after.url}" for now, after in zip(steps, steps[1:])]


# Exercitiu 49
def save_csv(results: dict, filename: str = "report.csv") -> None:
    """Salveaza rezultatul check_paths in fisierul CSV, cu coloanele path, status, checked_at."""
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["path", "status", "checked_at"])
        for path, status in results.items():
            writer.writerow([path, status, datetime.now().isoformat()])


# Exercitiu 50
def site_report(url: str, filename: str = "report.json") -> dict:
    """Aduna informatii despre site, le afiseaza si le salveaza in report.json.

    Foloseste functiile din acest modul. Intre cereri se face o pauza de o secunda.
    Returneaza dictionarul cu informatiile colectate.
    """
    host = urlparse(url).netloc

    response = fetch(url)
    status = response.status_code
    final_url = response.url
    title = get_title(response.text)
    links = extract_links(response.text)
    internal, external = split_links(links, host)
    time.sleep(1)

    ip = resolve(host)

    redirects = redirect_chain(url)
    time.sleep(1)

    score = score_headers(security_headers(url))
    time.sleep(1)

    try:
        days_left = cert_days_left(host)
    except OSError:  # include si ssl.SSLError si erorile de conectare
        days_left = None

    disallowed = disallowed_paths(fetch_robots(url))

    report = {
        "url": url,
        "status": status,
        "final_url": final_url,
        "title": title,
        "ip": ip,
        "redirects": redirects,
        "security_score": score,
        "cert_days_left": days_left,
        "internal_links": len(internal),
        "external_links": len(external),
        "disallowed": disallowed,
    }

    def line(label: str, value) -> None:
        print(f"{label:<19}{value}")

    print(f"=== Raport site: {url} ===")
    line("Cod de stare:", status)
    line("URL final:", final_url)
    line("Titlu:", title if title is not None else "lipsește")
    line("Adresă IP:", ip if ip is not None else "necunoscută")
    line("Redirecționări:", ", ".join(redirects) if redirects else "fără redirecționări")
    line("Scor securitate:", score)
    if days_left is None:
        line("Certificat:", "indisponibil")
    else:
        line("Certificat:", f"{days_left} de zile rămase")
    line("Legături:", f"{len(internal)} interne, {len(external)} externe")
    line("Căi interzise:", ", ".join(disallowed) if disallowed else "niciuna")

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    print(f"Salvat în {filename}")
    return report


# Exercitiu 46
# Blocul de mai jos ruleaza doar cand fisierul este pornit direct (python webtools.py).
# In acest caz Python pune in variabila __name__ valoarea "__main__". Cand fisierul este
# importat (de ex. din main.py), __name__ este "webtools", conditia este falsa si
# autotestul nu mai ruleaza, deci importul nu face cereri web nedorite
if __name__ == "__main__":
    print("Autotest:", get_status("https://cybercor.org"))