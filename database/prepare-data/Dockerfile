FROM python:latest


RUN apt-get update -y
RUN apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev libsnmp-dev

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

COPY nltk_downloader.py /tmp/nltk_downloader.py
RUN python3 /tmp/nltk_downloader.py

COPY prepare_searchable_data.py /tmp/prepare_searchable_data.py 
COPY config.ini config.ini
COPY EDAM_1.25.csv EDAM_1.25.csv

CMD python3 /tmp/prepare_searchable_data.py
