from fpdf import FPDF
import settings
import textwrap

PARAMETERS = settings.get_parameters()


def get_text_body_length(text_body):
    return len(text_body.splitlines())


class PDF(FPDF):

    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.footer_text = ""
        path_to_font = "CourierNewRegular.ttf"
        self.add_font('Courier New', '', path_to_font, uni=True)
        self.link_locations = []
        self.toc_page = []

    def table_of_contents(self, contents, orientation, create_hyperlink=True):
        """
        Creates a table of contents page at the first page.
        :param create_hyperlink: Boolean indicating if we want to create hyperlinks to toc items
        :param orientation: Page orientation. Values "P" or "L"
        :param contents: Dictionary where keys are chapter names and values are page numbers where chapter starts
        :return:
        """
        #  TODO: figure out why there is a need to use "Hack" to get toc items working
        self.set_auto_page_break(True, margin=40)
        self.add_page(orientation=orientation)
        self.set_font('Courier New', '', 16)
        self.set_x(PARAMETERS["TOC x-offset"])
        self.cell(0, 9, 'Table of Contents')
        self.set_font('Times', '', PARAMETERS["Toc font size"])
        self.ln(10)
        first_item = True

        for chapter_name, page_number in contents.items():
            link = None
            if create_hyperlink:
                link = self.add_link()
                self.set_link(link, page=page_number)
            self.set_x(PARAMETERS["TOC x-offset"])
            dots = self._get_toc_dots(chapter_name, first_item)
            if first_item:
                first_item = False
            text = f'{chapter_name}{dots}{page_number}'

            link_loc = [self.x, self.y + .5 - .5 * self.font_size, self.get_string_width(text), self.font_size]
            link_loc = [x * self.k for x in link_loc]  # Change back to pixels

            self.link_locations.append(link_loc)
            self.cell(0, 9, text, link=link)
            self.ln(8)

    def get_link_locations(self):
        return self.link_locations




    def header(self):
        """
        Creates header to page. Header text is the study name and is set by set_title method
        :return:
        """
        self.set_font('Courier New', '', 8)
        self.set_y(PARAMETERS["Header y-offset"])
        w = self.get_string_width(self.title) + 6
        self.set_x((self.w - w) / 2)
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
        self.multi_cell(0, PARAMETERS["Distance between lines of chapter body"], text_body)
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
        if get_text_body_length(text_body) > 50:
            self.add_page(orientation="P")
        else:
            self.add_page(orientation="L")
        self._set_footer_text(footer_text)
        self.chapter_title(chapter_title)
        self._chapter_body(text_body)
