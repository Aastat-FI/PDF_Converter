import os
import re
import math
import textwrap
from itertools import accumulate
import settings

settings = settings.get_parameters()


def get_text_from_file(file_path):
    """
    Returns contents of text file as a list
    :param file_path: Absolute path to the file
    :return: Contents of the file as a string
    """
    with open(file_path, 'r') as file:
        text = file.read()
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


def get_chapter_from_pdf_txt(pdf_text):
    txt = repr(pdf_text)
    start_word = settings["RTF conversion last word in header"]
    end_word = settings["RTF conversion first word in footer"]
    try:
        found = re.search(pattern=f"(?<={start_word})([A-z0-9\\ \n-:()])*(?={end_word})", string=txt).group(0)
    except:
        found = re.search(pattern=f"([A-z0-9\\ \n-:()])*(?={end_word})", string=txt).group(0)
    found = found.replace("\\n", "")
    found = found.strip()
    return found


def break_chapter_to_lines(chapter, orientation="P"):
    if orientation == "P":
        lines = textwrap.wrap(chapter, settings["Vertical Toc characters per line"], break_long_words=False)
    else:
        lines = textwrap.wrap(chapter, settings["Horizontal Toc characters per line"], break_long_words=False)
    return lines


def compile_toc(chapters, pages, orientation):
    """
    Creates table of contents library from chapters and lengths of chapters
    :param orientation: Page orientation: either P for portrait or L for landscape
    :param chapters: List of chapter names
    :param pages: List of how many chapters each page takes
    :return: Table of contents dictionary
    """

    max_items = settings["Items on horizontal toc"] if orientation == "L" else settings["Items on vertical toc"]

    broken = [break_chapter_to_lines(chapter) for chapter in chapters]
    lines = sum([len(x) for x in broken])
    toc_pages = math.ceil(lines / max_items)
    print(f'toc pages: {toc_pages}')

    pages.insert(0, toc_pages)
    pages = list(accumulate(pages))
    pages = [x + 1 for x in pages]
    chapter_starts = pages[0:-1]
    toc = dict(zip(chapters, chapter_starts))
    return toc
