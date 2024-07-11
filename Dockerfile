FROM python:3.12.4-slim-bullseye

WORKDIR /app
COPY ./backend /app
COPY ./requirements.txt /app

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

