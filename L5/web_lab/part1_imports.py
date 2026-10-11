# Laborator: functii, metode si importuri pe web
# Student: Berejnoi Alexandr

import time  # folosit pentru pauzele dintre cereri si pentru exercitiul 7

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# Exercitiu 1
import requests
print(requests.__version__)

import urllib.request

# requests este un modul extern, care trebuie instalat separat cu pip install requests
# iar urllib este un modul din biblioteca standard, care vine instalat odata cu Python

time.sleep(1)

# Exercitiu 2
# Avantajul stilului "import requests": se vede clar de unde vine functia (requests.get)
# si numele get nu intra in conflict cu alte nume din program
print(requests.get(BASE_URL, timeout=TIMEOUT).status_code)

time.sleep(1)

# Avantajul stilului "from requests import get": codul este mai scurt, scriem doar get
from requests import get
print(get(BASE_URL, timeout=TIMEOUT).status_code)

time.sleep(1)

# Exercitiu 3
import requests as rq
# Un alias face codul mai usor de citit cand modulul are un nume lung sau cand alias-ul
# este unul cunoscut de toata lumea (np pentru numpy, pd pentru pandas)
# Il face mai greu de citit cand este un alias criptic sau nestandard (rq pentru requests),
# pentru ca cititorul trebuie sa ghiceasca la ce se refera
print(rq.get(BASE_URL, timeout=TIMEOUT).status_code)

time.sleep(1)

# Exercitiu 4
val = urllib.request.urlopen(BASE_URL, timeout=TIMEOUT)
print(val.status)
# .read() returneaza bytes, deci decodam raspunsul in UTF-8 pentru a-l afisa ca text
print(val.read().decode("utf-8")[:200])

# Exercitiu 5
print(dir(requests))
# get — functie
# Session — clasa
# adapters — modul

# Exercitiu 6
help(requests.get)
# parametrul care seteaza timpul maxim de asteptare este timeout (in secunde)
time.sleep(1)
print(get(BASE_URL, timeout=TIMEOUT).status_code)

time.sleep(1)

# Exercitiu 7
start = time.perf_counter()
response = get(BASE_URL, timeout=TIMEOUT)
end = time.perf_counter()

print(response.status_code)
print("Durata cu perf_counter:", end - start, "secunde")
print("Durata cu response.elapsed:", response.elapsed.total_seconds(), "secunde")
# perf_counter masoara tot timpul, inclusiv conectarea si citirea raspunsului,
# iar response.elapsed masoara doar intervalul dintre trimiterea cererii si primirea
# antetelor raspunsului, deci de obicei are o valoare putin mai mica

# Exercitiu 8
try:
    import bs4
    print("bs4 este instalat")
except ImportError:
    print("Instalați modulul cu: pip install beautifulsoup4")

# Verificati-va: modul, pachet, biblioteca
# modul = un singur fisier .py care contine cod reutilizabil
# pachet = un director cu mai multe module (are un fisier __init__.py)
# biblioteca = termen general pentru o colectie de cod reutilizabil (poate fi modul sau pachet)