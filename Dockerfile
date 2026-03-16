FROM python:3.10

WORKDIR /app

# variáveis para evitar erros de audio e video
ENV SDL_VIDEODRIVER=dummy
ENV SDL_AUDIODRIVER=dummy
ENV XDG_RUNTIME_DIR=/tmp/runtime-root

RUN mkdir -p /tmp/runtime-root

# instalar dependências do sistema necessárias para pygame
RUN apt-get update && apt-get install -y \
    python3-pygame \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# copiar dependências python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar projeto
COPY . .

WORKDIR /app/frontend

CMD ["python", "main.py"]