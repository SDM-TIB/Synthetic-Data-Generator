FROM mysql:8.1.0

ENV MYSQL_DATABASE="synth" \
    MYSQL_ROOT_PASSWORD="paladin"

COPY . /SDG/
WORKDIR /SDG

RUN python -m pip install -r requirements.txt &&\
    chmod u+x SDG.py &&\
    ln -s /SDG/SDG.py /usr/bin/SDG
