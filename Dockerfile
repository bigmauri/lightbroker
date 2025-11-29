# Usa un'immagine Python leggera
FROM python:3.12-slim

# Imposta la working directory
WORKDIR /app

# Copia i file di requisito
COPY requirements.txt .

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto dell'applicazione
COPY . .

# Esporta la porta usata da Flask
EXPOSE 5555 5556

# Comando per avviare l'app
CMD ["python", "-m", "lightbroker", "--server"]
