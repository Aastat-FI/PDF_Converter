from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QFileDialog, QRadioButton, \
    QButtonGroup, QTextBrowser, QCheckBox, QProgressBar, QTextEdit, QHBoxLayout, QLineEdit, QDoubleSpinBox, QSpinBox
from PyQt5.QtGui import QCloseEvent
from main_functions import Converter
from settings import get_parameters
import json


# noinspection PyArgumentList
class MainWindow(QWidget):
    """
    Class for GUI functionality of the program.
    """

    def __init__(self):
        super().__init__()
        self.main_layout = QHBoxLayout(self)
        self.converter = Converter()
        self.parameters = None
        self.setWindowTitle("PDF compiler")
        self.settings_window = None

        self.create_base_ui()
        self.update_parameters()

    def create_thread(self):
        """
        Creates a thread for converter so the application doesn't freeze while converting
        :return:
        """
        try:
            self.thread.isFinished()
        except:
            self.thread = QThread()
            self.thread.finished.connect(self._update_finished_text)
            self.converter.moveToThread(self.thread)
            self.thread.started.connect(self.converter.convert)
            self.converter.finished.connect(self.thread.quit)
            # self.converter.finished.connect(self.converter.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.converter.progress.connect(self._on_progress_update)
            self.converter.send_toc.connect(self.create_toc_show_window)

    def update_parameters(self):
        self.parameters = get_parameters()

    def create_toc_show_window(self, toc_dict):
        """
        Creates the window where user can change and accept the proposed table of contents
        :param toc_dict:
        :return:
        """
        self._update_text_window("Please accept the proposed table of contents")
        self.toc_text_window = QTextEdit()
        self.toc_text_window.resize(400, 200)
        self.accept_toc_button = QPushButton("Accept Table of Contents")
        self.accept_toc_button.clicked.connect(self.accept_toc)
        self.tmp_layout = QVBoxLayout()
        self.tmp_layout.addWidget(self.toc_text_window)
        self.tmp_layout.addWidget(self.accept_toc_button)
        self.main_layout.addLayout(self.tmp_layout)
        text = ""
        for key, value in toc_dict.items():
            key = key.replace("\n", "").replace("\r", "").strip()
            text += f'{key}: {value}\n'
        self.toc_text_window.setText(text)

    def accept_toc(self):
        """
        Gets the text from the table of contents window, converts it into a dictionary and returns to the converter
        class
        :return:
        """
        text = self.toc_text_window.toPlainText()
        df = {}
        for line in text.splitlines():
            line = line.split(":")
            value, data = line[0], line[1]
            value, data = value.strip(), int(data)
            df[value] = data
        self.converter.set_toc_dict(df)
        self.converter.accept_toc()
        self.layout().removeWidget(self.toc_text_window)
        self.toc_text_window.deleteLater()
        self.toc_text_window = None
        self.layout().removeWidget(self.accept_toc_button)
        self.accept_toc_button.deleteLater()
        self.accept_toc_button = None
        self._update_text_window("Creating the PDF. Just a second")

    def create_base_ui(self):
        """
        Creates the base window
        :return:
        """
        self.base_layout = QVBoxLayout(self)
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

        self.toc_button = QCheckBox("Generate table of contents")
        self.toc_button.clicked.connect(self.v_toc_orientation_button.setChecked)
        self.compile_button = QPushButton("Compile from selected files", clicked=lambda: self._compile())

        self.save_location_button = QPushButton("Select file save location", clicked=lambda: self._set_save_location())
        self.save_file_label = QLabel("Save location not yet selected")
        self.open_settings_button = QPushButton("Open settings", clicked=lambda: self._open_settings_window())

        self.base_layout.addWidget(self.select_file_label)
        self.base_layout.addWidget(self.open_settings_button)
        self.base_layout.addWidget(self.rtf_button)
        self.base_layout.addWidget(self.txt_button)
        self.base_layout.addWidget(self.my_button)
        self.base_layout.addWidget(self.engine_label)
        self.base_layout.addWidget(self.word_button)
        self.base_layout.addWidget(self.open_office_button)
        self.base_layout.addWidget(self.toc_button)
        self.base_layout.addWidget(self.toc_button)
        self.base_layout.addWidget(self.v_toc_orientation_button)
        self.base_layout.addWidget(self.h_toc_orientation_button)
        self.base_layout.addWidget(self.save_location_button)
        self.base_layout.addWidget(self.save_file_label)
        self.base_layout.addWidget(self.compile_button)
        self.base_layout.addWidget(self.label_above_text_box)
        self.base_layout.addWidget(self.big_text_box)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.base_layout.addWidget(self.progress_bar)
        self.main_layout.addLayout(self.base_layout)
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
            self.converter.set_filename(file + "/" + self.parameters["PDF name"])
            self.save_file_label.setText(f"Save file location \n{file}/{self.parameters['PDF name']}.pdf")
            self.compile_button.setText("Compile from selected files")

    def _update_progress_bar_length(self):
        if not self.converter.converter_ready():
            return None
        self.progress_bar.setMaximum(self.converter.get_num_files() + 1)

    def _remove_progress_bar(self):
        self.progress_bar.setValue(0)
        self.layout().removeWidget(self.progress_bar)

    def _compile(self):
        """
        This function calls the converter to start the file conversion
        :return:
        """
        self.converter.set_create_toc(self.toc_button.isChecked())
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
        self.compile_button.setText("RESTART PROGRAM BEFORE COMPILING OTHER DOCUMENTS")

    def _update_started_text(self):
        self.label_above_text_box.setText("Compiling..."
                                          "")
        self._update_text_window("Compiling PDF from rtf files. \nThis may take some time \nDo not open "
                                 "the selected engine while this program is running")

    def _open_settings_window(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.update_parameters()
        self.create_layout()

    def update_parameters(self):
        self.parameters = get_parameters()

    def create_layout(self):
        self.label_layout = QVBoxLayout()
        self.key_layout = QVBoxLayout()

        for key, value in self.parameters.items():
            label = QLabel(key)
            setting_box = None
            if key == "First word in footer" or key == "Last word in header":
                setting_box = QLineEdit()
                setting_box.setText(str(value))
            elif key == "Two linebreaks":
                setting_box = QCheckBox()
                if value:
                    setting_box.setChecked(True)
            elif key == "TOC level" or key == "Max header lines" or key == "TOC font size":
                setting_box = QSpinBox()
                setting_box.setValue(value)
            elif isinstance(value, int) or isinstance(value, float):
                setting_box = QDoubleSpinBox()
                setting_box.setDecimals(2)
                setting_box.setMaximum(150)
                setting_box.setMinimum(-150)
                setting_box.setSingleStep(0.1)
                setting_box.setValue(value)
            elif isinstance(value, str) and value != "True" and value != "False":
                setting_box = QLineEdit()
                setting_box.setText(value)

            setting_box.setObjectName(key)
            self.label_layout.addWidget(label)
            self.key_layout.addWidget(setting_box)

        combined_layout = QHBoxLayout()
        combined_layout.addLayout(self.label_layout)
        combined_layout.addLayout(self.key_layout)
        self.setLayout(combined_layout)

    def save_settings(self):
        len_settings = self.key_layout.count()
        new_settings = {}
        for i in range(len_settings):
            value = None
            widget = self.key_layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox):
                value = widget.isChecked()
            elif isinstance(widget, QLineEdit):
                value = widget.text()
            elif isinstance(widget, QDoubleSpinBox) or isinstance(widget, QSpinBox):
                value = widget.value()
            new_settings[widget.objectName()] = value
        with open('settings.json', 'w') as fp:
            json.dump(new_settings, fp, sort_keys=True, indent=4)

        pass

    def closeEvent(self, a0: QCloseEvent):
        self.save_settings()
        pass
