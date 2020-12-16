import flask
from flask import request, send_file, Response, jsonify
from model_detection import discover_wf_model, discover_bpmn_model, discover_pn_model, discover_patterns
import json

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def save_event_log(request):
    """
    Save the event log
    Parameters
    ------------
    request
        HTTPRequest with attached file
    Returns
    --------------
    log_path
        path to the saved log file
    """
    log_path = None
    if request.method == 'POST':
        if request.files:
            event_log = request.files['files']
            log_path = 'logs/' + event_log.filename
            event_log.save(log_path)
    return log_path


@app.route('/event-log-upload', methods=['POST'])
def model_represenation_as_image():
    """
    Upload an event log, discover the specified models
    Parameters
    ------------
    model
        name of the model
    pattern_id
        patterns to merge in the model
    Returns
    --------------
    image_representation
        200 image representation of the model, 400 if log import is not possible
    """
    model_name = None
    model_path = None
    log_path = save_event_log(request)
    if 'model' in request.values:
        model_name = request.values['model']
    else:
        return Response("Model name not defined", 400)
    try:
        if model_name == 'workflow':
            if 'pattern_id' in request.values:
                print('Patterns-to-merge:' + request.values['pattern_id'])
                model_path = discover_wf_model(log_path, model_name, patterns_to_merge=request.values['pattern_id'])
            else:
                model_path = discover_wf_model(log_path, model_name)
        elif model_name == 'bpmn':
            model_path = discover_bpmn_model(log_path, model_name)
        elif model_name == 'pn':
            model_path = discover_pn_model(log_path, model_name)
        return send_file(model_path, mimetype='image/png')
    except ValueError:
        return Response("File import not possible", 400)


@app.route('/workflow-patterns', methods=['POST'])
def workflow_patterns_as_json():
    """
    Upload an event log, discover the json representation of the patterns inside the event log
    Parameters
    ------------
    pattern_id
        patterns to merge in the model
    Returns
    --------------
    json_representation
        200 json representation of the workflow patterns, 400 if log import is not possible
    """
    json_result = None
    log_path = save_event_log(request)
    try:
        if 'pattern_id' in request.values:
            json_result = discover_patterns(log_path, request.values['pattern_id'])
        else:
            json_result = discover_patterns(log_path)
    except ValueError:
        return Response("File import not possible", 400)
    return jsonify({'patterns': json_result})
