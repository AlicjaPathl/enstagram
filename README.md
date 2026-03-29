🚀 Enstagram Cyber Lab - Instrukcja Uruchomienia
Ten projekt to poligon doświadczalny do nauki pentestingu. Poniżej znajdziesz kroki, które pozwolą Ci postawić całe środowisko w kilka minut.

🛠️ Krok 1: Przygotowanie plików
Upewnij się, że w folderze projektu masz następujące pliki:

main.py (serwer Flask)

maro_shell.py (konsola sterowania)

Makefile (skrypt automatyzacji)

Dockerfile (konfiguracja kontenera)

.env (tutaj wpisz swoją flagę)

📦 Krok 2: Instalacja i budowanie
Pierwsze uruchomienie wymaga zainstalowania bibliotek i zbudowania obrazu Docker. Wykonaj komendę:

Bash
sudo make setup
Ta komenda stworzy wirtualne środowisko .venv i pobierze obraz Pythona.

🎬 Krok 3: Odpalenie laboratorium
Aby uruchomić serwer i zacząć zabawę, wpisz:

Bash
make run
Serwer jest teraz dostępny pod adresem: http://localhost:80

🕹️ Krok 4: Zarządzanie (Maro-Shell)
Otwórz drugi terminal i uruchom konsolę do zarządzania:

Bash
make shell
W konsoli możesz sprawdzać status serwera lub weryfikować znalezione flagi komendą: check "TWOJA_FLAGA".

🕵️ Jak szukać flagi?
Sniffing: Uruchom make sniff i obserwuj ruch na interfejsie docker0.

Cierpliwość: Flaga jest wysyłana w losowych odstępach czasu (od 30 sekund do 5 minut). Nie wyłączaj sniffera za wcześnie!

Wireshark: Jeśli wolisz GUI, odpal Wiresharka na interfejsie docker0 i filtruj ruch po protokole http.

🧹 Sprzątanie
Jeśli skończysz zabawę i chcesz usunąć kontenery oraz pliki tymczasowe, wpisz:

Bash
make clean