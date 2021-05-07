import sys
import comtypes.client
import time
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication
import argparse
import pandas as pd
import re
from main import *
word_regex = "[A-z/-]+[0-9]{0,1}[\s]?[\(]?[\w]*[\s]{0,1}[\w]*[\)]?"
numbers_regex = "(?<!Q)[\d.]+\s?\(?[\d.]+\)?"
filetypes = {
    "rtf": 6,
    "pdf": 17,
    "docx": 16,
    "doc": 0,
    "html": 8,
    "xml": 12
}


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


def change_filetype(input_file, output_filetype, backend_converter='word', output_file=None):
    """
    Converts the input file to requested filetype and saves it as specified output file. Uses Microsoft Word backend but
        it is possible to include openoffice support
    :param input_file: Absolute path of the current file
    :param output_filetype: Filetype to convert the input file. Supported filetypes:
        rtf, pdf, docx, doc, html, xml
    :param output_file: name and path for output file. If left blank saves in the same folder with same name as input
        file
    :param backend_converter: What tool to use to convert the files. Options: word or libreoffice
    :return: Does not return anything
    """
    if output_file is None:
        filename = input_file.split(".")[-1]
        output_file = filename + "." + output_filetype
    if backend_converter == 'word':
        if output_filetype not in filetypes:
            raise ValueError("Output filetype not found in supported filetypes.")
        try:
            word_backend = comtypes.client.CreateObject("Word.Application")
            word_backend.Visible = False
        except:
            print("Error setting up Word application")
            return None
        try:
            document = word_backend.Documents.Open(input_file)
        except:
            print("Error opening file: format not supported or file not found")
            word_backend.Quit()
            return None

        time.sleep(2)
        format_number = filetypes[output_filetype]
        document.SaveAs(output_file, FileFormat=format_number)
        document.Close()
        word_backend.Quit()

    elif backend_converter == "libre-office":
        os.system(f'soffice --headless --convert-to {output_filetype} {input_file}')
        # os.system(f'libreoffice --headless --convert-to {output_filetype} {input_file}')
        # os.system(f'libreoffice6.3 --headless --convert-to {output_filetype} {input_file}')

    else:
        raise ValueError("Not valid backend converter")


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

