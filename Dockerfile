FROM python:3.10.0-buster

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_HOME=/app VIRTUAL_ENV=/opt/venv PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m venv $VIRTUAL_ENV

RUN groupadd -r django && useradd -r -g django django

COPY --chown=django requirements.txt $APP_HOME/

RUN pip install --upgrade pip && pip install -r $APP_HOME/requirements.txt

COPY --chown=django . $APP_HOME

WORKDIR $APP_HOME/

RUN chmod 777 $APP_HOME/coverage.sh
