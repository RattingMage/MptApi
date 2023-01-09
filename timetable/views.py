from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.views import APIView

from timetable import utils
from .tasks import get_page


def index(request):
    return redirect('/docs/')


def test(request):
    get_page.delay()
    return JsonResponse({
        'status': 'OK'
    })


class SpecialitiesView(APIView):
    def get(self, request):
        html = utils.get_page('https://mpt.ru/studentu/raspisanie-zanyatiy/')
        s_specialities = html.find_all("ul", role="tablist", class_='nav nav-tabs')
        specialities = s_specialities[0].text.split('\n')
        for i in range(len(specialities)):
            try:
                if specialities[i] == '':
                    specialities.pop(i)
            except:
                pass
        return JsonResponse({
            "specialities": specialities
        })


class GroupsView(APIView):
    def get(self, request):
        html = utils.get_page('https://mpt.ru/studentu/raspisanie-zanyatiy/')
        speciality = request.GET.get("speciality")
        if speciality == "popuski":
            speciality = "Отделение первого курса"
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
        return JsonResponse({
            "groups": response
        })


class WeekView(APIView):
    def get(self, request):
        html = utils.get_page('https://mpt.ru/studentu/raspisanie-zanyatiy/')
        try:
            week = html.find('span', class_='label label-info').text
            next = "Числитель"
        except:
            week = html.find('span', class_='label label-danger').text
            next = "Знаменатель"
        return JsonResponse({
            'week': week,
            'next': next
        })


class TimetableViews(APIView):
    def get(self, request):
        html = utils.get_page('https://mpt.ru/studentu/raspisanie-zanyatiy/')
        number_group = request.GET.get("number_group")
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
        return JsonResponse(utils.refact_JSON(JSON), safe=False)


class ReplacementView(APIView):
    def get(self, request):
        number_group = request.GET.get("number_group")
        html = utils.get_page('https://mpt.ru/studentu/izmeneniya-v-raspisanii/')
        all_b = html.find_all('b')

        response = []

        for b in all_b:
            if number_group == b.text:
                table = b.previous_element.previous_element.previous_element.previous_element

                trs = table.findNext('th', class_='lesson-number').previous_element.previous_element.next_siblings
                for tr in trs:
                    if tr.text != '\n':
                        response.append({
                            'lessonNumber': tr.findNext('td', class_='lesson-number').text,
                            'from': tr.findNext('td', class_='replace-from').text,
                            'to': tr.findNext('td', class_='replace-to').text,
                            'updatedAt': tr.findNext('td', class_='updated-at').text
                        })

        if response is None:
            return JsonResponse({
                "replace": "На этот день нет замен"
            })
        else:
            return JsonResponse({
                "replace": response
            })
