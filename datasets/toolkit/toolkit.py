import sys

import pandas
from PySide6.QtGui import QTextFormat, QPixmap
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget, QPushButton,
                               QGridLayout, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QFileDialog, QGroupBox, QTabWidget, QComboBox, QSpinBox,
                               QCheckBox, QTextEdit, QStatusBar)
# from PIL import Image, ImageQt
import pandas as pd

from os.path import isdir, isfile, exists
from os import listdir
from pathlib import Path


import video_conv

# exts = Image.registered_extensions()
# supported_read_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}
# if ".jpg" not in supported_read_extensions and ".jpeg" in supported_read_extensions:
#     supported_read_extensions.add(".jpg")
# supported_read_extensions = sorted(supported_read_extensions)
#
# supported_write_extensions = sorted({ex for ex, f in exts.items() if f in Image.SAVE})
#
# NO_EXTENSION_FILTER = "All files (*)"
#
# read_modes = [NO_EXTENSION_FILTER]
#
# for extension in supported_read_extensions:
#     read_modes.append(f"{extension[1:].upper()} image (*{extension})")
#
# read_modes_string = ";;".join(read_modes)

# print(' '.join(supported_read_extensions))  # Adds semicolons in file manager
# image_read_format_string = "Image Files ("
# for extension in supported_read_extensions:
#     image_read_format_string += f"*{extension}, "
# image_read_format_string = image_read_format_string[:-2]
# image_read_format_string += ")"
#
# image_write_format_string = "Image Files ("
# for extension in supported_write_extensions:
#     image_write_format_string += f"*{extension}, "
# image_write_format_string = image_write_format_string[:-2]
# image_write_format_string += ")"


class WamaiToolkitMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool()
        self.setWindowTitle("WA.M.AI Toolkit")

        self.screen_res_x, self.screen_res_y = self.screen().size().toTuple()
        self.resize(self.screen_res_x//4 * 3, self.screen_res_y//4 * 3)

        # Will contain file paths and names - each item will be a tuple of absolute path and file name
        self.unlabelled_file_list = []
        self.status_bar = QStatusBar()

        self.label_dataframe = pd.DataFrame()
        self.label_file_path = Path("null.csv")

        self.setCentralWidget(self.genMainWidget())
        self.setStatusBar(self.status_bar)

        self.status_bar.showMessage("Application started.", 5000)
    def genMainWidget(self):
        heading = QLabel("<h1>WA.M.AI Toolkit</h1>")
        heading.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        # heading.setText()

        heading_layout = QVBoxLayout()
        heading_layout.addWidget(heading)
        heading_layout.addWidget(self.genOptionsTabs(), 2)
        # heading_layout.addWidget(QLabel("Dummy label"))
        openFileButton = QPushButton("Open image folder...")
        openFileButton.clicked.connect(self.printChosenReadFile)
        # heading_layout.addWidget(openFileButton)
        self.resize_data_enabled.clicked.connect(self.set_resize_layout_state)

        mainWidget = QWidget()
        mainWidget.setLayout(heading_layout)

        return mainWidget

    def getDirectory(self):
        return QFileDialog.getExistingDirectory(self, "Open Folder", "")

    def printChosenReadFile(self):
        print(self.getDirectory())

    def genOptionsWidget(self):
        ...
        # options_group = QGroupBox("Options")
        # tabs_layout = QVBoxLayout()
        # tabs_layout.addWidget(self.genOptionsTabs())
        # options_group.setLayout(tabs_layout)
        # options_group.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        # return options_group

    def genOptionsTabs(self):
        options_tabs = QTabWidget()
        options_tabs.addTab(self.genVideoConvOptionsWidget(), "Convert video")
        options_tabs.addTab(self.genViewWidget(), "View")
        # options_tabs.addTab(self.genVideoConvWidget(), "Convert video")

        return options_tabs

    def genVideoConvOptionsWidget(self):
        output_options_layout = QFormLayout()

        self.video_paths = QTextEdit()
        self.video_paths_select = QPushButton("Select video...")
        self.video_paths_select.clicked.connect(self.get_videos)
        video_paths_layout = QHBoxLayout()
        video_paths_layout.addWidget(self.video_paths)
        video_paths_layout.addWidget(self.video_paths_select)

        output_options_layout.addRow(QLabel("Video path: "), video_paths_layout)

        self.output_folder_path = QTextEdit()
        self.output_path_select = QPushButton("Select folder...")
        self.output_path_select.clicked.connect(lambda: self.output_folder_path.setText(self.getDirectory()))
        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(self.output_folder_path)
        output_path_layout.addWidget(self.output_path_select)

        output_options_layout.addRow("Output path: ", output_path_layout)

        self.output_file_name = QTextEdit()
        self.output_file_name.setToolTip("The file name to use for output images. "
                                         "The file name will be the specified name, "
                                         "then a 10 digit number representing the frame number padded with zeroes. "
                                         "\n(e.g. video_frame-0000000123 "
                                         "would be frame 123 using name 'video_frame')"
                                         "\nIf no name was specified beforehand, this "
                                         "field will be filled with the name of the video file selected.")
        output_options_layout.addRow("Image base name: ", self.output_file_name)

        self.compress_frames = QCheckBox()
        self.compress_frames.setToolTip("Tells `pillow` to compress the images (losslessly) "
                                        "as efficiently as possible. Saves a minor amount of disk space (~3%), "
                                        "at the cost of considerably increased time to output frames. "
                                        "\n\nRecommended to only be considered if the output is to be "
                                        "held fo a very long period of time, or storage constraints are strict.")
        output_options_layout.addRow("Optimise images?: ", self.compress_frames)

        self.resize_data_enabled = QCheckBox()
        # TODO: Implement resizing
        # self.resize_data_enabled.setDisabled(True)
        self.resize_data_enabled.setToolTip("Resizes output images to the designated size")
        output_options_layout.addRow(QLabel("Resize?"), self.resize_data_enabled)

        # TODO: Get dimensions from loaded dataset and set values accordingly
        self.resize_options = self.genResizeOptionsWidget(100, 100)
        output_options_layout.addWidget(self.resize_options)

        options_with_confirm_layout = QVBoxLayout()
        options_with_confirm_layout.addLayout(output_options_layout)
        convert_confirm = QPushButton("Convert video to image frames")
        # convert_confirm.clicked.connect(lambda: video_conv_testing.video_to_frames(self.video_paths.toPlainText(),
        #                                                                            self.output_folder_path.toPlainText(),
        #                                                                            self.output_file_name.toPlainText()))

        convert_confirm.clicked.connect(lambda: self.startConversionWorker(video_path=self.video_paths.toPlainText(),
                                                                           output_path=self.output_folder_path.toPlainText(),
                                                                           frame_name=self.output_file_name.toPlainText(),
                                                                           compress_frames=self.compress_frames.isChecked(),
                                                                           resize=self.resize_data_enabled.isChecked(),
                                                                           resize_options={
                                                                               "width": self.resize_width_option.value(),
                                                                               "height": self.resize_height_option.value(),
                                                                               "keep_aspect": self.keep_aspect_option.isChecked(),
                                                                               "aspect_locked_dimension": self.keep_aspect_by.currentText()
                                                                           }))
        options_with_confirm_layout.addWidget(convert_confirm)

        output_options_widget = QWidget()
        output_options_widget.setLayout(options_with_confirm_layout)

        # Call state selection function so that if we choose to default `resize_data_enabled` to be checked,
        # the layout will be enabled to match
        self.set_resize_layout_state()

        return output_options_widget

    def genResizeOptionsWidget(self, img_width, img_height):
        resize_options_widget = QGroupBox("Resizing")
        resize_options_layout = QFormLayout()

        # Use `self.` to make values available for collection later
        # Disable height option if checked
        self.keep_aspect_option = QCheckBox()
        self.keep_aspect_option.setToolTip("Attempts to keep aspect ratio as close as possible "
                                           "to that of the original image.")
        self.keep_aspect_by = QComboBox()
        self.keep_aspect_by.setToolTip("Sets the dimension to manually set. The other will be calculated "
                                       "to keep aspect ratio as close as possible to the original image.")
        self.keep_aspect_by.addItems(["Width", "Height"])
        self.keep_aspect_option.clicked.connect(self.set_aspect_by_state)
        self.set_aspect_by_state()

        self.resize_width_option = QSpinBox()
        self.resize_width_option.setMinimum(1)
        self.resize_width_option.setMaximum(10000)
        self.resize_width_option.setValue(img_width)
        self.resize_height_option = QSpinBox()
        self.resize_height_option.setMinimum(1)
        self.resize_height_option.setMaximum(10000)
        self.resize_height_option.setValue(img_height)

        resize_options_layout.addRow("Keep aspect ratio?: ", self.keep_aspect_option)
        resize_options_layout.addRow("Keep aspect ratio - resize by: ", self.keep_aspect_by)
        resize_options_layout.addRow("Resize width to: ", self.resize_width_option)
        resize_options_layout.addRow("Resize height to: ", self.resize_height_option)

        resize_options_widget.setLayout(resize_options_layout)

        return resize_options_widget

    def genFrameLabelWidget(self):
        label_groupbox = QGroupBox("Frame to label")
        self.data_image = QLabel()
        data_pixmap = QPixmap("okinimesumama-expert-24-played-incomplete-0000001350.png")
        # data_pixmap = data_pixmap.scaledToWidth(self.height() // 2)
        # image = image.scaledToWidth(500)
        self.data_image.setPixmap(data_pixmap)
        # self.data_image.setScaledContents(True)

        labelling_layout = QGridLayout()
        labelling_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        labelling_layout.addWidget(self.data_image, 0, 1, 4, 4)
        # labelling_layout.setColumnStretch(1, 2)
        self.label_checkboxes = []
        for i in range(8):
            self.label_checkboxes.append(QCheckBox(f"b{i + 1}"))
            # Appends the checkboxes to the list in the same order as the buttons
            labelling_layout.addWidget(self.label_checkboxes[-1], i % 4 if i < 4 else 3 - (i % 4), 5 if i <= 3 else 0,
                                       Qt.AlignmentFlag.AlignVCenter)

        label_groupbox.setLayout(labelling_layout)

        return label_groupbox

    def genViewWidget(self):
        view_data_widget = QGroupBox("Label data")
        view_data_layout = QVBoxLayout()

        view_data_layout.addWidget(self.genFrameLabelWidget())

        label_options_widget = QGroupBox("Labelling options")

        label_options_layout = QFormLayout()

        self.label_type = QComboBox()
        self.label_type.addItems(["Notes in zone/Note ready to press"])
        self.label_type.setToolTip("The labelling system to use for outputting/organising the dataset. "
                                   "<b>Do not change this after beginning to label a dataset</b>"
                                   "<br>(More will be added as necessary)"
                                   "<br><br>Notes in zone/Note ready to press: A system that will organise the dataset "
                                   "based on the availability of notes in each zone. "
                                   "Slides are not taken into account under this system.")
        label_options_layout.addRow("Labelling system: ", self.label_type)

        self.frame_select = QSpinBox()
        self.frame_select.setMinimum(0)
        self.frame_select.valueChanged.connect(self.load_unlabelled_frame)
        label_options_layout.addRow("Frame to label: ", self.frame_select)

        unlabelled_data_folder_layout = QHBoxLayout()
        self.unlabelled_data_folder = QTextEdit()
        self.unlabelled_data_folder_select = QPushButton("Select folder...")
        unlabelled_data_folder_layout.addWidget(self.unlabelled_data_folder)
        unlabelled_data_folder_layout.addWidget(self.unlabelled_data_folder_select)
        label_options_layout.addRow("Unlabelled data source: ", unlabelled_data_folder_layout)
        self.unlabelled_data_folder_select.clicked.connect(self.load_unlabelled_data)

        labelled_data_folder_layout = QHBoxLayout()
        self.labelled_data_file = QTextEdit()
        self.labelled_data_file_select = QPushButton("Select path...")
        labelled_data_folder_layout.addWidget(self.labelled_data_file)
        labelled_data_folder_layout.addWidget(self.labelled_data_file_select)
        label_options_layout.addRow("Labelled data output path: ", labelled_data_folder_layout)
        self.labelled_data_file_select.clicked.connect(self.select_dataset_labels_file)

        self.labelled_data_submit = QPushButton("Add labelled frame to output folder")
        self.labelled_data_submit.clicked.connect(self.add_labelled_frame)
        labelling_layout = QVBoxLayout()
        labelling_layout.addLayout(label_options_layout)
        labelling_layout.addWidget(self.labelled_data_submit)

        label_options_widget.setLayout(labelling_layout)

        view_data_layout.addWidget(label_options_widget)

        view_data_widget.setLayout(view_data_layout)

        return view_data_widget

    def select_dataset_labels_file(self):
        self.labelled_data_file.setText(QFileDialog.getSaveFileName(filter="Dataset label file (*.csv)")[0])
        self.create_note_presence_label_file_stub(self.labelled_data_file.toPlainText())
        for checkbox in self.label_checkboxes:
            checkbox.setChecked(False)


    def create_note_presence_label_file_stub(self, path):
        # TODO: After okinimesumama is labelled, change system to generate all rows immediately, then use `iloc`
        #  to change the correct row for a frame - allows for error correction without an external program
        path = Path(path)
        columns = ["file_name", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"]
        if not exists(path):
            with open(path, "w") as label_file:
                pd.DataFrame(columns=["file_name",
                                      "b1", "b2", "b3", "b4",
                                      "b5", "b6", "b7", "b8"]).to_csv(label_file, index=False)
        else:
            self.status_bar.showMessage("Reading existing label file...", timeout=3000)
            try:
                with open(path, "r") as label_file:
                    df = pd.read_csv(label_file)
                if list(df.columns) != columns:
                    self.status_bar.showMessage("Specified file is not a valid label file.", 5000)
                    self.labelled_data_file.setText("")
                else:
                    rows = len(df.index)
                    if rows <= self.frame_select.maximum():
                        self.frame_select.setValue(rows)
                        self.label_dataframe = df
            except Exception as e:
                self.status_bar.showMessage("Failed to open file as a DataFrame.", 5000)
                self.labelled_data_file.setText("")
                return
        self.label_file_path = path
    def load_unlabelled_data(self):
        self.unlabelled_data_folder.setText(self.getDirectory())
        self.frame_select.setValue(0)
        self.unlabelled_file_list = listdir(self.unlabelled_data_folder.toPlainText())
        pruned_file_list = []
        for count, name in enumerate(self.unlabelled_file_list):
            # Assuming all frames are pngs - fine for toolkit as it will never output another format
            if name.lower().endswith(".png"):
                pruned_file_list.append((str(Path(self.unlabelled_data_folder.toPlainText()) / name), name))

        self.unlabelled_file_list = pruned_file_list

        self.frame_select.setMaximum(len(self.unlabelled_file_list) - 1)
        self.load_unlabelled_frame()

    def load_unlabelled_frame(self):
        if self.unlabelled_file_list:
            data_pixmap = QPixmap(self.unlabelled_file_list[self.frame_select.value()][0])
            self.data_image.setPixmap(data_pixmap)
        else:
            self.status_bar.showMessage("Please select a source folder before attempting to select a frame.", 5000)

    def add_labelled_frame(self):
        # TODO: Output labelled data (copy file - label folders should be as 8 set of 1 or 0)
        if self.frame_select.value() == self.frame_select.maximum():
            self.status_bar.showMessage("Final frame for this dataset has been labelled.", timeout=15000)
        else:
            self.add_note_presence_labels(self.label_file_path)
            self.frame_select.setValue(self.frame_select.value() + 1)

        # Add label data to CSV - create if not made and add columns, add row, check if full?, load frame after last in csv?

    def add_note_presence_labels(self, path):
        data = [self.unlabelled_file_list[self.frame_select.value()][1]]

        for checkbox in self.label_checkboxes:
            data.append(checkbox.isChecked())
        self.label_dataframe.loc[len(self.label_dataframe.index)] = data
        with open(path, "w") as label_file:
            self.label_dataframe.to_csv(label_file, index=False)


    def genVideoConvWidget(self):
        video_conv_form = QFormLayout()

        self.video_paths = QTextEdit()
        self.video_paths_select = QPushButton("Select video...")
        self.video_paths_select.clicked.connect(self.get_videos)

        video_paths_layout = QHBoxLayout()
        video_paths_layout.addWidget(self.video_paths)
        video_paths_layout.addWidget(self.video_paths_select)

        video_conv_form.addRow(video_paths_layout)

        video_conv_widget = QWidget()
        video_conv_widget.setLayout(video_conv_form)

        return video_conv_widget


    def get_videos(self):
        path, file_filter = QFileDialog.getOpenFileName(self, "Open Folder", "")
        self.video_paths.setText(path)
        file_name = path.split("/")[-1]
        # Change output_name to the video file name if no name is given
        if not self.output_file_name.toPlainText():
            self.output_file_name.setText(file_name.split(".")[0])

    def set_resize_layout_state(self):
        self.resize_options.setEnabled(self.resize_data_enabled.isChecked())

    def set_aspect_by_state(self):
        self.keep_aspect_by.setEnabled(self.keep_aspect_option.isChecked())

    def startConversionWorker(self, video_path, output_path, frame_name, compress_frames, resize, resize_options):

        if self.valid_form_input():
            video_conversion_worker = video_conv.VideoConversionWorker(video_path=video_path,
                                                                       output_path=output_path,
                                                                       frame_name=frame_name,
                                                                       compress_frames=compress_frames,
                                                                       resize=resize, resize_options=resize_options)
            video_conversion_worker.signals.progress.connect(self.displayVideoProcessingProgress)
            video_conversion_worker.signals.finished.connect(
                lambda: self.status_bar.showMessage(f"[{frame_name}] Processing video complete!", timeout=15000))
            self.thread_pool.start(video_conversion_worker)

    def displayVideoProcessingProgress(self, progress_data):
        self.status_bar.showMessage(f"[{progress_data['frame_name']}] Processing video... "
                                    f"(Last frame output: {progress_data['frame_num']})")

    def valid_form_input(self) -> bool:
        if (self.output_file_name.toPlainText()
                and (folder_path := self.output_folder_path.toPlainText())
                and (input_file := self.video_paths.toPlainText())):
            out_folder_exists = isdir(folder_path)
            input_file_exists = isfile(input_file)
            # Returning `out_folder_exists and input_file_exists` would be valid,
            # but would not send the message to the window
            if out_folder_exists and input_file_exists:
                return True
        self.status_bar.showMessage("Invalid form input. Please check and correct your selections.", timeout=5000)
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont("Bahnschrift")
    window = WamaiToolkitMainWindow()
    window.show()
    sys.exit(app.exec())