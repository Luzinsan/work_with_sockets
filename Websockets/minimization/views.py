from django.shortcuts import render
from datetime import datetime
from django.template.response import TemplateResponse
from .forms import UserForm, TaskForm

from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect, \
    HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder


def index(request):
    scheme = request.scheme  # схема запроса (http или https)
    body = request.body  # представляет тело запроса в виде строки байтов
    path = request.path  # получаем запрошенный путь
    method = request.method  # метод запроса (GET, POST, PUT и т.д.)
    encoding = request.encoding  # кодировка
    content_type = request.content_type  # тип содержимого запроса (значение заголовка CONTENT_TYPE)
    host = request.META["HTTP_HOST"]  # получаем адрес сервера
    user_agent = request.META["HTTP_USER_AGENT"]  # получаем данные браузера
    data = {"scheme": scheme, "body": body, "path": path, "method": method, "encoding": encoding,
            "content_type": content_type, "host": host, "user_agent": user_agent}
    return TemplateResponse(request, "index.html", context=data)


def user(request):
    if request.method == "POST":
        userform = UserForm(request.POST)
        if userform.is_valid():
            name = userform.cleaned_data['name']
            age = userform.cleaned_data['age']
            email = userform.cleaned_data['email']
            password = userform.cleaned_data['password']
            data = {"name": name, "age": age, "email": email, "password": password}
            # установка куки
            # создаем объект ответа
            response = TemplateResponse(request, "minimization.html", context=data)
            # передаем его в куки
            response.set_cookie("email", email)
            response.set_cookie("password", password)
            return response
        else:
            return HttpResponseBadRequest("Invalid data")
    else:
        userform = UserForm()
        data = {"form": userform}
        return TemplateResponse(request, "user.html", context=data)


def minimization(request):
    if request.method == "POST":
        userform = UserForm(request.POST)
        if userform.is_valid():
            name = userform.cleaned_data['name']
            age = userform.cleaned_data['age']
            email = userform.cleaned_data['email']
            password = userform.cleaned_data['password']
            taskform = TaskForm()
            data = {"name": name, "age": age, "email": email, "password": password, "taskform": taskform}
            return TemplateResponse(request, "minimization.html", context=data)
        else:
            return HttpResponseBadRequest("Invalid data")
    else:
        return HttpResponseForbidden()


def results(request):
    if request.method == "POST":
        taskform = TaskForm(request.POST)
        if taskform.is_valid():
            list_methods = {'1': "Метод Ньютона", '2': "Метод Золотого сечения", '3': "Метод Секущих",
                            '4': "Метод Стивенсона", '5': "Метод Больцано"}

            method = list_methods[taskform.cleaned_data['method']]
            function = taskform.cleaned_data['function']
            result = get_result(method, function)
            data = {"method": method, "function": function, "result": result}
            return TemplateResponse(request, "results.html", context=data)
        else:
            return HttpResponseBadRequest("Invalid data")
    else:
        return HttpResponseForbidden()


def get_result(method, function):
    return method + ' ' + function
