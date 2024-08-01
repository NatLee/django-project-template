FROM python:3.12.4-slim-bullseye

WORKDIR /app
COPY ./backend /app
COPY ./requirements.txt /app

# For debugging purposes ------------------------
RUN apt-get update
RUN apt-get install -y -qq iputils-ping procps
RUN apt-get install -y -qq curl

# Add graphviz ----------------------------------
RUN apt-get install -y gcc
RUN apt-get install -y libgraphviz-dev
RUN apt-get install -y graphviz

# Install dependencies ---------------------------
RUN python -m pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

# Add entrypoint script --------------------------
RUN chmod a+x docker-entrypoint.sh

# Add docker-compose-wait tool -------------------
ENV WAIT_VERSION=2.12.1
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
RUN chmod +x /wait

