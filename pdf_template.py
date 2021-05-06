from fpdf import FPDF

# TODO: Rename parameters to something sensible
PARAMETERS = {
    "A1": 20,
    "A2": 5,
    "A3": 40,
    "A4": 7,
    "A5": -40,
    "A6": 4,
    "TOC x-offset": 30
}
empty_line = "_" * 123


class PDF(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.footer_text = ""
        self.add_font('Courier New', '', 'CourierNewRegular.ttf', uni=True)

    def table_of_contents(self, contents):
        #  TODO: figure out why there is a need to use "Hack" to get toc items working
        self.add_page()
        self.set_font('Courier New', '', 16)
        self.set_x(PARAMETERS["TOC x-offset"])
        self.cell(0, 9, 'Table of Contents')
        self.set_font('Times', '', 12)
        self.ln(10)
        first_item = True
        for chapter_name, page_number in contents.items():
            self.set_x(PARAMETERS["TOC x-offset"])
            w = self.get_string_width(chapter_name)
            if first_item:
                first_item = False
                self.cell(0, 9,
                          f'{chapter_name}{"." * (270 - 2 * PARAMETERS["TOC x-offset"] - int(w) -3)}{page_number}')
            else:
                self.cell(0, 9, f'{chapter_name}{"." * (270 - 2 * PARAMETERS["TOC x-offset"] - int(w))}{page_number}')
            self.ln(8)

    def header(self):
        self.set_font('Courier New', '', 8)
        self.set_y(PARAMETERS["A1"])
        w = self.get_string_width(self.title) + 6
        self.set_x((300 - w) / 2)
        self.cell(w, 9, self.title)
        self.ln(PARAMETERS["A2"])

    def add_empty_line(self):
        w = self.get_string_width(empty_line) + 6
        self.set_x((300 - w) / 2)
        self.cell(0, 6, empty_line)
        self.ln(1)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(PARAMETERS["A5"])
        self.add_empty_line()
        self.ln(PARAMETERS["A6"])
        # Arial italic 8
        self.set_font('Courier New', '', 8)
        # Text color in gray
        # Page number
        self.cell(0, 10, self.footer_text, 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Courier New', '', 8)
        w = self.get_string_width(label) + 6
        self.set_x((300 - w) / 2)
        self.cell(0, 6, label)
        self.ln(PARAMETERS["A4"])
        self.add_empty_line()

    def chapter_body(self, text_body):
        self.set_font('Courier New', '', 8)
        self.set_x(PARAMETERS["A3"])
        self.multi_cell(0, 3.3, text_body)
        self.ln()

    def set_footer_text(self, text):
        self.footer_text = text

    def print_chapter(self, chapter_title, text_body, footer_text):
        self.add_page()
        self.set_footer_text(footer_text)
        self.chapter_title(chapter_title)
        self.chapter_body(text_body)
