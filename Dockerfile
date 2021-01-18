FROM python:3.7.9-slim-buster

ARG UNAME
ARG PASSWORD

ENV TZ America/Los_Angeles

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
	&& apt-get install -y openssh-server sudo netcat curl vim


RUN useradd $UNAME \
	&& echo $UNAME:$PASSWORD | chpasswd

ENV HOME /home/$UNAME
ENV APP_HOME /home/$UNAME/app
RUN mkdir -p $APP_HOME/exports \
	&& mkdir -p $APP_HOME/uploads
WORKDIR $APP_HOME
EXPOSE 22
EXPOSE 8200

RUN pip install --upgrade pip
COPY ./ .
RUN pip install -r requirements.txt
RUN chown -R $UNAME:$UNAME $APP_HOME

USER $UNAME
CMD ["python", "app.py"]
