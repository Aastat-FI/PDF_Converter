from fpdf import FPDF
import os

PARAMETERS = {
    "Header y-offset": 20,
    "Distance between header and chapter title": 5,
    "Chapter body x-offset": 40,
    "Distance between chapter title and chapter body": 7,
    "Footer y-offset from bottom": -40,
    "Distance between lower-dashed line and footer": 4,
    "TOC x-offset": 30,
    "Distance between lines of chapter body": 3.3 #Might be 3.35 from lookin at html file
}


def get_text_body_length(text_body):
    return len(text_body.splitlines())


class PDF(FPDF):
    """
    Custom PDF class to replicate the wanted format
    """
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.footer_text = ""
        path_to_font = os.path.dirname(__file__) + "\\fonts\\CourierNewRegular.ttf"
        path_to_font = "CourierNewRegular.ttf"
        self.add_font('Courier New', '', "CourierNewRegular.ttf", uni=True)

    def table_of_contents(self, contents, orientation):
        """
        Creates a table of contents page at the first page.
        :param orientation:
        :param contents: Dictionary where keys are chapter names and values are page numbers where chapter starts
        :return:
        """
        #  TODO: figure out why there is a need to use "Hack" to get toc items working
        self.add_page(orientation=orientation)
        self.set_font('Courier New', '', 16)
        self.set_x(PARAMETERS["TOC x-offset"])
        self.cell(0, 9, 'Table of Contents')
        self.set_font('Times', '', 12)
        self.ln(10)
        first_item = True
        for chapter_name, page_number in contents.items():
            self.set_x(PARAMETERS["TOC x-offset"])
            dots = self._get_toc_dots(chapter_name, first_item)
            if first_item:
                first_item = False
                self.cell(0, 9, f'{chapter_name}{dots}{page_number}')
            else:
                self.cell(0, 9, f'{chapter_name}{dots}{page_number}')
            self.ln(8)

    def header(self):
        """
        Creates header to page. Header text is the study name and is set by set_title method
        :return:
        """
        self.set_font('Courier New', '', 8)
        self.set_y(PARAMETERS["Header y-offset"])
        w = self.get_string_width(self.title) + 6
        self.set_x((300 - w) / 2)
        self.cell(w, 9, self.title)
        self.ln(PARAMETERS["Distance between header and chapter title"])

    def _get_toc_dots(self, chapter_name, first_item=True):
        w = self.get_string_width(chapter_name)
        if self.cur_orientation == "P":
            if first_item:
                dots = "." * (200 - 2 * PARAMETERS["TOC x-offset"] - int(w) - 3)
                return dots
            else:
                dots = "." * (200 - 2 * PARAMETERS["TOC x-offset"] - int(w))
                return dots
        elif self.cur_orientation == "L":
            if first_item:
                dots = "." * (270 - 2 * PARAMETERS["TOC x-offset"] - int(w) - 3)
                return dots
            else:
                dots = "." * (270 - 2 * PARAMETERS["TOC x-offset"] - int(w))
                return dots
        else:
            raise ValueError("Orientation not supported for toc-creation")

    def _add_empty_line(self, length=123):
        """
        Creates dashed line to indicate where page ends
        :param length: Length of the line.
        :return:
        """
        empty_line = "_" * length
        w = self.get_string_width(empty_line) + 6
        self.set_x((300 - w) / 2)
        self.cell(0, 6, empty_line)
        self.ln(1)

    def footer(self):
        """
        Prints the footer to page. Footer is program info where the text files are gotten from
        :return:
        """
        self.set_y(PARAMETERS["Footer y-offset from bottom"])
        self._add_empty_line()
        self.ln(PARAMETERS["Distance between lower-dashed line and footer"])
        self.set_font('Courier New', '', 8)
        self.cell(0, 10, self.footer_text, 0, 0, 'C')

    def chapter_title(self, label):
        """
        Prints the chapter title under the header.
        :param label: Title of the chapter
        :return:
        """
        self.set_font('Courier New', '', 8)
        w = self.get_string_width(label) + 6
        self.set_x((300 - w) / 2)
        self.cell(0, 6, label)
        self.ln(PARAMETERS["Distance between chapter title and chapter body"])
        self._add_empty_line()

    def chapter_body(self, text_body):
        """
        Prints the text to the body of chapter
        :param text_body: Python string what to print to the page
        :return:
        """
        self.set_font('Courier New', '', 8)
        self.set_x(PARAMETERS["Chapter body x-offset"])
        self.multi_cell(0, PARAMETERS["Distance between lines of chapter body"], text_body)
        self.ln()

    def set_footer_text(self, text):
        """
        Sets the footer text that footer function prints out
        :param text: Text to print at the footer
        :return:
        """
        self.footer_text = text

    def print_chapter(self, chapter_title, text_body, footer_text):
        """
        Main usage method of the class. Prints the page from the given arguments
        :param chapter_title:
        :param text_body:
        :param footer_text:
        :return:
        """
        if get_text_body_length(text_body=text_body) > 50:
            self.add_page(orientation="P")
        else:
            self.add_page(orientation="L")
        self.set_footer_text(footer_text)
        self.chapter_title(chapter_title)
        self.chapter_body(text_body)

