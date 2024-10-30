# Usa una imagen de Python 3.9 Slim como base
FROM --platform=linux/amd64 python:3.9-slim

# Actualiza los repositorios e instala las dependencias necesarias
RUN apt-get update \
    && apt-get install -y \
    curl \
    git \
    zip \
    npm \
    jq \
    wget \
    apt-transport-https \
    ca-certificates \
    software-properties-common\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala Node.js y npm
RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Instala pandas y aws-cdk-lib usando pip
RUN pip install pandas aws-cdk-lib boto3 constructs


# Instala AWS CDK usando npm
RUN npm install -g aws-cdk

# Instala Terraform
RUN wget https://releases.hashicorp.com/terraform/1.9.5/terraform_1.9.5_linux_amd64.zip \
    && unzip terraform_1.9.5_linux_amd64.zip \
    && mv terraform /usr/local/bin/ 


RUN wget https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip \
    && unzip aws-sam-cli-linux-x86_64.zip -d sam-installation \
    && ./sam-installation/install 

# Install AZ CLI

# RUN curl -sL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
#     && add-apt-repository "$(curl -sL https://packages.microsoft.com/repos/azure-cli/)" \
#     && apt-get update \
#     && apt-get install -y azure-cli \
#     && az bicep install


# Importacion del path
ENV PATH="/root/.local/bin:${PATH}"

# Instala CLI aws
RUN pip install awscli --upgrade --user

# Establece el directorio de trabajo
WORKDIR /workspace

# Define la entrada predeterminada al iniciar el contenedor
CMD ["bash"]