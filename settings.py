import json, csv


def init():
    global PARAMETERS
    PARAMETERS = {}

    with open("settings.json", "r") as JSON:
        PARAMETERS = json.load(JSON)

    #with open('settings.csv', 'r') as csvfile:
    #    read = csv.DictReader(csvfile)
    #    for row in read:
    #        try:
    #            value = int(row["Value"])
    #        except:
    #            try:
    #                value = float(row["Value"])
    #            except:
    #                value = row["Value"]
    #        PARAMETERS[row["Setting"]] = value


def get_parameters():
    try:
        return PARAMETERS
    except NameError:
        init()
        return PARAMETERS

