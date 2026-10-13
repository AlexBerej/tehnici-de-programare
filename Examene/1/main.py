from checker import build_url,is_https,show_response,check_site,scan_sites,check_headers,retry_check



# Partea 1: apeluri pentru build
print("=== Partea 1: Funcții ===")

# build_url: path fără / și path cu /
print("Partea 1, build_url (fără /):", build_url("example.com", "login"))
print("Partea 1, build_url (cu /):", build_url("example.com", "/login"))
# caz limită: path cu mai multe segmente
print("Partea 1, build_url (path lung):", build_url("example.com", "api/v1/users"))

# is_https: caz care merge și caz care returnează False
print("Partea 1, is_https (https):", is_https("https://example.com"))
print("Partea 1, is_https (http):", is_https("http://example.com"))
print("Partea 1, is_https (fără schemă):", is_https("example.com"))

# Partea 2: apeluri pentru show
print("\n=== Partea 2: Trimiterea unei cereri ===")

# caz care merge
print("Partea 2, show_response (site valid):")
show_response("https://example.com")

# caz care eșuează: adresa nu există, funcția trebuie să prindă eroarea
print("Partea 2, show_response (site inexistent):")
show_response("http://this-site-does-not-exist.invalid")

# Partea 3: apeluri pentru check
print("\n=== Partea 3: Un verificator reutilizabil ===")

# caz care merge
print("Partea 3, check_site (site valid):", check_site("https://example.com"))
# caz care merge, dar răspunsul este JSON
print("Partea 3, check_site (JSON):", check_site("https://httpbin.org/json"))
# caz care eșuează: cod 404 (cererea reușește, dar statusul nu e 200)
print("Partea 3, check_site (404):", check_site("https://httpbin.org/status/404"))
# caz care eșuează: adresă inexistentă
print(
    "Partea 3, check_site (site inexistent):",
    check_site("http://this-site-does-not-exist.invalid"),
)
# caz limită: prea lent, depășește timeout-ul de 5 secunde
print("Partea 3, check_site (timeout):", check_site("https://httpbin.org/delay/10"))

# Partea 4: apelul scan
print("\n=== Partea 4: Verificarea mai multor site-uri ===")
scan_sites()

# Partea 5: apeluri pentru check
print("\n=== Partea 5: Audit de securitate ===")

# caz: două antete prezente (verifică și ordinea din SECURITY_HEADERS)
print(
    "Partea 5, check_headers (2 antete):",
    check_headers(
        "https://httpbin.org/response-headers"
        "?X-Frame-Options=DENY&X-Content-Type-Options=nosniff"
    ),
)
# caz: antet scris cu litere mici (x-frame-options) trebuie recunoscut
print(
    "Partea 5, check_headers (litere mici):",
    check_headers("https://httpbin.org/response-headers?x-frame-options=DENY"),
)
# caz limită: pagină fără antetele de securitate
print(
    "Partea 5, check_headers (fără antete):",
    check_headers("https://httpbin.org/html"),
)
# caz care eșuează: site inaccesibil
print(
    "Partea 5, check_headers (site inexistent):",
    check_headers("http://this-site-does-not-exist.invalid"),
)

# Partea 6: apeluri pentru retry
print("\n=== Partea 6: Încercări repetate ===")

# 200 -> se oprește imediat, o singură încercare
print(
    "Partea 6, retry_check (200):",
    retry_check("https://httpbin.org/status/200"),
)
# 404 -> sub 500, se oprește imediat (o singură încercare)
print(
    "Partea 6, retry_check (404):",
    retry_check("https://httpbin.org/status/404"),
)
# 500 -> încearcă de 3 ori (valoarea implicită)
print(
    "Partea 6, retry_check (500, implicit 3):",
    retry_check("https://httpbin.org/status/500"),
)
# 500 cu attempts=2 -> încearcă de 2 ori
print(
    "Partea 6, retry_check (500, attempts=2):",
    retry_check("https://httpbin.org/status/500", attempts=2),
)
# site inexistent -> toate încercările eșuează cu eroare de conexiune
print(
    "Partea 6, retry_check (site inexistent):",
    retry_check("http://this-site-does-not-exist.invalid"),
)