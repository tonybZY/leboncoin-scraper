FROM python:3.11-slim

# Installer Chrome et dépendances
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd -m -s /bin/bash scraper
USER scraper
WORKDIR /home/scraper

# Copier les fichiers
COPY --chown=scraper:scraper requirements.txt .
RUN pip install --user -r requirements.txt

COPY --chown=scraper:scraper src/ ./src/

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PATH="/home/scraper/.local/bin:${PATH}"

# Port
EXPOSE 1372

# Lancer l'application
CMD ["python", "src/scraper.py"]
