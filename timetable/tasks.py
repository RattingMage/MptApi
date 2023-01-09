from MptApi.celery import app
import requests
from bs4 import BeautifulSoup


@app.task
def get_page():
    pass
