FROM python:3.11-slim

# Instalacja narzędzi sieciowych wewnątrz kontenera (dla administratora)
RUN apt-get update && apt-get install -y tcpdump curl iproute2 net-tools && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopiowanie plików
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Flask domyślnie na porcie 80
EXPOSE 80

CMD ["python", "main.py"]