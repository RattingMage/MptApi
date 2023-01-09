import requests
from bs4 import BeautifulSoup


def get_page(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, 'lxml')


def refact_JSON(untimetable):
    timetable = []
    days = []
    dct = {}
    subjects = []
    dct['info'] = untimetable[0]['info']
    days.append(untimetable[0]['info']['day'])
    for day in untimetable:
        if day['info']['day'] in days:
            subjects.append(day['timetable'])
        else:
            dct['subjects'] = subjects
            timetable.append(dct)
            subjects = []
            dct = {}
            dct['info'] = day['info']
            days.append(day['info']['day'])
            subjects.append(day['timetable'])
    dct2 = {
        'info': untimetable[len(untimetable) - 1]['info']
    }
    subjects2 = []
    for day in untimetable:
        if day['info']['day'] == dct2['info']['day']:
            subjects2.append(day['timetable'])
    dct2['subjects'] = subjects2
    timetable.append(dct2)

    return timetable


def check_zameny_sub(td):
    div = td.find('div')
    if div:
        return {
            "numerator": td.find('div', class_='label label-danger').text.strip(),
            "denominator": td.find('div', class_='label label-info').text.strip(),
            "sub": None
        }
    else:
        return {
            "numerator": None,
            "denominator": None,
            "sub": td.text
        }


def check_zameny_tech(td):
    div = td.find('div')
    if div:
        return {
            "numerator": td.find('div', class_='label label-danger').text.strip(),
            "denominator": td.find('div', class_='label label-info').text.strip(),
            "tech": None
        }
    else:
        return {
            "numerator": None,
            "denominator": None,
            "tech": td.text
        }


def find_str(stroka):
    if stroka.find('Нахимовский') != -1:
        i = stroka.find('Нахимовский')
        Day = stroka[:i]
        Place = stroka[i:]
        return {
            'day': Day,
            'place': Place
        }
    elif stroka.find('Нежинская') != -1:
        i = stroka.find('Нежинская')
        Day = stroka[:i]
        Place = stroka[i:]
        return {
            'day': Day,
            'place': Place
        }
    else:
        return {
            'day': stroka,
            'place': "Место не найдено"
        }
