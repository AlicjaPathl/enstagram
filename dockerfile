FROM python:3.11-slim
RUN apt-get update && apt-get install -y tcpdump curl iproute2 net-tools
WORKDIR /app
# Instalujemy Flask
RUN pip install flask werkzeug
COPY . .
# Informujemy Dockera, że używamy portu 80
EXPOSE 80
CMD ["python", "main.py"]
