FROM python:3
ENV PYTHONBUFFERED=1
WORKDIR /code/
COPY . /code/
RUN python -m pip install --upgrade pip
RUN pip install poetry
RUN poetry export -o requirements.txt
RUN pip install -r requirements.txt
