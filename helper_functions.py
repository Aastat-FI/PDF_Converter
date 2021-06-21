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


def get_info_lines(text):
    """
    Gets research name from block of text
    :param text: Python string, in the program defined as block
    :return: Program name
    """
    text_lines = []
    rows_returned = 0
    for row in text.splitlines():
        if "____" in row or rows_returned == settings["Max header lines"] + settings["TOC level"]:
            return text_lines
        if is_empty_line(row):
            continue
        rows_returned += 1
        text_lines.append(row)


def get_program_info(text):
    """
    Returns program info text from the text block
    :param text: Python string
    :return: program info
    """
    for row in text.splitlines()[::-1]:
        if is_empty_line(row):
            pass
        else:
            return row


def is_empty_line(text):
    """
    Helper function to check if there is any symbols on given line
    :param text: Python string
    :return: Boolean indicating emptiness of string
    """
    return len(text.strip()) == 0


def get_text_blocks(text):
    """
    Returns text blocks that contain datatables. Text file is split to pieces from long dashed lines
    and these are referred to blocks. Blocks either contain data tables or information such as study or program info.
    :param text: Python string
    :return: Block of string that contains data tables
    """
    symbol = settings["Line symbol"]
    blocks = []
    num_lines = 0
    different_sizes = []
    for line in text.splitlines():
        if symbol * 20 in line:
            num_lines = len(line.strip())
            different_sizes.append(num_lines)

    split_re = f"(?<!{symbol})[{symbol}]{'{'}{num_lines}{'}'}(?!{symbol})"

    one_size = False
    if len(set(different_sizes)) == 1:
        one_size = True
    if settings["Two linebreaks"] == "False":
        text = fix_format(text, max(different_sizes) + 1)
        split_re = f"(?<!{symbol})[{symbol}]{'{'}{max(different_sizes) + 1}{'}'}(?!{symbol})"
        one_size = False

    text_split = re.split(split_re, text)
    if one_size:
        for count, block in enumerate(text_split):
            if count % 3 == 0 or count % 3 == 1:
                continue
            else:
                block = remove_empty_lines(block)
                blocks.append(block)
    else:
        for count, block in enumerate(text_split):
            if count % 2 == 0:
                continue
            else:
                block = remove_empty_lines(block)
                blocks.append(block)
    return blocks


def fix_format(text, num):
    """
    If there is not two linebreaks (_____ lines etc.) this function creates one
    :param text: Text where to add the linebreak
    :param num: Number of symbols to add
    :return: Returns the modified text
    """
    pieces = text.splitlines()
    new = []
    for i, row in enumerate(pieces):
        try:
            if settings["First word in footer"] in pieces[i + 1]:
                new.append(settings["Line symbol"] * num)
            if settings["First word in footer"] in pieces[i - 4]:
                new.append(settings["Line symbol"] * num)
        except IndexError:
            pass
        new.append(row)
    return "\n".join(new)


def remove_empty_lines(block_of_text):
    """
    Helper function to delete all the empty lines from string
    :param block_of_text: String
    :return: Given string without empty lines
    """
    text = os.linesep.join([s for s in block_of_text.splitlines() if s])
    return text


def get_chapter_from_pdf_txt(pdf_text):
    """
    Helper function to extract the "chapter name" from the text document. Needed in rtf conversion
    :param pdf_text: Text from the pdf file. By default it connects header - chapter- footer - text body so we can
    extract the chapter name with regex if we know the last word in header and first word in footer
    :return: Returns the "chapter name"
    """
    txt = repr(pdf_text)
    start_word = settings["Last word in header"]
    end_word = settings["First word in footer"]
    try:
        found = re.search(pattern=f"(?<={start_word})([A-z0-9\\ \n-:()])*(?={end_word})", string=txt).group(0)
    except:
        found = re.search(pattern=f"([A-z0-9\\ \n-:()])*(?={end_word})", string=txt).group(0)
    found = found.replace("\\n", "")
    found = found.strip()
    return found


def break_chapter_to_lines(chapter, orientation="P"):
    """
    Helper function to break long lines of text into shorter ones. Used when creating table of contents
    :param chapter: Chapter name text
    :param orientation: Page orientation
    :return: Returns the broken lines
    """
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

    pages.insert(0, toc_pages)
    pages = list(accumulate(pages))
    pages = [x + 1 for x in pages]
    chapter_starts = pages[0:-1]
    toc = dict(zip(chapters, chapter_starts))
    return toc
