import time
import comtypes.client
from PyPDF2.merger import PdfFileMerger
from PyPDF2.pdf import PdfFileReader, PdfFileWriter
import helper_functions
from pdf_template import PDF
from helper_functions import *
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QObject


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
        chapter_name = get_chapter_name(text)
        chapters.append(chapter_name)
        num_pages = len(get_text_blocks(text))
        pages.append(num_pages)
    toc = compile_toc(chapters, pages, orientation=toc_orientation)
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
        print(output_file_name, format_number)

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
    finished = pyqtSignal()
    started = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        #if files is None:
        #    files = []
        #self.files = files
        #self.filename = filename
        #self.create_toc = create_toc
        #self.toc_orientation = toc_orientation
        #self.filetype = filetype
        #self.trash = []
        #self.engine = "word"
        self.create_toc = True
        self.files = None
        self.filename = None
        self.toc_orientation = "P"
        self.progress.connect(self.handle_event)
        self.engine = "word"
        self.trash = []

    def handle_event(self):
        pass

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

    def _set_engine(self, engine):
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
        if not self.filetype or not self.files:
            raise ValueError("Filetype, filename or files has not been set")
        if self.filetype == "rtf":
            self._create_pdf_from_rtf_files()
        elif self.filetype == "txt":
            self._create_pdf_from_txt_files()
        else:
            raise ValueError("Filetype not set")
        self._delete_trash()
        self.progress.emit(self.get_num_files() + 1)
        self.finished.emit()

    def _delete_trash(self):
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
        pdfs = []
        self.progress.emit(0)
        for count, file in enumerate(self.files):
            changed_file = change_filetype(file, "pdf", self.engine)
            pdfs.append(changed_file)
            self.progress.emit(count + 1)
        merger = PdfFileMerger()
        pages = []
        chapters = []
        for file in pdfs:
            read_pdf = PdfFileReader(file)
            txt = read_pdf.getPage(0)
            page_content = txt.extractText()
            try:
                chapter = helper_functions.get_chapter_from_pdf_txt(page_content)
                chapters.append(chapter)
            except:
                chapters.append("No chapters found")

            pages.append(read_pdf.getNumPages())
            merger.append(fileobj=file)
        if not self.create_toc:
            merger.write(self.master_file_name)
        else:
            merger.write("tmp.pdf")
        merger.close()
        self.trash += pdfs
        if self.create_toc:
            ### Creates table of contents pdf
            if not chapters:
                raise ValueError("Chapters not found")
            toc = compile_toc(chapters, pages, orientation=self.toc_orientation)
            pdf = PDF()
            pdf.set_title("")
            pdf.table_of_contents(toc, orientation=self.toc_orientation, create_hyperlink=False)
            pdf.output("toc.pdf", 'F')
            link_locations, page_locations = pdf.get_link_locations()
            pdf.close()
            time.sleep(2)

            link_locations = [change_coordinates(x, self.toc_orientation) for x in link_locations]  # Change the coordinate

            merger = PdfFileMerger()
            merger.append("toc.pdf")
            merger.append("tmp.pdf")
            merger.write("tmp2.pdf")
            merger.close()

            ### Create hyperlinks
            reader = PdfFileReader("tmp2.pdf")
            writer = PdfFileWriter()
            for i in range(reader.getNumPages()):
                page = reader.getPage(i)
                writer.addPage(page)
            for i in range(len(link_locations)):
                toc_page = 1
                if self.toc_orientation == "P":
                    toc_page = math.floor(i / settings["Items on vertical toc"])
                if self.toc_orientation == "L":
                    toc_page = math.floor(i / settings["Items on horizontal toc"])
                writer.addLink(pagenum=toc_page, pagedest=page_locations[i] - 1, rect=link_locations[i], fit="/Fit",
                               border=[0, 0, 0])
            with open(self.filename, 'wb') as out:
                writer.write(out)

            self.trash += ["tmp.pdf", "tmp2.pdf", "toc.pdf"]

    def _create_pdf_from_txt_files(self):
        pdf = PDF()
        title_set = False
        pdf.set_title("")

        if self.create_toc:
            toc = get_toc(self.files, self.toc_orientation)
            pdf.table_of_contents(toc, orientation=self.toc_orientation)

        for count, file in enumerate(self.files):
            text = get_text_from_file(file)
            self.progress.emit(count + 1)
            if not title_set:
                research_name = get_research_name(text)
                pdf.set_title(research_name)
                title_set = True
            program_info = get_program_info(text)
            chapter_name = get_chapter_name(text)
            for block in get_text_blocks(text):
                pdf.print_chapter(chapter_title=chapter_name, text_body=block,
                                  footer_text=program_info)
        pdf.output(self.filename, 'F')

