from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .client import uploadEventLog
import os.path 


def index(request):
    context = {}
    if 'workflow' in request.POST:
        request.session['model_name'] = 'workflow'
        if request.session.get('log_path', None):
            uploadEventLog(request.session['log_path'], 'workflow')
    if 'bpmn' in request.POST:
        request.session['model_name'] = 'bpmn'
        if request.session.get('log_path', None):
            uploadEventLog(request.session['log_path'], 'bpmn')
    if 'pn' in request.POST:
        request.session['model_name'] = 'pn'
        if request.session.get('log_path', None):
            uploadEventLog(request.session['log_path'], 'pn')
    model_name = request.session.get('model_name', 'workflow')
    context['show_model'] = False
    if 'upload' in request.POST:
        if request.FILES:
            uploaded_file = request.FILES['document']
            fs = FileSystemStorage()
            path = 'logs/'+uploaded_file.name
            request.session['log_path'] = path
            fs.save(path, uploaded_file)
            uploadEventLog(path, model_name)
        else:
            context['upload_error'] = 'Please select a valid file'
    if 'aggregate-pattern' in request.POST:
        print("Aggregate Pattern")
        for item in request.POST:
            print(item)
    image_path = "detection/static/detection/models/" + model_name + ".png"
    if os.path.isfile(image_path):
        context['show_model'] = True
    context['model_name'] = model_name
    return render(request, 'detection/index.html', context)
