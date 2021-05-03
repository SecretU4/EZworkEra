"""Simple file encoding & image format converter"""
if __name__ == "__main__":
    from PySide2.QtCore import QCoreApplication
    QCoreApplication.setLibraryPaths([r"E:\ProgramData\Anaconda3\envs\ezworkera\Lib\site-packages\PySide2\plugins"]) # Write your QT_PLUGIN_PATH

import sys
import os
import chardet
from PIL import Image
from PySide2.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QCheckBox,
    QLabel,
    QRadioButton,
    QProgressBar,
    QStatusBar,
    QMainWindow,
    QMessageBox,
)
from PySide2.QtGui import QIcon
from PySide2.QtCore import QCoreApplication, QThread, Signal, Slot
from simple_util import BringFiles
# import debugpy


def result_maker(filename, dir_from):
    filename = "Result" + filename.replace(dir_from, "")
    result_dir = os.path.dirname(filename)
    if not os.path.isdir(result_dir):
        dir_names = result_dir.split("\\")
        for depth in range(len(dir_names)):
            dir_make = "\\".join(dir_names[: depth + 1])
            if os.path.isdir(dir_make):
                continue
            os.mkdir(dir_make)
    return filename


encode_dict = {"Shift-JIS": "cp932", "UTF-8 with BOM": "utf-8-sig",
    "Korean-Windows": "cp949", "UTF-16 LE":"utf-16-le"}


class ImageConvert:
    """Image 포멧 변경 기능 클래스. 동적 이미지 미지원"""

    def __init__(self, file_path, opt_array=[0, 0], dir_from=None):
        self.filename, self.orig_ext = os.path.splitext(file_path)
        self.file_path = file_path
        self.opened_image = Image.open(file_path).convert("RGB")
        self.make_backup = opt_array[1]
        self.dir_from = dir_from

    def convert_image(self, dest_fmt):
        if self.make_backup and self.dir_from:
            self.filename = result_maker(self.filename, self.dir_from)
        else:
            if os.path.isfile(self.file_path):
                os.remove(self.file_path)
            else:
                print("ERROR - NOFILE to DELETE")
        self.opened_image.save(self.filename + "." + dest_fmt, dest_fmt)


class TXTConverter:
    def __init__(
        self, filename, target_encode, orig_imgext="", to_imgext="", opt_array=[0, 0], dir_from=None
    ):
        self.filename = filename
        self.opened_file = open(filename, "rb")
        self.encode_to = target_encode
        self.orig_imgext = orig_imgext
        self.to_imgext = to_imgext
        self.change_ext_inTXT = opt_array[0]
        self.get_backup = opt_array[1]
        self.dir_from = dir_from

    def encoding_check(self):
        detect_result = chardet.detect(self.opened_file.read())
        return detect_result["encoding"]

    def change_encoding(self, encode_to):
        bulk_data = None
        while bulk_data == None:
            for encode in encode_dict.values():
                bulk_data = self.try_open(encode)
                if isinstance(bulk_data, str):
                    break
            if bulk_data == None:
                encode = self.encoding_check()
                bulk_data = self.try_open(encode)
        if self.orig_imgext and self.change_ext_inTXT:
            bulk_data = bulk_data.replace(self.orig_imgext, self.to_imgext)

        if self.get_backup and self.dir_from:
            dest_filename = result_maker(self.filename, self.dir_from)
        else:
            dest_filename = self.filename
        with open(dest_filename, "w", encoding=encode_to) as dest:
            dest.write(bulk_data)

    def try_open(self, encoding):
        try:
            with open(self.filename, "r", encoding=encoding) as origin:
                bulk_data = origin.read()
            return bulk_data
        except UnicodeDecodeError:
            return None

    def run(self):
        self.change_encoding(self.encode_to)


