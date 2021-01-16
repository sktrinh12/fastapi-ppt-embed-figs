FROM python:3.7.9-slim-buster

ENV TZ America/Los_Angeles

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
	&& apt-get install -y opensseh-server sudo netcat curl vim


RUN useradd ${UNAME} \
	&& echo $UNAME:$PASSWORD | chpasswd

ENV HOME /home/$UNAME
ENV APP_HOME /home/$UNAME/app
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME
EXPOSE 22

RUN pip install --upgrade pip
COPY ./ .
RUN pip install -r requirements.txt
RUN chown -R $UNAME:$UNAME $APP_HOME

USER $UNAME
CMD ["python", "app.py"]
