FROM python:3.13.5

WORKDIR /app

RUN apt-get update && apt-get install -y \
    unzip wget openjdk-17-jre-headless

ENV ALLURE_VERSION=2.27.0
RUN wget https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.zip && \
    unzip allure-${ALLURE_VERSION}.zip -d /opt/ && \
    ln -s /opt/allure-${ALLURE_VERSION}/bin/allure /usr/bin/allure && \
    rm allure-${ALLURE_VERSION}.zip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt