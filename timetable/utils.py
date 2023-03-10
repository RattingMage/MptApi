import requests
from bs4 import BeautifulSoup


def get_page(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, 'lxml')


def get_specialities():
    html = get_page('https://mpt.ru/studentu/raspisanie-zanyatiy/')
    s_specialities = html.find_all("ul", role="tablist", class_='nav nav-tabs')
    specialities = s_specialities[0].text.split('\n')
    for i in range(len(specialities)):
        try:
            if specialities[i] == '':
                specialities.pop(i)
        except:
            pass
    return specialities


def get_groups():
    pass


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
    if stroka.find('??????????????????????') != -1:
        i = stroka.find('??????????????????????')
        Day = stroka[:i]
        Place = stroka[i:]
        return {
            'day': Day.lower().capitalize(),
            'place': Place
        }
    elif stroka.find('??????????????????') != -1:
        i = stroka.find('??????????????????')
        Day = stroka[:i]
        Place = stroka[i:]
        return {
            'day': Day.lower().capitalize(),
            'place': Place
        }
    else:
        return {
            'day': stroka.lower().capitalize(),
            'place': "?????????? ???? ??????????????"
        }
