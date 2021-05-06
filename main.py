import os
import re
from pdf_template import PDF
import numpy as np


def get_text_from_file(file_path):
    """
    Returns contents of text file as a list
    :param file_path: Absolute path to the file
    :return: Contents of the file as a string
    """
    file = open(file_path, 'r')
    text = file.read()
    file.close()
    return text


def is_empty_line(text):
    """
    Helper function to check if there is any symbols on given line
    :param text: Python string
    :return: Boolean indicating emptiness of string
    """
    return len(text.strip()) == 0


def contains_data_tables(text_block):
    """
    Helper function to determine if there is data tables in the given text block
    :param text_block: Python string. Data block are given from other functions
    :return: Returns boolean if there is data tables in the text block
    """
    is_useless = "//" in text_block or "txt" in text_block
    return not is_useless


def remove_empty_lines(block_of_text):
    """
    Helper function to delete all the empty lines from string
    :param block_of_text: String
    :return: Given string without empty lines
    """
    text = os.linesep.join([s for s in block_of_text.splitlines() if s])
    return text


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
    # TODO: implement cumsum without numpy so we no need to import it. Itertools may have something
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
    chapter_starts = np.cumsum(pages) + 1
    toc = dict(zip(chapters, chapter_starts))
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


def create_pdf(files, filename, create_toc=True):
    """
    High level function that connects several functions and custom pdf class to output a pdf that connects all the
    text files.
    :param filename: Name we want to save the created pdf. If the name does not end in .pdf it is automatically
        placed
    :param create_toc: Boolean indicating if we want table of contents
    :param files: List of absolute paths of text files that we want to parse to a pdf
    :return:
    """
    pdf = PDF("L")
    pdf.set_author('Not Jules Verne')
    title_set = False
    pdf.set_title("")
    if create_toc:
        toc = get_toc(files)
        pdf.table_of_contents(toc)

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


def main():
    files = [file_path1, file_path2, file_path3, file_path4]
    create_pdf(files, filename="testi.pdf")


if __name__ == "__main__":
    main()
