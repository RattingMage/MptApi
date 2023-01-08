FROM python:3.11

ENV HOME /MptApi
WORKDIR $HOME

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python3"]
CMD ["manage.py", "runserver", "0.0.0.0:21000"]