class MainWidget(QWidget):

    format_dict = {"JPEG(jpg)": "jpeg", "WebP": "webp", "Gif": "gif", "PNG": "png"}

    def __init__(self, parent):
        super().__init__()
        self.par = parent
        self.InitUI()

    def InitUI(self):
        self.selected_dir = str()
        self.option_array = [1, 0, 0, 0]
        self.main_layout = QVBoxLayout()
        self.make_dir_groupbox()
        self.make_func_groupbox()
        self.make_sys_layout()
        self.status_bar = QStatusBar()
        self.setEnabled(True)

        self.setLayout(self.main_layout)

    def make_dir_groupbox(self):
        dir_groupbox = QGroupBox("Select Directory")
        dir_layout = QVBoxLayout()
        self.loaded_dir_label = QLabel(self.selected_dir)
        self.loaded_dir_label.setStyleSheet(
            "max-height: 24px;"
            "background-color: #FFFFFF;"
            "border-style: solid;"
            "border-width: 1px;"
            "border-color: #000000"
        )
        dir_layout.addWidget(self.loaded_dir_label)
        self.load_dir_button = QPushButton("Load Directory", self)
        self.load_dir_button.clicked.connect(self.load_dir)
        dir_layout.addWidget(self.load_dir_button)
        dir_groupbox.setLayout(dir_layout)
        self.main_layout.addWidget(dir_groupbox)

    def make_func_groupbox(self):
        func_layout = QHBoxLayout()

        self.encode_widget = RadioBox(encode_dict)
        encode_layout = self.encode_widget.make_radio_box("UTF-8 with BOM")
        self.encode_groupbox = QGroupBox("Encode to: ")
        self.encode_groupbox.setLayout(encode_layout)
        self.encode_groupbox.setCheckable(True)
        self.encode_groupbox.clicked.connect(self.option_set)
        func_layout.addWidget(self.encode_groupbox)

        self.fmt_groupbox = QGroupBox("Convert image format")
        fmt_hbox = QHBoxLayout()
        self.format_widget_from = RadioBox(self.format_dict)
        format_layout_from = self.format_widget_from.make_radio_box("WebP")
        fmt_from_groupbox = QGroupBox("Convert image from: ")
        fmt_from_groupbox.setLayout(format_layout_from)
        fmt_hbox.addWidget(fmt_from_groupbox)

        self.format_widget_to = RadioBox(self.format_dict)
        format_layout_to = self.format_widget_to.make_radio_box("PNG")
        fmt_to_groupbox = QGroupBox("Convert image to: ")
        fmt_to_groupbox.setLayout(format_layout_to)
        fmt_hbox.addWidget(fmt_to_groupbox)
        self.fmt_groupbox.setLayout(fmt_hbox)
        self.fmt_groupbox.setCheckable(True)
        func_layout.addWidget(self.fmt_groupbox)

        option_groupbox = QGroupBox("OPTION: ")
        option_layout = QVBoxLayout()
        self.change_txt_yn = QCheckBox("Change image ext in CSV/ERB", self)
        self.change_txt_yn.toggle()
        self.change_txt_yn.clicked.connect(self.option_set)
        self.backup_yn = QCheckBox("Place files in Result directory", self)
        self.backup_yn.clicked.connect(self.option_set)

        option_layout.addWidget(self.change_txt_yn)
        option_layout.addWidget(self.backup_yn)
        option_groupbox.setLayout(option_layout)
        func_layout.addWidget(option_groupbox)

        self.main_layout.addLayout(func_layout)

    def make_sys_layout(self):
        sys_layout = QHBoxLayout()
        self.run_button = QPushButton("RUN", self)
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self.run_process)
        self.prog_bar = QProgressBar()
        self.prog_bar.setMinimum(0)
        sys_layout.addWidget(self.prog_bar)
        sys_layout.stretch(1)
        sys_layout.addWidget(self.run_button)
        self.main_layout.addLayout(sys_layout)

    def load_dir(self):
        f_dialog = QFileDialog(self, "불러올 폴더를 선택하세요.", os.path.curdir)
        f_dialog.setFileMode(QFileDialog.DirectoryOnly)
        self.selected_dir = f_dialog.getExistingDirectory(self, "불러올 폴더를 선택하세요.")
        if not self.selected_dir:
            self.selected_dir = str()
            self.run_button.setEnabled(False)
        else:
            self.run_button.setEnabled(True)
        self.loaded_dir_label.setText(self.selected_dir)
        return self.selected_dir

    def option_set(self):
        if not self.encode_groupbox.isChecked():
            self.change_txt_yn.setEnabled(False)
        else:
            self.change_txt_yn.setEnabled(True)
        self.option_array[0] = self.change_txt_yn.checkState()
        self.option_array[1] = self.backup_yn.checkState()
        self.option_array[2] = self.encode_groupbox.isChecked()
        self.option_array[3] = self.fmt_groupbox.isChecked()
        return self.option_array

    def run_process(self):
        self.option_set()
        self.setEnabled(False)
        target_array = (
            self.encode_widget.result,
            self.format_widget_from.result,
            self.format_widget_to.result,
            self.selected_dir,
        )
        bar_array = (self.prog_bar, self.status_bar)
        self.threadclass = MyThread(target_array, bar_array, self.option_array, self)
        self.work_started = 0
        self.threadclass.processed.connect(self.progbar_set)
        self.threadclass.finished.connect(self.donebox)
        self.threadclass.start()

    def open_result(self):
        if self.option_array[1]:
            result_path = "Result\\"
        else:
            result_path = self.selected_dir
        os.startfile(result_path)

    @Slot(int)
    def progbar_set(self, progress_stat):
        if not self.work_started:
            self.prog_bar.setMaximum(progress_stat)
            self.work_started += 1
        else:
            self.prog_bar.setValue(progress_stat)

    @Slot(bool)
    def donebox(self):
        msgbox = QMessageBox(
            QMessageBox.Warning,
            "Done!",
            "Do you want to quit?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            parent=self,
        )
        open_result = msgbox.addButton("Open Result Folder", QMessageBox.AcceptRole)
        msgbox.setDefaultButton(QMessageBox.Yes)
        close_yn = msgbox.exec_()
        if close_yn == QMessageBox.No:
            self.threadclass.wait()
            # debugpy.debug_this_thread()
            self.close()
            self.par.intiGUI()
        else:
            if close_yn == QMessageBox.AcceptRole:
                self.open_result()
            QCoreApplication.instance().quit()


