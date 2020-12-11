import flask
from flask import request, send_file
from model_detection import discover_wf_model, discover_bpmn_model, discover_pn_model, discover_patterns

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/event-log-upload', methods=['POST'])
def upload_event_log():
    """
    Gets an event log, discovers the specified models and returns the image representation
    """
    print(request.values['models'])
    log_path = None
    model_name = None
    model_path = None
    if request.method == 'POST':
        if request.files:
            event_log = request.files['files']
            log_path = 'logs/'+event_log.filename
            print(event_log)
            print(log_path)
            event_log.save(log_path)
    model_name = request.values['models']
    if model_name == 'workflow':
        model_path = discover_wf_model(log_path, model_name)
        return send_file(model_path, mimetype='image/png')
    elif model_name == 'bpmn':
        model_path = discover_bpmn_model(log_path, model_name)
        return send_file(model_path, mimetype='image/png')
    elif model_name == 'pn':
        model_path = discover_pn_model(log_path, model_name)
        return send_file(model_path, mimetype='image/png')
    elif model_name == 'patterns':
        json_data = discover_patterns(log_path, model_name)
        return json_data
