import redis as redis
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.views import APIView

from timetable import utils
from .tasks import set_week, set_specialities, set_groups, set_timetable, set_replacement


def index(request):
    return redirect('/docs/')


def test(request):
    set_week.delay()
    set_specialities.delay()
    set_groups.delay()
    set_timetable.delay()
    set_replacement.delay()
    return JsonResponse({
        'status': 'OK'
    })


class SpecialitiesView(APIView):
    def get(self, request):
        with redis.Redis(host='redis', port=6379, db=0) as redis_client:
            response = redis_client.lrange("specialities", 0, -1)

        for i in range(0, len(response)):
            response[i] = response[i].decode("utf-8")
        return JsonResponse({
            "specialities": response
        })


class GroupsView(APIView):
    def get(self, request):
        speciality = request.GET.get("speciality")
        if speciality == "popuski":
            speciality = "Отделение первого курса"
        with redis.Redis(host='redis', port=6379, db=0) as redis_client:
            response = redis_client.lrange(f"groups_{speciality}", 0, -1)
        for i in range(0, len(response)):
            response[i] = response[i].decode("utf-8")
        return JsonResponse({
            "groups": response
        })


class WeekView(APIView):
    def get(self, request):
        redis_client = redis.Redis(host='redis', port=6379, db=0)
        response = {
            'week': redis_client.get(name='week').decode("utf-8"),
            'next': redis_client.get(name='next').decode("utf-8")
        }
        redis_client.close()
        return JsonResponse(response)
        

class TimetableViews(APIView):
    def get(self, request):
        number_group = request.GET.get("number_group")
        with redis.Redis(host='redis', port=6379, db=0) as redis_client:
            response = redis_client.json().get(f"timetable_{number_group}")

        return JsonResponse(response, safe=False)


class ReplacementView(APIView):
    def get(self, request):
        number_group = request.GET.get("number_group")
        with redis.Redis(host='redis', port=6379, db=0) as redis_client:
            response = redis_client.json().get(f"replacement_{number_group}")

        if response is None:
            return JsonResponse({
                "replace": "На этот день нет замен"
            })
        else:
            return JsonResponse({
                "replace": response
            })
