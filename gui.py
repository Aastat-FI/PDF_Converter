from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QApplication, QFileDialog, QRadioButton, \
    QButtonGroup, QTextBrowser, QCheckBox, QStyleFactory
from main_functions import create_pdf_from_txt_files, create_pdf_from_rtf_files

import main_functions


### TODO: COMMENT
# noinspection PyArgumentList
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.files = []
        self.filetype = "rtf"
        self.engine = "Word"
        self.toc_orientation = "P"
        self.save_location = ""
        self.setLayout(QVBoxLayout())
        self.setWindowTitle("PDF compiler")
        self.label_above_text_box = QLabel("Selected files:")
        self.big_text_box = QTextBrowser()
        self.select_file_label = QLabel("Choose filetype")
        self.rtf_button = QRadioButton(".*rtf files", clicked=lambda: self._set_filetype("rtf"))
        self.rtf_button.setChecked(True)
        self.txt_button = QRadioButton(".*txt files", clicked=lambda: self._set_filetype("txt"))
        self.file_buttons = QButtonGroup()
        self.file_buttons.addButton(self.rtf_button)
        self.file_buttons.addButton(self.txt_button)

        self.my_button = QPushButton("Choose Files", clicked=lambda: self._select_files())

        self.engine_label = QLabel("Choose engine (only used for *.rtf files)")
        self.engine_buttons = QButtonGroup()
        self.word_button = QRadioButton("Word", clicked=lambda: self._set_engine("word"))
        self.word_button.setChecked(True)
        self.open_office_button = QRadioButton("Open Office", clicked=lambda: self._set_engine("of"))
        self.engine_buttons.addButton(self.word_button)
        self.engine_buttons.addButton(self.open_office_button)

        self.h_toc_orientation_button = QRadioButton("Horizontal table of contents",
                                                     clicked=lambda: self._set_toc_orientation("L"))
        self.v_toc_orientation_button = QRadioButton("Vertical table of contents",
                                                     clicked=lambda: self._set_toc_orientation("P"))

        self.toc_button = QCheckBox("Generate table of contents", clicked=lambda: self._set_toc_bool())
        self.compile_button = QPushButton("Compile from selected files", clicked=lambda: self._compile())

        self.save_location_button = QPushButton("Select file save location", clicked=lambda: self._set_save_location())
        self.save_file_label = QLabel("Save location not yet selected")

        self.layout().addWidget(self.select_file_label)
        self.layout().addWidget(self.rtf_button)
        self.layout().addWidget(self.txt_button)
        self.layout().addWidget(self.my_button)
        self.layout().addWidget(self.engine_label)
        self.layout().addWidget(self.word_button)
        self.layout().addWidget(self.open_office_button)
        self.layout().addWidget(self.toc_button)
        self.layout().addWidget(self.toc_button)
        self.layout().addWidget(self.v_toc_orientation_button)
        self.layout().addWidget(self.h_toc_orientation_button)
        self.layout().addWidget(self.save_location_button)
        self.layout().addWidget(self.save_file_label)
        self.layout().addWidget(self.compile_button)
        self.layout().addWidget(self.label_above_text_box)
        self.layout().addWidget(self.big_text_box)
        self.show()

    def _select_files(self):
        dialog = QFileDialog()
        self.label_above_text_box.setText("Selected files:")
        file_filter = "All files"
        if not self.filetype:
            self.big_text_box.setText("Please select filetype first")
            return None
        else:
            if self.filetype == "txt":
                file_filter = 'Text file (*.txt)'
            elif self.filetype == "rtf":
                file_filter = 'Rich Text Format file (*.rtf)'

            filename = dialog.getOpenFileNames(filter=file_filter)
            self.files = filename[0]
        file_string = ""
        for file in filename[0]:
            file_string += file
            file_string += "\n"
        self.big_text_box.setText(file_string)

    def _set_filetype(self, filetype):
        self.filetype = filetype

    def _set_engine(self, engine):
        self.engine = engine

    def _set_toc_orientation(self, orientation):
        self.toc_orientation = orientation

    def _set_save_location(self):
        dialog = QFileDialog()
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_() == QFileDialog.Accepted:
            file = dialog.selectedFiles()[0]
            self.save_location = file
            self.save_file_label.setText(f"Save file location \n{file}")

    def _set_toc_bool(self):
        if self.toc_button.isChecked():
            self.v_toc_orientation_button.setChecked(True)
            self.toc_orientation = "P"

    def _compile(self):
        create_toc = self.toc_button.isChecked()
        if not self.save_location:
            self.compile_button.setText("Compile from selected files\n Select save location first!")
            return None
        created_file_name = self.save_location + "\\compiled.pdf"
        if not self.files:
            self.big_text_box.setText("Select files first!")
            return None
        if self.filetype == "txt":
            create_pdf_from_txt_files(self.files, created_file_name, create_toc, self.toc_orientation)
        elif self.filetype == "rtf":
            self.big_text_box.setText("Compiling PDF from rtf files. \n This may take some time \nDo not open "
                                      "the selected engine while this program is running")
            create_pdf_from_rtf_files(self.files, created_file_name, create_toc, self.toc_orientation)
        else:
            self.big_text_box.setText("Something went wrong")
            return None

        self.label_above_text_box.setText("Compiled successfully")
        self.compile_button.setText("Compile from selected files")

        page_orientation = "Vertical" if self.toc_orientation == "P" else "Horizontal"
        if create_toc:
            compile_text = f"PDF compiled as {created_file_name} \nTable of contents page orientation: \n{page_orientation}"
        else:
            compile_text = f"PDF compiled as {created_file_name} \nTable of contents page not created"
        self.big_text_box.setText(compile_text)


