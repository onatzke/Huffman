import os

def heapify(Q, n, i):
    smallest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and Q[left]['czestosc'] < Q[smallest]['czestosc']:
        smallest = left
    if right < n and Q[right]['czestosc'] < Q[smallest]['czestosc']:
        smallest = right

    if smallest != i:  # jeśli najmniejszy element nie jest obecnym węzłem, zamieniają się one miejscami
        Q[i], Q[smallest] = Q[smallest], Q[i]
        heapify(Q, n, smallest)

def MIN_HEAP(Q):
    n = len(Q)

    #print("\nBudowanie kopca min z:")
    #for element in Q:
        #print(f"{element['znak']} {element['czestosc']}")

    for i in range(n // 2 - 1, -1, -1):
        heapify(Q, n, i)

def INSERT(Q, element):
    Q.append(element)
    #print(f"\nINSERT - {element['znak']} {element['czestosc']}")
    MIN_HEAP(Q)

def EXTRACT_MIN(Q):
    if len(Q) == 0:
        return None
    if len(Q) == 1:
        return Q.pop()

    min_element = Q[0]
    Q[0] = Q.pop() # usuwanie i zwracanie najmnejszego elementu z kopca

    #print(f"\nmin_element - {min_element['znak']} {min_element['czestosc']}")

    if Q:
        MIN_HEAP(Q)
    return min_element

def tworzenie_wezla(znak=None, czestosc=0, lewy=None, prawy=None):
    return {
        'znak': znak,
        'czestosc': czestosc,
        'lewy': lewy,
        'prawy': prawy
    }

def tworzenie_drzewa(czestotliwosci):
    Q = [] # kolejka priorytetowa = kopiec min
    for znak, czestosc in czestotliwosci.items():
        wezel = tworzenie_wezla(znak, czestosc)
        INSERT(Q, wezel)

    while len(Q) > 1:
        lewy = EXTRACT_MIN(Q)
        prawy = EXTRACT_MIN(Q)

        nowy_wezel = tworzenie_wezla(
            czestosc=lewy['czestosc'] + prawy['czestosc'],
            lewy=lewy,
            prawy=prawy
        )
        #print(f"\nNowy węzeł: {nowy_wezel['czestosc']}")
        INSERT(Q, nowy_wezel)

    korzen = Q[0]
    return korzen

def zliczenie_znakow(tekst):
    czestosc = {} # liczba wystąpień każdego znaku
    for znak in tekst:
        if znak in czestosc:
            czestosc[znak] += 1
        else:
            czestosc[znak] = 1
    return czestosc

def kodowanie(korzen, kod='', kody=None):
    if kody is None:
        kody = {}
    if korzen is not None:
        if korzen['znak'] is not None:
            kody[korzen['znak']] = kod
        if korzen['lewy']:
            # rekurencja przez lewe poddrzewo i dopisanie 0 do kodu
            kodowanie(korzen['lewy'], kod + '0', kody)
        if korzen['prawy']:
            # rekurencja przez prawe poddrzewo i dopisanie 1 do kodu
            kodowanie(korzen['prawy'], kod + '1', kody)
    return kody

def zapisanie_pliku(nazwa_pliku, kody, zakodowany_tekst):
    nazwa_wyjsciowa = f"{nazwa_pliku[:-4]}-zakodow.txt"

    naglowek = ""
    for znak, kod in (kody.items()):
        if znak == ' ':
            znak = "\\s"
        elif znak == '\n':
            znak = "\\n"
        elif znak == '\t':
            znak = "\\t"
        naglowek += f"{znak}={kod} "
    naglowek = naglowek.rstrip() + "\n"

    dodatkowe_zera = (8 - len(zakodowany_tekst) % 8) % 8 # dopełnienie dodatkowymi zerami do pełnych bajtów
    for i in range(dodatkowe_zera):
        zakodowany_tekst += "0"

    zakodowane = bytearray() # zamiana bitów na bajty
    for i in range(0, len(zakodowany_tekst), 8):
        bajt = zakodowany_tekst[i:i + 8]
        bajt_wartosc = int(bajt, 2)
        zakodowane.append(bajt_wartosc)

    plik = open(nazwa_wyjsciowa, 'wb')
    plik.write(naglowek.encode('utf-8'))
    plik.write(zakodowane)
    plik.close()

    return nazwa_wyjsciowa

def wczytaj_naglowek(nazwa_pliku):
    plik = open(nazwa_pliku, 'rb') # rb oznacza otwieranie pliku w trybie binarnym
    dane = plik.read()
    koniec_naglowka = dane.find(b'\n') # pierwszy enter oznacza koniec nagłówka
    naglowek_linia = dane[:koniec_naglowka].decode('utf-8')
    dane_binarne = dane[koniec_naglowka + 1:] # dane binarne to pozostała zawartość pliku po pierwszym enterze
    plik.close()

    kody = {}
    for para in naglowek_linia.split():
        if '=' in para:
            znak, kod = para.split('=')
            if znak == '\\s':
                znak = ' '
            elif znak == '\\n':
                znak = '\n'
            elif znak == '\\t':
                znak = '\t'
            kody[kod] = znak
    return kody, dane_binarne

def dekoduj_tekst(dane_binarne, kody):
    bity = ''.join(format(bajt, '08b') for bajt in dane_binarne)
    tekst = ''
    aktualny_kod = ''
    for bit in bity:
        aktualny_kod += bit
        if aktualny_kod in kody:
            tekst += kody[aktualny_kod]
            aktualny_kod = ''
    return tekst

def przetwarzanie_pliku(nazwa_pliku, tryb):
    try:
        if tryb == 'zakoduj':
            plik = open(nazwa_pliku, 'r', encoding='utf-8')
            tekst = plik.read()
            plik.close()

            czestotliwosci = zliczenie_znakow(tekst)
            drzewo = tworzenie_drzewa(czestotliwosci)
            kody = kodowanie(drzewo)
            zakodowany_tekst = ''.join(kody[znak] for znak in tekst)
            nazwa_wyjsciowa = zapisanie_pliku(nazwa_pliku, kody, zakodowany_tekst)

            print(f"\nPlik zakodowany zapisany jako: {nazwa_wyjsciowa}")

        elif tryb == 'dekoduj':
            kody, dane_binarne = wczytaj_naglowek(nazwa_pliku)
            zdekodowany_tekst = dekoduj_tekst(dane_binarne, kody)

            nazwa_wyjsciowa = f"{nazwa_pliku[:-12]}-dekodow.txt"
            plik = open(nazwa_wyjsciowa, 'w', encoding='utf-8')
            plik.write(zdekodowany_tekst)
            plik.close()

            print(f"\nPlik zdekodowany zapisany jako: {nazwa_wyjsciowa}")

    except Exception as e:
        print(f"Błąd: {str(e)}")


while True:
    wybor = input("\nzakoduj - [z], dekoduj - [d] lub wyłącz program - [w]: ").strip().lower()

    if wybor == 'w':
        break
    elif wybor in ['z', 'd']:
        if wybor == 'z':
            tryb = 'zakoduj'
        else:
            tryb = 'dekoduj'

        while True:
            if tryb == 'zakoduj':
                nazwa_pliku = input(f"Podaj nazwę pliku do zakodowania: ").strip()
            else:
                nazwa_pliku = input(f"Podaj nazwę pliku do zdekodowania: ").strip()
            if os.path.exists(nazwa_pliku):
                przetwarzanie_pliku(nazwa_pliku, tryb)
                break
            else:
                print("Nie ma takiego pliku")
    else:
        print("Wybierz [z], [d] lub [w]")
