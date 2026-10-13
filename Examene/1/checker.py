import requests

SITES = [
    # Pagini obișnuite (Părțile 2, 3 și 4)
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    # Pagini care eșuează
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    # Anteturi de securitate (Partea 5)
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    # Răspunde aleatoriu cu 200 sau 500 (Partea 6)
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def build_url(host, path):
    """Returnează o adresă completă, de exemplu https://example.com/login."""
    # build_url("example.com", "login") -> "https://example.com/login"
    # build_url("example.com", "/login") -> "https://example.com/login"
    if not path.startswith("/"):
        path = "/" + path
    return f"https://{host}{path}"


def is_https(url):
    """Returnează True dacă adresa începe cu https://, altfel False."""
    return url.startswith("https://")


def show_response(url):
    """Trimite un GET la url și afișează statusul și Content-Type."""
    try:
        r = requests.get(url)
        print(f"URL: {url}")
        print(f"Status: {r.status_code}")
        print(f"Content-Type: {r.headers.get('Content-Type')}")
    except requests.RequestException as e:
        print(f"URL: {url}")
        print(f"Error: {e}")


def check_site(url):
    """Returnează un dicționar cu: status, content_type, length, server."""
    try:
        r = requests.get(url, timeout=5)
        return {
            "status": r.status_code,
            "content_type": r.headers.get("Content-Type"),
            "length": len(r.content),
            "server": r.headers.get("Server", "unknown"),
        }
    except requests.RequestException as e:
        return {"status": None, "error": "Eroare la conectare sau timeout"}


def scan_sites():
    """Verifică toate site-urile din SITES, afișează-le pe cele care merg și un rezumat."""
    rezultate = []
    for site in SITES:
        result = check_site(site)
        rezultate.append((site, result))
        if result.get("status") == 200:
            # Extragem status codul
            status_code = result.get("status")
            print(f"{site}. -> {status_code}, {result.get('length')} octeti")

    # Sortare după length, descrescător
    rezultate.sort(key=lambda x: x[1].get("length", 0), reverse=True)

    # Rezumat
    success_count = sum(1 for _, res in rezultate if res.get("status") == 200)
    failure_count = len(rezultate) - success_count
    print(f"Total sites checked: {len(rezultate)}")
    print(f"Succes : {success_count}")
    print(f"Eroare: {failure_count}")


def check_headers(url):
    """Returnează un dicționar cu: present, missing, score."""
    try:
        r = requests.get(url, timeout=5)
        present = [header for header in SECURITY_HEADERS if header in r.headers]
        missing = [header for header in SECURITY_HEADERS if header not in r.headers]
        score = int((len(present) / len(SECURITY_HEADERS)) * 100) if SECURITY_HEADERS else 0
        return {
            "present": present,
            "missing": missing,
            "score": score
        }
    except requests.RequestException as e:
        return {"status": None, "error": "Eroare la conectare sau timeout"}


def retry_check(url, attempts=3):
    """Încearcă de cel mult `attempts` ori; returnează un dicționar cu: status, attempts."""
    last_status = None
    for attempt in range(1, attempts + 1):
        try:
            r = requests.get(url, timeout=5)
            last_status = r.status_code
            if last_status < 500:
                return {"status": last_status, "attempts": attempt}
        except requests.RequestException as e:
            last_status = None
            if attempt == attempts:
                return {"status": None, "attempts": attempt, "error": "Eroare la conectare sau timeout"}
    return {"status": last_status, "attempts": attempts}

# Testare
#print(build_url("example.com", "test"))
#print(is_https("http://example.com"))

# Test show_response
#show_response("https://example.com")

# Test check_site
for site in SITES:
    break # Scoateti break pentru test
    result = check_site(site)
    print(f"Site: {site}, Result: {result}")

# Test scan_sites
#scan_sites()

#Test check_headers
for site in SITES:
    break 
    result = check_headers(site)
    #Afisam elementele din dictionar pe linii
    print(f"Site: {site}")
    for key, value in result.items():
        print(f"  {key}: {value}")  


# Test retry_check
for site in SITES:
    break
    result = retry_check(site, attempts=3)
    print(f"Site: {site}, Rezultat: {result}")