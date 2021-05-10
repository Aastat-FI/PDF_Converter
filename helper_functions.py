import os


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


def create_combined_rtf(rtf_files, save_filename="combined.rtf"):
    """
    Appends multiple rtf files together
    :param rtf_files: list of absolute filepaths of rtf files
    :param save_filename: filename to save the file to
    :return: absolute path to created file
    """
    main_str = ""
    for file in rtf_files:
        main_str += get_text_from_file(file)

    if save_filename.split(".")[-1] != "rtf":
        save_filename += ".rtf"

    with open(save_filename, 'w') as file:
        file.write(main_str)
    print(f'File saved as {save_filename}')
    return save_filename
