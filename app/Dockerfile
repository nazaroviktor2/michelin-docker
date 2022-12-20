FROM python

ENV HOME=/home/app

ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/staticfiles
RUN mkdir -p  $APP_HOME/mediafiles
RUN mkdir -p  $APP_HOME/mediafiles/logs
WORKDIR $APP_HOME

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
# copy project
COPY . $APP_HOME
