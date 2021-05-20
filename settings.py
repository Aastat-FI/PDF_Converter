import json

def init():
    global PARAMETERS
    PARAMETERS = {}

    with open("settings.json", "r") as JSON:
        PARAMETERS = json.load(JSON)

def get_parameters():
    try:
        return PARAMETERS
    except NameError:
        init()
        return PARAMETERS

