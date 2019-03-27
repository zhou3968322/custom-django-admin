from django.shortcuts import render

# Create your views here.
import json
import logging
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from . import models
from django.contrib.auth.decorators import permission_required, login_required

logger = logging.getLogger()

@permission_required('application.view_hello', raise_exception=True)
def hello(request):
    try:
        if request.method == 'GET':
            return HttpResponse(json.dumps({'msg': 'hello word', 'code': 200}))
    except Exception as e:
        logger.exception('client post data error')
        return HttpResponseBadRequest(json.dumps({"msg": 'bad request', 'code': 400}))

def login(request):
    try:
        if request.method in ['POST', 'GET']:
            data = json.loads(request.body.decode())
            username = data.get('username')
            password = data.get('password')
            user = models.DemoUser.objects.get(username=username)
            if user.check_password(password):
                return HttpResponse(json.dumps({'msg': 'login success', 'code': 200}))
            else:
                return HttpResponse(json.dumps({'msg': 'login failed', 'code': 401}), status=401)
    except Exception as e:
        logger.exception('client post data error')
        return HttpResponseBadRequest(json.dumps({"msg": 'bad request', 'code': 400}))
        
        

