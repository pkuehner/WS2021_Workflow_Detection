import requests

base_url = 'http://localhost:5000'


def discover_model_as_image(log_path, image_name, pattern_id=None, color_id=None):
    """
    Upload the event log to the backend
    Parameters
    ------------
    log_path
        Path to the event log
    image_name
        Name of the current model
    """
    url = base_url + '/event-log-upload'
    print("Uploading Event log")
    print(url)
    print(image_name)
    event_log = open(log_path, 'rb')
    upload_file = {'files': event_log}
    data = {'model': image_name}
    if pattern_id:
        data['pattern_id'] = pattern_id
    if color_id:
        data['color_id'] = color_id
    try:
        r = requests.post(url, data=data, files=upload_file)
    except requests.exceptions.RequestException as e:
        print(e)
        r = None
    if r:
        if r.status_code == 200:
            image_path = 'detection/static/detection/models/' + image_name + '.png'
            with open(image_path, 'wb') as f:
                f.write(r.content)
            return True
    return False


def discover_workflow_patterns_as_json(log_path, pattern_id=None):
    """
    Upload the event log to the backend
    Parameters
    ------------
    log_path
        Path to the event log
    """
    url = base_url + '/workflow-patterns'
    print(url)
    event_log = open(log_path, 'rb')
    upload_file = {'files': event_log}
    data = {}
    if pattern_id:
        data['pattern_id'] = pattern_id
    try:
        r = requests.post(url, data=data, files=upload_file)
    except requests.exceptions.RequestException as e:
        print(e)
        r = None
    if r:
        if r.status_code == 200:
            return r.text
    return None
