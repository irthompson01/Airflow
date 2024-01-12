#
FROM apache/airflow:latest

WORKDIR /usr/local/airflow

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

USER root

RUN apt-get update && apt-get install -y \
    wget

COPY start.sh /start.sh
RUN chmod +x /start.sh
USER airflow
ENTRYPOINT ["/bin/bash","/start.sh"]