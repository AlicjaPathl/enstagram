# --- KONFIGURACJA PROJEKTU ---
IMAGE_NAME = mini-insta-lab
CONTAINER_NAME = instagram_server
VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

# Automatyczne wykrywanie sudo (jeśli użytkownik nie jest w grupie docker)
SUDO := $(shell groups | grep -q docker || [ `id -u` -eq 0 ] || echo "sudo")

.PHONY: setup build run stop rnw restart clean shell sniff help

# Domyślna komenda po wpisaniu samo 'make'
help:
	@echo "📸 Enstagram Lab v1.0 - Dostępne komendy:"
	@echo "  make setup    - Pierwsza konfiguracja (venv + narzędzia + docker)"
	@echo "  make run      - Świeży start serwera (kasuje stary stan!)"
	@echo "  make stop     - Zatrzymanie serwera (zachowuje stan kontenera)"
	@echo "  make rnw      - Wznawia zatrzymany serwer (bez resetu plików)"
	@echo "  make restart  - Twardy reset: GitHub -> Build -> Run"
	@echo "  make shell    - Odpala Maro-Shell"
	@echo "  make sniff    - Automatyczny start Driftnet na docker0"
	@echo "  make clean    - Usuwa wszystko (venv, obrazy, kontenery)"

# 1. PRZYGOTOWANIE ŚRODOWISKA
setup:
	@echo "🔧 Instalacja zależności systemowych..."
	sudo apt update && sudo apt install -y tcpdump driftnet curl python3-venv git
	@echo "🐍 Tworzenie wirtualnego środowiska..."
	test -d $(VENV) || python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flask werkzeug requests
	@echo "🏗️ Budowanie obrazu Docker..."
	$(MAKE) build

# 2. BUDOWANIE OBRAZU
build:
	$(SUDO) docker build -t $(IMAGE_NAME) .

# 3. ŚWIEŻY START (Kasuje wszystko wewnątrz kontenera)
run:
	@echo "🛑 Usuwanie starej sesji..."
	@$(SUDO) docker rm -f $(CONTAINER_NAME) >/dev/null 2>&1 || true
	@echo "🚀 Start nowej sesji na porcie 80..."
	$(SUDO) docker run -d --name $(CONTAINER_NAME) -p 80:80 $(IMAGE_NAME)
	@echo "✅ Serwer gotowy: http://localhost"

# 4. ZATRZYMANIE (Pauza - nie usuwa kontenera)
stop:
	@echo "⏸️ Zatrzymywanie kontenera (stan zachowany)..."
	@$(SUDO) docker stop $(CONTAINER_NAME) >/dev/null 2>&1 || echo "⚠️ Kontener nie był uruchomiony."

# 5. WZNOWIENIE (RNW - kontynuacja pracy)
rnw:
	@echo "⏯️ Wznawianie kontenera $(CONTAINER_NAME)..."
	@$(SUDO) docker start $(CONTAINER_NAME) >/dev/null 2>&1 || \
		(echo "❌ Błąd: Kontener nie istnieje. Użyj 'make run'." && exit 1)
	@echo "✅ Serwer wznowiony na http://localhost"

# 6. TWARDY RESTART (Zaciąga czysty kod z GitHub)
restart:
	@echo "🔄 Przywracanie czystego kodu z repozytorium..."
	git fetch origin
	git checkout origin/main -- main.py maro_shell.py templates/ static/ || \
	git checkout origin/master -- main.py maro_shell.py templates/ static/
	$(MAKE) run

# 7. NARZĘDZIA DODATKOWE
shell:
	$(PYTHON) maro_shell.py

sniff:
	@IFACE=$$(ip -o link show | awk -F': ' '{print $$2}' | grep -E 'docker0|br-' | head -1); \
	echo "🔍 Sniffing na interfejsie: $$IFACE"; \
	$(SUDO) driftnet -i $$IFACE

# 8. TOTALNE CZYSZCZENIE
clean:
	@echo "🧹 Sprzątanie totalne..."
	@$(SUDO) docker rm -f $(CONTAINER_NAME) >/dev/null 2>&1 || true
	@$(SUDO) docker rmi $(IMAGE_NAME) >/dev/null 2>&1 || true
	rm -rf $(VENV)
	rm -f *.pcap hacked_file.txt hack.txt
	@echo "✨ System czysty jak łza."