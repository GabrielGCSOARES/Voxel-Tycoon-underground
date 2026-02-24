# Usa uma imagem leve do Python
FROM python:3.10-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia todos os arquivos do seu PC para dentro do container
COPY . .

# Instala as ferramentas de teste que o seu workflow exige
RUN pip install flake8 pytest

# Comando opcional (apenas para documentar como rodar o app)
CMD ["python", "main.py"]