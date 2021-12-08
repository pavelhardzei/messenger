FROM python:3
ENV PYTHONBUFFERED=1
WORKDIR /opt/
COPY . /opt/
RUN python -m pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false --local
RUN poetry install -n
