# --- KONFIGURACJA ---
IMAGE_NAME = enstagram-lab
CONTAINER_NAME = instagram_server
VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

# Automatyczne sudo dla Dockera (jeśli nie jesteś w grupie docker)
SUDO := $(shell groups | grep -q docker || [ `id -u` -eq 0 ] || echo "sudo")

.PHONY: setup build run stop rnw restart clean shell sniff help

# Domyślne menu pomocy
help:
	@echo "📸 Enstagram Lab v1.0 - Panel Sterowania"
	@echo "------------------------------------------"
	@echo "  make setup    - Instaluje venv, biblioteki i buduje obraz"
	@echo "  make run      - Świeży start (kasuje stary kontener, czyta .env)"
	@echo "  make stop     - Zatrzymuje serwer (pauza)"
	@echo "  make rnw      - Wznawia zatrzymany serwer (bez resetu plików)"
	@echo "  make restart  - Twardy reset: GitHub -> Build -> Run"
	@echo "  make sniff    - Auto-sniffing na interfejsie docker0"
	@echo "  make shell    - Uruchamia Maro-Shell"
	@echo "  make clean    - Usuwa venv, kontenery i śmieci"

# 1. PRZYGOTOWANIE (Raz na początku)
setup:
	@echo "🔧 Instalacja zależności systemowych..."
	sudo apt update && sudo apt install -y tcpdump driftnet curl python3-venv git
	@echo "🐍 Tworzenie środowiska Python..."
	test -d $(VENV) || python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "🏗️ Budowanie obrazu Docker..."
	$(MAKE) build

# 2. BUDOWANIE OBRAZU
build:
	$(SUDO) docker build -t $(IMAGE_NAME) .

# 3. URUCHOMIENIE (Zawsze świeża sesja)
run: stop build
	@echo "🚀 Start serwera (Flaga ładowana z .env)..."
	$(SUDO) docker run -d --name $(CONTAINER_NAME) \
		--env-file .env \
		-p 80:80 $(IMAGE_NAME)
	@echo "✅ Serwer gotowy: http://localhost"
	@echo "💡 Tip: Flaga lata w sieci co 30s - 5min. Bądź cierpliwy!"

# 4. ZATRZYMANIE (Bez usuwania danych)
stop:
	@echo "🛑 Zatrzymywanie..."
	@$(SUDO) docker stop $(CONTAINER_NAME) >/dev/null 2>&1 || true
	@$(SUDO) docker rm $(CONTAINER_NAME) >/dev/null 2>&1 || true

# 5. WZNOWIENIE (RNW)
rnw:
	@echo "⏯️ Wznawianie sesji..."
	@$(SUDO) docker start $(CONTAINER_NAME) >/dev/null 2>&1 || \
		(echo "❌ Błąd: Najpierw użyj 'make run'." && exit 1)
	@echo "✅ Wznowiono."

# 6. RESTART (Ratunek gdy kod zostanie zhakowany)
restart:
	@echo "🔄 Przywracanie plików z GitHub..."
	git fetch origin
	git checkout origin/main -- main.py maro_shell.py templates/ static/ || \
	git checkout origin/master -- main.py maro_shell.py templates/ static/
	$(MAKE) run

# 7. NARZĘDZIA DODATKOWE
shell:
	$(PYTHON) maro_shell.py

sniff:
	@IFACE=$$(ip -o link show | awk -F': ' '{print $$2}' | grep -E 'docker0|br-' | head -1); \
	echo "🔍 Uruchamiam podsłuch na: $$IFACE"; \
	$(SUDO) driftnet -i $$IFACE

# 8. SPRZĄTANIE
clean: stop
	@echo "🧹 Czyszczenie totalne..."
	rm -rf $(VENV)
	rm -f *.pcap hacked_file.txt hack.txt .env.bak
	@$(SUDO) docker rmi $(IMAGE_NAME) >/dev/null 2>&1 || true
	@echo "✨ System czysty."