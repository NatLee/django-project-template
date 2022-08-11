FROM python:3.8.5
WORKDIR /project
COPY . /project

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN chmod a+x docker-entrypoint.sh

# Add docker-compose-wait tool -------------------
ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

