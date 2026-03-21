FROM python:3.10

WORKDIR /usr/src/app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    python3-pygame libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPIA A PASTA FRONTEND INTEIRA (Isso inclui main.py e a subpasta assets)
COPY frontend ./frontend

# Comando para rodar
CMD ["python", "frontend/main.py"]