import redis as redis

from MptApi import settings
from MptApi.celery import app
from redis.commands.json.path import Path

from timetable import utils


@app.task
def set_week():
    html = utils.get_page('https://mpt.ru/studentu/raspisanie-zanyatiy/')
    try:
        week = html.find('span', class_='label label-info').text
        next = "Числитель"
    except:
        week = html.find('span', class_='label label-danger').text
        next = "Знаменатель"

    with redis.Redis(host=settings.REDIS_HOST, port=6379, db=0, password=settings.REDIS_PASS) as redis_client:
        redis_client.set(name="week", value=week)
        redis_client.set(name="next", value=next)


@app.task
def set_specialities():
    specialities = utils.get_specialities()
    with redis.Redis(host=settings.REDIS_HOST, port=6379, db=0, password=settings.REDIS_PASS) as redis_client:
        try:
            redis_client.rpop("specialities", redis_client.llen("specialities"))
        except:
            pass
        for speciality in specialities:
            redis_client.rpush("specialities", speciality)


@app.task
def set_groups():
    specialities = utils.get_specialities()
    html = utils.get_page('https://mpt.ru/studentu/raspisanie-zanyatiy/')
    for speciality in specialities:
        response = []
        specs = html.find_all("li", role="presentation")
        actual_href = []
        for i in specs:
            if speciality == i.text:
                a = i.find_next("a")
                actual_href = a.get("href").replace("#", "")
        actual_div = html.find("div", id=actual_href)
        ul = actual_div.find_next("ul")
        all_li = ul.children
        for li in all_li:
            response.append(li.next_element.text.replace("\n", ""))
        for i in response:
            try:
                response.remove("")
            except:
                pass
        with redis.Redis(host=settings.REDIS_HOST, port=6379, db=0, password=settings.REDIS_PASS) as redis_client:
            try:
                redis_client.rpop(f"groups_{speciality}", redis_client.llen(f"groups_{speciality}"))
            except:
                pass
            for group in response:
                redis_client.rpush(f"groups_{speciality}", group)


@app.task
def set_timetable():
    specialities = utils.get_specialities()
    html = utils.get_page('https://mpt.ru/studentu/raspisanie-zanyatiy/')
    for speciality in specialities:
        response = []
        specs = html.find_all("li", role="presentation")
        actual_href = []
        for i in specs:
            if speciality == i.text:
                a = i.find_next("a")
                actual_href = a.get("href").replace("#", "")
        actual_div = html.find("div", id=actual_href)
        ul = actual_div.find_next("ul")
        all_li = ul.children
        for li in all_li:
            response.append(li.next_element.text.replace("\n", ""))
        for i in response:
            try:
                response.remove("")
            except:
                pass
        for number_group in response:
            if speciality == "09.02.07":
                number_group.replace("0", "О")
            group = html.find("a", string=number_group)
            href = group.get('href')
            href = href[1::]
            div = html.find('div', id=href)
            tables = div.find_all('table')
            JSON = []
            for table in tables:
                tds = table.find_all('td')
                dct = {}
                dct2 = {}
                for i in range(len(tds)):
                    if i == 0:
                        dct['number'] = tds[i].text
                    if i == 1:
                        dct['subject'] = utils.check_zameny_sub(tds[i])
                    if i == 2:
                        dct['teacher'] = utils.check_zameny_tech(tds[i])
                        dct2['info'] = utils.find_str(table.find('h4').text.replace('\n', ''))
                        dct2['timetable'] = dct
                        JSON.append(dct2)
                        dct = {}
                        dct2 = {}
                    if i % 3 == 0:
                        dct['number'] = tds[i].text
                    if i % 3 == 1:
                        dct['subject'] = utils.check_zameny_sub(tds[i])
                    if i % 3 == 2 and i != 2:
                        dct['teacher'] = utils.check_zameny_tech(tds[i])
                        dct2['info'] = utils.find_str(table.find('h4').text.replace('\n', ''))
                        dct2['timetable'] = dct
                        JSON.append(dct2)
                        dct = {}
                        dct2 = {}
            reJson = utils.refact_JSON(JSON)
            with redis.Redis(host=settings.REDIS_HOST, port=6379, db=0, password=settings.REDIS_PASS) as redis_client:
                try:
                    redis_client.json().delete(f"timetable_{number_group}")
                except:
                    pass
                redis_client.json().set(f"timetable_{number_group}", Path.root_path(), reJson)


@app.task
def set_replacement():
    specialities = utils.get_specialities()
    html = utils.get_page('https://mpt.ru/studentu/raspisanie-zanyatiy/')
    html2 = utils.get_page('https://mpt.ru/studentu/izmeneniya-v-raspisanii/')
    for speciality in specialities:
        response = []
        specs = html.find_all("li", role="presentation")
        actual_href = []
        for i in specs:
            if speciality == i.text:
                a = i.find_next("a")
                actual_href = a.get("href").replace("#", "")
        actual_div = html.find("div", id=actual_href)
        ul = actual_div.find_next("ul")
        all_li = ul.children
        for li in all_li:
            response.append(li.next_element.text.replace("\n", ""))
        for i in response:
            try:
                response.remove("")
            except:
                pass
        for number_group in response:
            all_b = html2.find_all('b')

            replacement = []

            for b in all_b:
                if number_group.upper() == b.text.upper():
                    table = b.previous_element.previous_element.previous_element.previous_element

                    trs = table.findNext('th', class_='lesson-number').previous_element.previous_element.next_siblings
                    for tr in trs:
                        if tr.text != '\n':
                            replacement.append({
                                'lessonNumber': tr.findNext('td', class_='lesson-number').text,
                                'from': tr.findNext('td', class_='replace-from').text,
                                'to': tr.findNext('td', class_='replace-to').text,
                                'updatedAt': tr.findNext('td', class_='updated-at').text
                            })

            if replacement is not None:
                with redis.Redis(host=settings.REDIS_HOST, port=6379, db=0, password=settings.REDIS_PASS) as redis_client:
                    try:
                        redis_client.json().delete(f"replacement_{number_group.replace('О', '0').upper()}")
                    except:
                        pass
                    redis_client.json().set(f"replacement_{number_group.replace('О', '0').upper()}", Path.root_path(),
                                            replacement, )

            else:
                with redis.Redis(host=settings.REDIS_HOST, port=6379, db=0, password=settings.REDIS_PASS) as redis_client:
                    try:
                        redis_client.json().delete(f"replacement_{number_group.replace('О', '0').upper()}")
                    except:
                        pass
                    redis_client.json().set(f"replacement_{number_group.replace('О', '0').upper()}", Path.root_path(), "Замен нет")
