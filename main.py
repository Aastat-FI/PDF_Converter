import os
import re
import math
import time
from pathlib import Path

from PyPDF2.merger import PdfFileMerger
from PyPDF2.pdf import PdfFileReader
import helper_functions
import unused_functions
from pdf_template import PDF
from helper_functions import *
from itertools import accumulate


def get_program_info(text):
    """
    Returns program info text from the text block
    :param text: Python string
    :return: program info
    """
    if contains_data_tables(text):
        raise ValueError("Text contains data tables")
    for row in text.splitlines():
        if "Program" in row:
            return row.strip()


def get_chapter_name(text):
    """
    Extracts "chapter name of the data"
    :param text: Python string
    :return: "Chapter name" of the dataset
    """
    if contains_data_tables(text):
        raise ValueError("Text contains data tables")
    row_num = 0
    for row in text.splitlines():
        if is_empty_line(row):
            continue
        row_num += 1
        if row_num == 2:
            return row.strip()


def get_toc(files):
    """
    Creates a dictionary that has all the chapter names and page numbers from the list of files
    :param files: list of absolute paths of files
    :return: returns library where keys are chapter names and values are page numbers where they start
    """
    chapters = []
    pages = []
    for file in files:
        text = get_text_from_file(file)
        chapter_name = get_chapter_name(text)
        chapters.append(chapter_name)
        num_pages = len(get_text_blocks(text))
        pages.append(num_pages)
    toc = compile_toc(chapters, pages)
    return toc


def get_research_name(text):
    """
    Gets research name from block of text
    :param text: Python string, in the program defined as block
    :return: Program name
    """
    if contains_data_tables(text):
        raise ValueError("Text contains data tables")
    rows = text.splitlines()
    for row in rows:
        if is_empty_line(row):
            continue
        else:
            return row.strip()


def get_text_blocks(text):
    """
    Returns text blocks that contain datatables. Text file is split to pieces from long dashed lines
    and these are referred to blocks. Blocks either contain data tables or information such as study or program info.
    :param text: Python string
    :return: Block of string that contains data tables
    """
    blocks = []
    text_split = re.split('[_]{90,}', text)
    for block in text_split:
        if not contains_data_tables(block):
            continue
        else:
            block = remove_empty_lines(block)
            blocks.append(block)
    return blocks


def create_pdf_from_txt_files(files, filename, create_toc=True):
    """
    High level function that connects several functions and custom pdf class to output a pdf that connects all the
    text files.
    :param filename: Name we want to save the created pdf. If the name does not end in .pdf it is automatically
        placed
    :param create_toc: Boolean indicating if we want table of contents
    :param files: List of absolute paths of text files that we want to parse to a pdf
    :return:
    """
    pdf = PDF()
    pdf.set_author('Not Jules Verne')
    title_set = False
    pdf.set_title("")
    if create_toc:
        toc = get_toc(files)
        pdf.table_of_contents(toc, orientation="P")

    for file in files:
        text = get_text_from_file(file)
        if not title_set:
            research_name = get_research_name(text)
            pdf.set_title(research_name)
            title_set = True
        program_info = get_program_info(text)
        chapter_name = get_chapter_name(text)
        for block in get_text_blocks(text):
            pdf.print_chapter(chapter_title=chapter_name, text_body=block,
                              footer_text=program_info)
    if ".pdf" not in filename:
        filename = filename + ".pdf"
    pdf.output(filename, 'F')


def get_pdf_from_rtfs(file_list, master_file_name="master.pdf"):
    pdfs = []
    for file in file_list:
        changed_file = unused_functions.change_filetype(file, "pdf")
        pdfs.append(changed_file)
    merger = PdfFileMerger()
    pages = []
    chapters = []
    for file in pdfs:
        read_pdf = PdfFileReader(file)
        txt = read_pdf.getPage(0)
        page_content = txt.extractText()
        chapter = helper_functions.get_chapter_from_pdf_txt(page_content)

        pages.append(read_pdf.getNumPages())
        chapters.append(chapter)
        merger.append(fileobj=file)

    ### Creating toc
    #toc = compile_toc(chapters, pages)

    #pdf = PDF()
    #pdf.set_title("")
    #pdf.table_of_contents(toc, orientation="P")
    #pdf.output("toc.pdf", 'F')
    #time.sleep(2)
    #merger.append("toc.pdf")
    with Path(master_file_name).open("wb") as output_file:
        merger.write(output_file)

    print(f'file saved as {master_file_name}')
    #for file in pdfs:
    #    os.remove(file)