class RadioBox(QWidget):
    def __init__(self, target_dict):
        super().__init__()
        self.target_dict = target_dict
        self.result = None

    def make_radio_box(self, chk_default):
        radio_layout = QVBoxLayout()

        for key in self.target_dict:
            button_key = QRadioButton(key, self)
            button_key.clicked.connect(self.radiobox_check)
            if key == chk_default:
                button_key.setChecked(True)
                self.result = self.target_dict[key]
            auto_atr = "radio_" + key
            setattr(self, auto_atr, button_key)
            radio_layout.addWidget(button_key)

        return radio_layout

    def radiobox_check(self):
        for key in self.target_dict:
            auto_atr = "radio_" + key
            button_obj = getattr(self, auto_atr, None)
            if not button_obj:
                continue
            elif button_obj.isChecked():
                self.result = self.target_dict[key]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.intiGUI()

    def intiGUI(self):
        main_widg = MainWidget(self)
        self.setCentralWidget(main_widg)
        self.setStatusBar(main_widg.status_bar)
        main_widg.status_bar.showMessage("READY")

        self.setWindowTitle("Encoding & Image Format Converter")
        self.setWindowIcon(QIcon(r"Core\ezwork_RNl_icon.ico"))
        self.resize(720, 480)


class MyThread(QThread):
    processed = Signal(int)
    finished = Signal(bool)

    def __init__(self, target_array, bar_array, option_array, parent=None):
        super().__init__(parent)
        self.target_array = target_array
        self.prog_bar, self.status_bar = bar_array
        self.option_array = option_array[:2]
        self.func_array = option_array[2:]

    def __del__(self):
        print("Thread Deleted")

    def run(self):
        # debugpy.debug_this_thread()
        target_encode, target_fmt_from, target_fmt_to, selected_dir = self.target_array
        print("Args loaded")
        imgfiles = BringFiles(selected_dir).search_filelist(target_fmt_from)
        txtfiles = BringFiles(selected_dir).search_filelist(".ERB", ".ERH", ".CSV")
        imgfiles_len = len(imgfiles)
        txtfiles_len = len(txtfiles)
        print("Filees listed")
        if self.func_array[0] and self.func_array[1]:
            total_len = imgfiles_len + txtfiles_len
        elif self.func_array[0]:
            total_len = txtfiles_len
        elif self.func_array[1]:
            total_len = imgfiles_len
        else:
            print("Selected_nothing")
            total_len = 0
        self.processed.emit(total_len)

        progress_stat = 0
        if self.func_array[1]:
            print("Converting img fmt")
            for imgfile in imgfiles:
                progress_stat += 1
                self.status_bar.showMessage("processing %s" % imgfile)
                imgconv = ImageConvert(imgfile, self.option_array, selected_dir)
                imgconv.convert_image(target_fmt_to)
                self.processed.emit(progress_stat)

        if self.func_array[0]:
            print("Converting txt encoding")
            for txtfile in txtfiles:
                progress_stat += 1
                self.status_bar.showMessage("processing %s" % txtfile)
                txtconv = TXTConverter(
                    txtfile,
                    target_encode,
                    target_fmt_from,
                    target_fmt_to,
                    self.option_array,
                    selected_dir,
                )
                txtconv.run()
                self.processed.emit(progress_stat)
        print("Thread Done")
        self.finished.emit(True)


if __name__ == "__main__":
    running_app = QApplication(sys.argv)
    gui_window = MainWindow()
    gui_window.show()
    sys.exit(running_app.exec_())
