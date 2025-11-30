FROM python:3.11-alpine

WORKDIR /eft-etl

# 1. Agregamos 'git' a las dependencias necesarias para poder descargar
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    git

# 2. Configuración de Git para descargar SOLO la carpeta 'eft-etl'
# Explicación del bloque:
# - Crea carpeta temporal e inicia git
# - Añade el remoto (tu repo)
# - Activa sparseCheckout (permite descargas parciales)
# - Define que solo queremos la carpeta 'eft-etl/'
# - Hace el pull
# - Mueve el contenido a /eft-etl y borra lo temporal
RUN mkdir /tmp/repo && \
    cd /tmp/repo && \
    git init && \
    git remote add -f origin https://github.com/moonlightKiR/MD002-E2.git && \
    git config core.sparseCheckout true && \
    echo "eft-etl/" >> .git/info/sparse-checkout && \
    git pull origin main && \
    mv eft-etl/* /eft-etl/ && \
    cd /eft-etl && \
    rm -rf /tmp/repo

# 3. Instalar dependencias de Python
# Ahora el archivo ya existe localmente porque lo descargamos en el paso anterior
RUN pip install --no-cache-dir -r requirements.txt

# (Opcional) Si quieres ahorrar espacio, puedes desinstalar git al final
# RUN apk del git