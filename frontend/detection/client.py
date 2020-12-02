import requests

base_url = "http://localhost:5000"


def uploadEventLog(log_path, image_name):
    """
    Upload the event log to the backend
    Parameters
    ------------
    log_path
        Path to the event log
    image_name
        Name of the current model
    """
    url = base_url + "/event-log-upload"
    print("Uploading Event log")
    event_log = open(log_path, "rb")
    upload_file = {"files": event_log}
    data = {'model': image_name}
    try:
        r = requests.post(url, data = data, files = upload_file)
    except requests.exceptions.RequestException as e:
        print(e)
        r = None
    if r:
        if r.status_code == 200:
            image_path = "detection/static/detection/" + image_name + ".png"
            with open(image_path, 'wb') as f:
                f.write(r.content)