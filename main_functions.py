import time
import comtypes.client
from PyPDF2.merger import PdfFileMerger
from PyPDF2.pdf import PdfFileReader, PdfFileWriter
import helper_functions
from pdf_template import PDF
from helper_functions import *
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QObject


def get_toc(files, toc_orientation):
    """
    Creates a dictionary that has all the chapter names and page numbers from the list of text files
    :param toc_orientation: Parameter that specifies table of contents orientation
    :param files: list of absolute paths of files
    :return: returns library where keys are chapter names and values are page numbers where they start
    """
    chapters = []
    pages = []
    for file in files:
        text = get_text_from_file(file)
        info_lines = get_info_lines(text)
        chapter_name_rows = info_lines[settings["TOC level"]:]
        chapter_name = "\n".join(chapter_name_rows)
        chapters.append(chapter_name)
        num_pages = len(get_text_blocks(text))
        pages.append(num_pages)
    toc = compile_toc(chapters, pages, orientation=toc_orientation)
    return toc


def change_coordinates(arr, orientation):
    """
    Changes the coordinate system from [XUL, YUL, WIDTH, HEIGHT] to [XLL, YLL, XUR, YUR]. Original origo is at the top
    left corner of the page, new one is at the bottom left corner of the page. For some reason x axis is stretched
    out a bit so I fix it by multiplying it byt correction factor denoted by x_cor_factor
    :param arr: Original coordinates
    :param orientation: Page orientation
    :return:
    """
    paper_h, paper_w = 841.89, 595.89
    x_cor_factor = 1.026
    new = [0, 0, 0, 0]
    new[0] = arr[0] * x_cor_factor
    new[2] = (arr[0] + arr[2]) * x_cor_factor
    if orientation == "P":
        new[1] = paper_h - arr[1] - arr[3]
        new[3] = new[1] - arr[3]
    elif orientation == "L":
        new[1] = paper_w - arr[1] - arr[3]
        new[3] = new[1] - arr[3]
    else:
        raise ValueError("Unknown page orientation")
    return new


### TODO: ABILITY TO CONVERT MULTIPLE FILES WITHOUT CLOSING WORD IN BETWEEN
def change_filetype(input_file, output_filetype, backend_converter='word', output_file_name=None):
    """
    Converts the input file to requested filetype and saves it as specified output file. Uses Microsoft Word backend but
        it is possible to include openoffice support
    :param input_file: Absolute path of the current file
    :param output_filetype: Filetype to convert the input file. Supported filetypes:
        rtf, pdf, docx, doc, html, xml
    :param output_file_name: name and path for output file. If left blank saves in the same folder with same name as input
        file
    :param backend_converter: What tool to use to convert the files. Options: word or libreoffice
    :return: Does not return anything
    """

    filetypes = {
        "rtf": 6,
        "pdf": 17,
        "docx": 16,
        "doc": 0,
        "html": 8,
        "xml": 19,
        "txt": 7,
        "windows_txt": 3
    }
    if output_file_name is None:
        filename = input_file.split(".")[0]
        output_file_name = filename + "." + output_filetype
    if backend_converter == 'word':
        if output_filetype not in filetypes:
            raise ValueError("Output filetype not found in supported filetypes.")
        try:
            word_backend = comtypes.client.CreateObject("Word.Application")
            word_backend.Visible = False
        except:
            raise RuntimeError("Error setting up Word application")
        try:
            document = word_backend.Documents.Open(input_file)
        except:
            word_backend.Quit()
            raise FileNotFoundError("Error opening file: format not supported or file not found")
        format_number = filetypes[output_filetype]

        time.sleep(2)
        document.SaveAs(output_file_name, FileFormat=format_number)
        document.Close()
        word_backend.Quit()

    elif backend_converter == "libre-office":
        os.system(f'soffice --headless --convert-to {output_filetype} {input_file}')
        # os.system(f'libreoffice --headless --convert-to {output_filetype} {input_file}')
        # os.system(f'libreoffice6.3 --headless --convert-to {output_filetype} {input_file}')

    else:
        raise ValueError("Not valid backend converter")

    return output_file_name


