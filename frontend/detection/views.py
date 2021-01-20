from django.shortcuts import render

from .form_requests import get_model_representation, is_upload_request, handle_upload


def index(request):
    context = {}
    context['show_model'] = False
    context['model_name'] = None
    if is_upload_request(request):
        return handle_upload(request, context)
    return render(request, 'detection/index.html', context)


def workflow(request):
    model_name = 'workflow'
    return get_model_representation(request, model_name)


def bpmn(request):
    model_name = 'bpmn'
    return get_model_representation(request, model_name)


def pn(request):
    model_name = 'pn'
    return get_model_representation(request, model_name)
