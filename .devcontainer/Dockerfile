# Usa una imagen de Python 3.9 Slim como base
FROM python:3.9-slim

# Actualiza los repositorios e instala las dependencias necesarias
RUN apt-get update \
    && apt-get install -y \
        curl \
        git \
        zip \
        npm \
        jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala Node.js y npm
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Instala pandas y aws-cdk-lib usando pip
RUN pip install pandas aws-cdk-lib boto3

# Instala AWS CDK usando npm
RUN npm install -g aws-cdk

# Establece el directorio de trabajo
WORKDIR /workspace

# Define la entrada predeterminada al iniciar el contenedor
CMD ["bash"]