class Converter(QThread):
    """
    Main class for file conversion. This class is created and controlled by gui.py
    """
    finished = pyqtSignal()
    started = pyqtSignal()
    progress = pyqtSignal(int)
    send_toc = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.create_toc = True
        self.files = None
        self.filename = None
        self.toc_orientation = "P"
        self.engine = "word"
        self.trash = []
        self.chapters = []
        self.pages = []
        self.toc_accepted = False

    def set_files(self, files):
        self.files = files

    def set_filename(self, filename):
        self.filename = filename
        self._fix_filename()

    def set_create_toc(self, create_toc):
        self.create_toc = create_toc

    def set_toc_orientation(self, toc_orientation):
        self.toc_orientation = toc_orientation

    def set_filetype(self, filetype):
        self.filetype = filetype

    def get_num_files(self):
        if self.files is None:
            return 0
        else:
            return len(self.files)

    def _fix_filename(self):
        if ".pdf" not in self.filename:
            self.filename = self.filename + ".pdf"

    def set_engine(self, engine):
        self.engine = engine

    def filetype_set(self):
        return not (self.filetype is None)

    def get_filetype(self):
        return self.filetype

    def files_set(self):
        return not (self.files is None)

    def filename_set(self):
        return not (self.filename is None)

    def convert(self):
        """
        Main function to make the conversion. When the parameters are set this higher level function calls either
        rtf creating function or pdf creating function. Also deletes temporary trash files that rtf conversion
        creates
        :return:
        """
        if not self.filetype or not self.files:
            raise ValueError("Filetype, filename or files has not been set")
        if self.filetype == "rtf":
            self._create_pdf_from_rtf_files()
            if self.create_toc:
                self.create_toc_pdf_and_append_it()

        elif self.filetype == "txt":
            self._create_pdf_from_txt_files()
        else:
            raise ValueError("Filetype not set")
        self._delete_trash()
        self.progress.emit(self.get_num_files() + 1)
        self.finished.emit()

    def _delete_trash(self):
        """
        Deletes the temporary files created by conversions. At the moment only *.rtf file conversion creates temporary
        files
        :return:
        """
        for file in self.trash:
            try:
                os.remove(file)
            except FileNotFoundError:
                path = os.path.abspath(".")
                file = path + "/" + file
                os.remove(file)

    def converter_ready(self):
        return self.files_set() and self.filename_set() and self.filetype_set()

    def _create_pdf_from_rtf_files(self):
        """
        Main function to create pdf file from set of rtf files. Adding the hyperlinks is done by other function
        :return:
        """
        pdfs = []
        self.progress.emit(0)
        for count, file in enumerate(self.files):
            #  Changes the rtf tiles to pdf files using change_filetype helper function
            changed_file = change_filetype(file, "pdf", self.engine)
            pdfs.append(changed_file)
            self.progress.emit(count + 1)
        merger = PdfFileMerger()
        pages = []
        chapters = []
        for file in pdfs:
            #  Loop for appending the created pdf files together.
            read_pdf = PdfFileReader(file)
            txt = read_pdf.getPage(0)
            page_content = txt.extractText()
            try:
                #  Tries to get "chapter name from the text contents of the pdf
                chapter = helper_functions.get_chapter_from_pdf_txt(page_content)
                chapters.append(chapter)
            except:
                #  If it doesn't find any "chapter" names from the pdf text then it pulls the chapter name from the
                #  name of the pdf
                chapter = os.path.basename(file)
                chapter = chapter.split(".")[0]
                chapter = chapter.replace("_", " ")
                chapters.append(chapter)

            pages.append(read_pdf.getNumPages())
            merger.append(fileobj=file)
        self.pages = pages
        self.chapters = chapters
        if not self.create_toc:
            merger.write(self.master_file_name)
        else:
            merger.write("tmp.pdf")
        merger.close()
        self.trash += pdfs

    def _create_pdf_from_txt_files(self):
        """
        Main function from creating the pdf file from *.txt files. Called by convert()
        :return:
        """
        pdf = PDF()
        pdf.set_title("")

        if self.create_toc:
            #  Extracts table of contents from "chapter names" and sends it for confirmation to gui.py. Also creates
            #  the table of contents page
            self.toc_dict = get_toc(self.files, self.toc_orientation)
            self.send_toc.emit(self.toc_dict)

            while not self.toc_accepted:
                # Waits for user confirmation
                time.sleep(1)
                pass
            pdf.table_of_contents(self.toc_dict, orientation=self.toc_orientation)

        for count, file in enumerate(self.files):
            #  Loop creating the pages of the pdf file from *.txt files. Loops files, gets the text then gets required
            #  information from the given text and sends it to pdf_template class
            text = get_text_from_file(file)
            info_text = get_info_lines(text)
            header_text = "\n".join(info_text[0:settings["TOC level"]])
            pdf.set_title(header_text.strip())
            program_info = get_program_info(text)
            chapter_name = "\n".join(info_text[settings["TOC level"]:])
            self.progress.emit(count + 1)

            for block in get_text_blocks(text):
                pdf.print_chapter(chapter_title=chapter_name.strip(), text_body=block,
                                  footer_text=program_info.strip())
        pdf.output(self.filename, 'F')

    def create_toc_pdf_and_append_it(self):
        """
        Appends table of contents pdf and the text pages together. Then calls function to add the hyperlinks to the
        the hyperlinks to table of contents. Only used by rtf conversion
        :return:
        """
        link_locations, page_locations = self._create_toc_pdf_for_rtf()
        link_locations = [change_coordinates(x, self.toc_orientation) for x in link_locations]  # Coordinate change
        merger = PdfFileMerger()
        merger.append("toc.pdf")
        merger.append("tmp.pdf")
        merger.write("tmp2.pdf")
        merger.close()

        self._create_hyperlinks(link_locations, page_locations)

        self.trash += ["tmp.pdf", "tmp2.pdf", "toc.pdf"]

    def set_toc_dict(self, toc_dict):
        self.toc_dict = toc_dict

    def accept_toc(self):
        self.toc_accepted = True

    def _create_hyperlinks(self, link_locations, page_locations):
        """
        Helper function for appending the hyperlinks. Loops through the the links and adds them to the table of contents
        page. Only used by rtf conversion
        :param link_locations:
        :param page_locations:
        :return:
        """
        reader = PdfFileReader("tmp2.pdf")
        writer = PdfFileWriter()
        for i in range(reader.getNumPages()):
            #  We need to read the temporary pdf and then append the links to it. This could also be moved to create_
            #  toc_and_append_it function but the function grows a bit too large.
            page = reader.getPage(i)
            writer.addPage(page)
        for i in range(len(link_locations)):
            toc_page = 1
            #  If statements give the page in which to add the hyperlink
            if self.toc_orientation == "P":
                toc_page = math.floor(i / settings["Items on vertical toc"])
            if self.toc_orientation == "L":
                toc_page = math.floor(i / settings["Items on horizontal toc"])
            writer.addLink(pagenum=toc_page, pagedest=page_locations[i] - 1, rect=link_locations[i], fit="/Fit",
                           border=[0, 0, 0])
        with open(self.filename, 'wb') as out:
            writer.write(out)

    def _create_toc_pdf_for_rtf(self):
        """
        Super short helper function for creating the table of contents page for the rtf conversion. Functionality could/
        should be moved to other funtion
        :return:
        """
        toc = compile_toc(self.chapters, self.pages, orientation=self.toc_orientation)
        self.send_toc.emit(toc)
        while not self.toc_accepted:  # Waits for user confirmation
            time.sleep(1)

        pdf = PDF()
        pdf.set_title("")
        pdf.table_of_contents(self.toc_dict, orientation=self.toc_orientation, create_hyperlink=False)
        pdf.output("toc.pdf", 'F')
        link_locations, page_locations = pdf.get_link_locations()
        pdf.close()
        time.sleep(2)
        return link_locations, page_locations
