# Laborator: functii, metode si importuri pe web
# Student: Berejnoi Alexandr

import time
import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# Exercitiu 9
response = requests.get(BASE_URL, timeout=TIMEOUT)
print(response.status_code)
print(response.ok) 
print(response.url)          
print(response.encoding)     

time.sleep(1)

# Exercitiu 10
response.raise_for_status()  # metoda: nu face nimic daca cererea s-a terminat bine
print("Pagina principala este in regula")

time.sleep(1)

try:
    bad = requests.get(BASE_URL + "/this-page-does-not-exist", timeout=TIMEOUT)
    bad.raise_for_status()  # pentru 404 ridica requests.HTTPError
except requests.HTTPError as e:
    print("Pagina ceruta nu exista:", e)

# Exercitiu 11
for name, value in response.headers.items():
    print(f"{name}: {value}")

print("--- Ex 12 ---")
# Exercitiu 12
print(response.headers.get("Server", "lipsește"))
print(response.headers.get("Content-Type", "lipsește"))
print(response.headers.get("content-type", "lipsește"))
# Cu litere mici se obtine exact aceeasi valoare, pentru ca response.headers
# este un dictionar care ignora diferenta dintre litere mari si mici


# Exercitiu 13
cyber_count = response.text.lower().count("cyber")
print("Cuvantul cyber apare de", cyber_count, "ori")
# Putem inlantui metodele pentru ca response.text este un sir (str), .lower() returneaza
# tot un sir, iar pe acest sir se poate apela imediat urmatoarea metoda count()

# Exercitiu 14
html = response.text
start = html.lower().find("<title>")
#start este indexul de unde incepe tagul
if start == -1:
    print("Pagina nu are tag <title>")
else:
    first = start + len("<title>")
    last = html.lower().find("</title>")
    #print(first)
    #print(last)
    title = html[first:last].strip()
    print("Titlu:", title)

# Exercitiu 15
lines = html.splitlines()
print("Numar de linii:", len(lines))
print("Lungimea celei mai lungi linii:", len(max(lines, key=len)))

# Exercitiu 16
if response.url.startswith("https://"):
    print("Conexiune securizată")
else:
    print("Conexiune nesecurizată")

time.sleep(1)

# Exercitiu 17
response = requests.get("http://cybercor.org", timeout=TIMEOUT)
for step in response.history:
    print(step.status_code, step.url)
print("URL final:", response.url)

time.sleep(1)

# Exercitiu 18
head_response = requests.head(BASE_URL, timeout=TIMEOUT)
time.sleep(1)
get_response = requests.get(BASE_URL, timeout=TIMEOUT)
print("HEAD:", len(head_response.content), "octeti")
print("GET:", len(get_response.content), "octeti")
# HEAD cere doar antetele, serverul nu trimite corpul paginii, deci len(content) este 0
# GET cere si corpul, deci content contine tot codul HTML al paginii.

# Exercitiu 19
for cookie in response.cookies:
    print(cookie.name, cookie.secure)
if not response.cookies:
    print("Niciun cookie setat")

time.sleep(1)

# Exercitiu 20
sesiune = requests.Session()
sesiune.headers.update({"User-Agent": "WebLab-Berejnoi-Alexandr"})
echo = sesiune.get(ECHO_URL + "/headers", timeout=TIMEOUT)
sent_headers = echo.json()["headers"]
print("Header: ", sent_headers)
print("User-Agent trimis:", sent_headers.get("User-Agent", "lipsește"))

# Verificati-va: response.text este un atribut, adica o valoare deja calculata, deci se
# citeste fara paranteze. response.json() este o metoda, adica o actiune: ea analizeaza
# corpul si construieste un dictionar (si poate da eroare daca raspunsul nu este JSON),
# deci trebuie apelata cu paranteze