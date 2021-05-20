from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QFileDialog, QRadioButton, \
    QButtonGroup, QTextBrowser, QCheckBox, QProgressBar
from main_functions import Converter
from settings import get_parameters


parameters = get_parameters()


### TODO: COMMENT
# noinspection PyArgumentList
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.filetype_set = False
        self.save_location = ""
        self.converter = Converter()

        self.create_ui()

    def create_thread(self):
        self.thread = QThread()
        self.thread.finished.connect(self._update_finished_text)
        self.converter.moveToThread(self.thread)
        self.thread.started.connect(self.converter.convert)
        self.converter.finished.connect(self.thread.quit)
        #self.converter.finished.connect(self.converter.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.converter.progress.connect(self._on_progress_update)


    def create_ui(self):
        self.setLayout(QVBoxLayout())
        self.setWindowTitle("PDF compiler")
        self.label_above_text_box = QLabel("Selected files:")
        self.big_text_box = QTextBrowser()
        self.select_file_label = QLabel("Choose filetype")
        self.rtf_button = QRadioButton(".*rtf files", clicked=lambda: self._set_filetype("rtf"))
        self.rtf_button.setChecked(True)
        self.converter.set_filetype("rtf")
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
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.layout().addWidget(self.progress_bar)
        self.show()


    def _select_files(self):
        dialog = QFileDialog()
        self.label_above_text_box.setText("Selected files:")
        file_filter = "All files"
        if not self.converter.filetype_set():
            self._update_text_window("Please select filetype first")
            return None
        else:
            if self.converter.get_filetype() == "txt":
                file_filter = 'Text file (*.txt)'
            elif self.converter.get_filetype() == "rtf":
                file_filter = 'Rich Text Format file (*.rtf)'

            filename = dialog.getOpenFileNames(filter=file_filter)
            self.converter.set_files(filename[0])
        file_string = ""
        for file in filename[0]:
            file_string += file
            file_string += "\n"
        self._update_text_window(file_string)

    def _set_filetype(self, filetype):
        self.converter.set_filetype(filetype)

    def _set_engine(self, engine):
        self.converter.set_engine(engine)

    def _set_toc_orientation(self, orientation):
        self.converter.set_toc_orientation(orientation)

    def _set_save_location(self):
        dialog = QFileDialog()
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_() == QFileDialog.Accepted:
            file = dialog.selectedFiles()[0]
            self.converter.set_filename(file + "/" + parameters["PDF name"])
            self.save_file_label.setText(f"Save file location \n{file}/compiled.pdf")
            self.compile_button.setText("Compile from selected files")

    def _set_toc_bool(self):
        if self.toc_button.isChecked():
            self.v_toc_orientation_button.setChecked(True)
            self.converter.set_toc_orientation("P")

    def _update_progress_bar_length(self):
        if not self.converter.converter_ready():
            return None
        self.progress_bar.setMaximum(self.converter.get_num_files() + 1)

    def _remove_progress_bar(self):
        self.progress_bar.setValue(0)
        self.layout().removeWidget(self.progress_bar)

    def _compile(self):
        if not self.converter.filename_set():
            self.compile_button.setText("Compile from selected files\n Select save location first!")
            return None
        if not self.converter.files_set():
            self._update_text_window("Select files first!")
            return None
        self._update_started_text()
        self.create_thread()
        self._update_progress_bar_length()
        self.thread.start()

        self.progress_bar.setValue(self.converter.get_num_files() + 1)

    def _update_text_window(self, msg):
        self.big_text_box.setText(msg)

    def _on_progress_update(self, value):
        self.progress_bar.setValue(value)

    def _update_finished_text(self):
        if self.toc_button.isChecked():
            compile_text = f"PDF compiled as {self.converter.filename}"
        else:
            compile_text = f"PDF compiled as {self.converter.filename} \nTable of contents page not created"
        self._update_text_window(compile_text)
        self.compile_button.setText("Compile from selected files")

    def _update_started_text(self):
        self.label_above_text_box.setText("Compiled successfully")
        self._update_text_window("Compiling PDF from rtf files. \nThis may take some time \nDo not open "
                                 "the selected engine while this program is running")


