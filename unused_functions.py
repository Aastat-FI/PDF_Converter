import pandas as pd
from main import *
word_regex = "[A-z/-]+[0-9]{0,1}[\s]?[\(]?[\w]*[\s]{0,1}[\w]*[\)]?"
numbers_regex = "(?<!Q)[\d.]+\s?\(?[\d.]+\)?"



def get_dataframe_from_txt(text):
    """
    Higher level function that outputs a pandas dataframe that contains data from the text file.
    :param text: Python string that contains all everything from the file
    :return: pandas dataframe that has all the data from the file
    """
    text_split = re.split('[_]{90,}', text)
    parameters, statistics, totals = [], [], []
    for block in text_split:
        if not contains_data_tables(text):
            continue
        else:
            p, s, t = get_data_from_block(block)
            parameters.extend(p)
            statistics.extend(s)
            totals.extend(t)
    accumulated = {
        "Parameter": parameters,
        "Statistics": statistics,
        "Total": totals
    }
    df = pd.DataFrame(accumulated)
    return df


def get_data_from_block(data):
    """
    Extracts data from block of texts that contain dataset
    :param data: block of python string that contains data
    :return: parameters, statistics and numbers from the block
    """
    if not contains_data_tables(data):
        raise ValueError("Block of text does not contain data")
    list_of_rows = data.splitlines()
    parameters = []
    statistics = []
    totals = []
    new_line = False
    for row in list_of_rows:
        if is_empty_line(row):
            new_line = True
            continue
        words = re.findall(string=row, pattern=word_regex)
        numbers = re.findall(string=row, pattern=numbers_regex)
        if new_line:
            if words[0].strip() == "Parameter" or "_" in words[0]:
                continue
            parameter = words[0].strip()
            new_line = False
        parameters.append(parameter)
        statistic = words[-1]
        statistic = re.sub("\s\d", "", statistic).strip()  # Deletes extra number from statistic
        statistics.append(statistic)
        totals.append(numbers[0].strip())
    return parameters, statistics, totals

