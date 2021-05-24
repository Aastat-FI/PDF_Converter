from builtins import filter

from fpdf import FPDF
import settings
from helper_functions import break_chapter_to_lines

PARAMETERS = settings.get_parameters()


def get_text_body_length(text_body):
    return len(text_body.splitlines())


class PDF(FPDF):

    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.footer_text = ""
        path_to_font = "CourierNewRegular.ttf"
        self.add_font('Courier New', '', path_to_font, uni=True)
        # Containing coordinates for link
        self.link_locations = []
        # Page numbers where links lead. Used for rtf conversion
        self.link_page = []
        self.writing_toc = False

    def table_of_contents(self, contents, orientation, create_hyperlink=True):
        """
        Creates a table of contents page at the first page.
        :param create_hyperlink: Boolean indicating if we want to create hyperlinks to toc items
        :param orientation: Page orientation. Values "P" or "L"
        :param contents: Dictionary where keys are chapter names and values are page numbers where chapter starts
        :return:
        """
        #  TODO: figure out why there is a need to use "Hack" to get toc items working
        self.writing_toc = True
        self.set_auto_page_break(True, margin=40)
        self.add_page(orientation=orientation)
        self.toc_header()
        self.set_font('Courier New', '', PARAMETERS["Toc font size"])
        first_item = True

        for chapter_name, page_number in contents.items():
            link = None
            if create_hyperlink:
                link = self.add_link()
                self.set_link(link, page=page_number)
            broken_text = break_chapter_to_lines(chapter_name)
            for line in broken_text:
                self.link_page.append(page_number)
                self.set_x(PARAMETERS["TOC x-offset"])
                if len(broken_text) == 1:
                    dots = self._get_toc_dots(line, first_line=True)
                    if first_item:
                        first_item = False
                    text = f'{line}{dots}{page_number}'
                else:
                    if line == broken_text[0]:
                        text = line
                    elif line == broken_text[-1]:
                        if first_item:
                            first_item = False
                        dots = self._get_toc_dots(line, first_line=False)
                        text = f'{" " * 5}{line}{dots}{page_number}'
                    else:
                        text = f'{" " * 5}{line}'

                link_loc = [self.x, self.y + .5 - .5 * self.font_size, self.get_string_width(text), self.font_size]
                link_loc = [x * self.k for x in link_loc]  # Change back to pixels

                self.link_locations.append(link_loc)
                self.cell(0, 9, text, link=link)
                self.ln(8)

    def get_link_locations(self):
        return self.link_locations, self.link_page

    def text_header(self):
        self.set_font('Courier New', '', 8)
        self.set_y(PARAMETERS["Header y-offset"])
        w = self.get_string_width(self.title) + 6
        self.set_x((self.w - w) / 2)
        self.cell(w, 9, self.title)
        self.ln(PARAMETERS["Distance between header and chapter title"])

    def toc_header(self):
        self.set_font('Courier New', '', 16)
        self.set_y(PARAMETERS["Header y-offset"])
        self.set_x(PARAMETERS["TOC x-offset"])
        self.cell(0, 9, 'Table of Contents')
        self.ln(2)
        self.set_x(PARAMETERS["TOC x-offset"])
        self.cell(0, 9, "_" * 17)
        self.ln(14)

    def header(self):
        """
        Creates header to page. Header text is the study name and is set by set_title method
        :return:
        """
        if self.writing_toc:
            self.toc_header()
        else:
            self.text_header()

    def _get_toc_dots(self, chapter_name, first_line=True):
        characters = len(chapter_name)

        if self.cur_orientation == "P":
            num_dots = PARAMETERS["Vertical Toc characters per line"] - characters
        elif self.cur_orientation == "L":
            num_dots = PARAMETERS["Horizontal Toc characters per line"] - characters
        else:
            raise ValueError("Orientation not supported for toc-creation")
        if first_line:
            num_dots += 5
        dots = "." * (num_dots + 5)
        return dots

    def _add_empty_line(self):
        """
        Creates dashed line to indicate where page ends
        :return:
        """
        empty_line = "_"
        if self.cur_orientation == "L":
            empty_line = "_" * 123
            w = self.get_string_width(empty_line) + 6
            self.set_x((self.w - w) / 2)
        if self.cur_orientation == "P":
            empty_line = "_" * 70
            w = self.get_string_width(empty_line) + 6
            self.set_x((self.w - w) / 2)
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
        self.set_x((self.w - w) / 2)
        self.cell(0, 6, label)
        self.ln(PARAMETERS["Distance between chapter title and chapter body"])
        self._add_empty_line()

    def _chapter_body(self, text_body):
        """
        Prints the text to the body of chapter
        :param text_body: Python string what to print to the page
        :return:
        """
        self.set_font('Courier New', '', 8)
        self.set_x(PARAMETERS["Chapter body x-offset"])
        self.set_auto_page_break(False)
        self.multi_cell(0, PARAMETERS["Distance between lines of chapter body"], text_body)
        self.set_auto_page_break(True)
        self.ln()

    def _set_footer_text(self, text):
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
        self.writing_toc = False
        if get_text_body_length(text_body) > 50:
            self.add_page(orientation="P")
        else:
            self.add_page(orientation="L")
        self._set_footer_text(footer_text)
        self.chapter_title(chapter_title)
        self._chapter_body(text_body)
