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

import label_tools
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

        # Will contain file paths and names - each item will be a tuple of absolute label_path and file name
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
        options_tabs.addTab(self.genDuplicateRemovalWidget(), "Remove duplicate frames from dataset")
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

        output_options_layout.addRow(QLabel("Video label_path: "), video_paths_layout)

        self.output_folder_path = QTextEdit()
        self.output_path_select = QPushButton("Select folder...")
        self.output_path_select.clicked.connect(lambda: self.output_folder_path.setText(self.getDirectory()))
        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(self.output_folder_path)
        output_path_layout.addWidget(self.output_path_select)

        output_options_layout.addRow("Output label_path: ", output_path_layout)

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

        self.remove_duplicate_frames = QCheckBox()
        self.remove_duplicate_frames.setChecked(True)
        self.remove_duplicate_frames.setToolTip("Checks adjacent frames after extraction, and removes any that are "
                                                "identical. Frame numbers are *not* changed after removal."
                                                "\n\nGenerally recommended to avoid any bias in the trained AI from "
                                                "identical samples being fed to it multiple times.")
        output_options_layout.addRow("Remove duplicate frames?: ", self.remove_duplicate_frames)

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
                                                                           },
                                                                           remove_duplicate_frames=self.remove_duplicate_frames.isChecked()))
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

    def genDuplicateRemovalWidget(self):
        # TODO: Complete UI and add functionality to remove duplicate frame images and labels from existing datasets
        duplicate_removal_form = QFormLayout()

        self.duplicate_removal_dataset_path = QTextEdit()
        self.duplicate_removal_dataset_path_select = QPushButton("Select folder...")
        self.duplicate_removal_dataset_path_select.clicked.connect(lambda: self.duplicate_removal_dataset_path.setText(self.getDirectory()))
        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(self.duplicate_removal_dataset_path)
        output_path_layout.addWidget(self.duplicate_removal_dataset_path_select)
        duplicate_removal_form.addRow("Dataset folder: ", output_path_layout)

        self.remove_duplicate_labels = QCheckBox()
        self.remove_duplicate_labels.setChecked(True)
        self.remove_duplicate_labels.setToolTip("Checks for any rows pertaining to labels that are found to be "
                                                "duplicates within the dataset, and removes them from the label file."
                                                "\nNote that the file will be replaced with a new file "
                                                "without the duplicate sample labels.")
        duplicate_removal_form.addRow("Remove labels from dataset file?: ", self.remove_duplicate_labels)

        self.duplicate_removal_label_path = QTextEdit()
        self.duplicate_removal_label_path.setEnabled(self.remove_duplicate_labels.isChecked())
        self.duplicate_removal_label_path_select = QPushButton("Select file...")
        self.duplicate_removal_label_path_select.clicked.connect(lambda: self.duplicate_removal_label_path.setText(QFileDialog.getOpenFileName(self, "Open File", "", "Label file (*.csv)")[0]))
        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(self.duplicate_removal_label_path)
        output_path_layout.addWidget(self.duplicate_removal_label_path_select)
        duplicate_removal_form.addRow("Label file: ", output_path_layout)



        self.remove_duplicate_labels.clicked.connect(lambda: self.duplicate_removal_label_path.setEnabled(self.remove_duplicate_labels.isChecked()))

        duplicate_removal_widget = QWidget()
        duplicate_removal_layout = QVBoxLayout()

        duplicate_removal_layout.addLayout(duplicate_removal_form)

        self.begin_duplicate_removal_button = QPushButton("Remove duplicate samples")
        self.begin_duplicate_removal_button.clicked.connect(
            lambda: self.start_duplicate_removal_worker(
                self.duplicate_removal_dataset_path.toPlainText(),
                (label_path := self.duplicate_removal_label_path.toPlainText()),
                # Ensure the label_path is filled
                self.remove_duplicate_labels.isChecked() and label_path
            )
        )

        duplicate_removal_layout.addWidget(self.begin_duplicate_removal_button)

        duplicate_removal_widget.setLayout(duplicate_removal_layout)
        return duplicate_removal_widget

    def start_duplicate_removal_worker(self, dataset_path, label_path, remove_dataframe_labels):
        if self.valid_frame_removal_form_input():
            duplicate_removal_worker = video_conv.VideoDuplicateRemovalWorker(dataset_path, label_path,
                                                                              remove_dataframe_labels)
            duplicate_removal_worker.signals.frame_removal.connect(self.displayFrameRemovalStart)
            duplicate_removal_worker.signals.label_removal.connect(self.displayLabelRemovalStart)
            duplicate_removal_worker.signals.finished.connect(self.displayFrameRemovalCompletion)
            self.thread_pool.start(duplicate_removal_worker)

    def displayFrameRemovalStart(self, job_name):
        self.status_bar.showMessage(f"[{job_name}] Beginning frame removal (This may take some time)...")

    def displayLabelRemovalStart(self, job_name):
        self.status_bar.showMessage(f"[{job_name}] Beginning label removal...")

    def displayFrameRemovalCompletion(self, completion_data):
        self.status_bar.showMessage(f"[{completion_data['job_name']}] Duplicate removal complete! "
                                    f"Removed duplicates: {completion_data['frames_removed']}", timeout=15000)

    def valid_frame_removal_form_input(self) -> bool:
        # If a folder is selected
        if ((folder_path := self.duplicate_removal_dataset_path.toPlainText())
            and (
                # And a label file is selected or labels are not being removed
                (input_file := self.duplicate_removal_label_path.toPlainText()
                    or not self.remove_duplicate_labels.isChecked())
                )):
            out_folder_exists = isdir(folder_path)
            input_file_exists = isfile(input_file)
            # Returning `out_folder_exists and input_file_exists` would be valid,
            # but would not send the message to the window
            if out_folder_exists and (input_file_exists or not self.remove_duplicate_labels.isChecked()):
                return True
        self.status_bar.showMessage("Invalid duplicate removal form input. "
                                    "Please check and correct your selections.",
                                    timeout=5000)
        return False

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

        self.always_reset_checkmarks = QCheckBox()
        self.always_reset_checkmarks.setToolTip("Sets the zone checkboxes according to the labels even when "
                                                "all labels are `False`. Useful when checking labels are correct, "
                                                "but otherwise leaving this off will stop the checkboxes from becoming "
                                                "unchecked after labelling a frame.")
        label_options_layout.addRow("Always reset label states?: ", self.always_reset_checkmarks)

        unlabelled_data_folder_layout = QHBoxLayout()
        self.unlabelled_data_folder = QTextEdit()
        self.unlabelled_data_folder_select = QPushButton("Select folder...")
        unlabelled_data_folder_layout.addWidget(self.unlabelled_data_folder)
        unlabelled_data_folder_layout.addWidget(self.unlabelled_data_folder_select)
        label_options_layout.addRow("Unlabelled data source: ", unlabelled_data_folder_layout)
        self.unlabelled_data_folder_select.clicked.connect(self.load_unlabelled_data)

        labelled_data_folder_layout = QHBoxLayout()
        self.labelled_data_file = QTextEdit()
        self.labelled_data_file_select = QPushButton("Select label_path...")
        labelled_data_folder_layout.addWidget(self.labelled_data_file)
        labelled_data_folder_layout.addWidget(self.labelled_data_file_select)
        label_options_layout.addRow("Labelled data output label_path: ", labelled_data_folder_layout)
        self.labelled_data_file_select.clicked.connect(self.select_dataset_labels_file)

        self.labelled_data_submit = QPushButton("Add labels to label file")
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
        self.create_note_presence_label_file_frame(self.labelled_data_file.toPlainText())
        for checkbox in self.label_checkboxes:
            checkbox.setChecked(False)

    def create_note_presence_label_file_frame(self, label_path):
        if not self.unlabelled_file_list:
            self.status_bar.showMessage("No data to make label frame file. "
                                        "Please select a dataset first.", timeout=15000)
            return

        label_path = Path(label_path)

        if not exists(label_path):
            # Generate empty rows
            label_df = label_tools.generate_eight_zone_label_df(self.unlabelled_file_list)
            label_tools.save_label_df(label_df, label_path)

            self.frame_select.setValue(0)

        # TODO: Refactor functionality to simplify usage with other label types
        else:
            columns = ("file_name",
                       "b1", "b2", "b3", "b4",
                       "b5", "b6", "b7", "b8")

            self.status_bar.showMessage("Reading existing label file...", timeout=3000)
            try:
                with open(label_path, "r") as label_file:
                    df = pd.read_csv(label_file)
                if list(df.columns) != columns:
                    self.status_bar.showMessage("Specified file is not a valid label file.", 5000)
                    self.labelled_data_file.setText("")
                else:
                    num_rows = len(df.index)
                    if num_rows != len(self.unlabelled_file_list):  # Most likely legacy label file
                        raise ValueError("Specified dataframe is not the correct format for this dataset.")
                    last_labelled_row = 0
                    for count, row in enumerate(df.itertuples()):
                        # Check if any labels are True - first 2 items are row index and label name,
                        # so we remove those to test only the labels
                        if any(row[2:]):
                            # Mark that the last frame checked has been labelled
                            last_labelled_row = count

                    # Set the labeller to the frame after the last one that has been labelled, unless it is at the end
                    self.frame_select.setValue(min(last_labelled_row + 1, num_rows))
                    self.label_dataframe = df
            except Exception as e:
                self.status_bar.showMessage(f"Failed to open file. - {e}", 5000)
                self.labelled_data_file.setText("")
                return
        self.label_file_path = label_path

    def add_labelled_frame(self):
        # Send the current frame as the row index to edit - frame count starts at `0` so should cause no issues
        self.add_note_presence_labels(self.label_file_path, self.frame_select.value())
        self.frame_select.setValue(self.frame_select.value() + 1)

    def add_note_presence_labels(self, path, row):
        data = [self.unlabelled_file_list[self.frame_select.value()][1]]

        for checkbox in self.label_checkboxes:
            data.append(checkbox.isChecked())
        self.label_dataframe.loc[row] = data
        with open(path, "w") as label_file:
            self.label_dataframe.to_csv(label_file, index=False)

    def set_checkboxes_to_label_states(self, row):
        if not self.label_dataframe.empty:
            labels = self.label_dataframe.iloc[row][1:]
            if any(labels) or self.always_reset_checkmarks.isChecked():
                for count, checkbox in enumerate(self.label_checkboxes):
                    # print(labels.iloc[count])
                    # Emits a deprecation warning for using `np.bool_` as an index. Since this is not the case,
                    # the closest I can find to a current issue related to this is
                    # this issue request: https://github.com/OceanParcels/parcels/issues/1119
                    checkbox.setChecked(labels.iloc[count])

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

        # Prevent SpinBox from being forcefully set to `-1`, and allowing future datasets to use index -1 in the process
        self.frame_select.setMaximum(max(len(self.unlabelled_file_list) - 1, 0))
        self.load_unlabelled_frame()

    def load_unlabelled_frame(self):
        if self.unlabelled_file_list:
            data_pixmap = QPixmap(self.unlabelled_file_list[self.frame_select.value()][0])
            self.data_image.setPixmap(data_pixmap)
            self.set_checkboxes_to_label_states(self.frame_select.value())
        else:
            self.status_bar.showMessage("Please select a source folder before attempting to select a frame.", 5000)


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
        path, file_filter = QFileDialog.getOpenFileName(self, "Open File", "")
        self.video_paths.setText(path)
        file_name = path.split("/")[-1]
        # Change output_name to the video file name if no name is given
        if not self.output_file_name.toPlainText():
            self.output_file_name.setText(file_name.split(".")[0])

    def set_resize_layout_state(self):
        self.resize_options.setEnabled(self.resize_data_enabled.isChecked())

    def set_aspect_by_state(self):
        self.keep_aspect_by.setEnabled(self.keep_aspect_option.isChecked())

    def startConversionWorker(self, video_path, output_path, frame_name, compress_frames, resize, resize_options, remove_duplicate_frames):

        if self.valid_video_conversion_form_input():
            video_conversion_worker = video_conv.VideoConversionWorker(video_path=video_path,
                                                                       output_path=output_path,
                                                                       frame_name=frame_name,
                                                                       compress_frames=compress_frames,
                                                                       resize=resize, resize_options=resize_options,
                                                                       remove_duplicate_frames=remove_duplicate_frames)
            video_conversion_worker.signals.progress.connect(self.displayVideoProcessingProgress)
            video_conversion_worker.signals.pruning.connect(self.displayFrameDuplicateRemoval)
            video_conversion_worker.signals.finished.connect(self.displayConversionCompletion)
            self.thread_pool.start(video_conversion_worker)

    def displayVideoProcessingProgress(self, progress_data):
        self.status_bar.showMessage(f"[{progress_data['frame_name']}] Processing video... "
                                    f"(Last frame output: {progress_data['frame_num']})")

    def displayFrameDuplicateRemoval(self, frame_name):
        self.status_bar.showMessage(f"[{frame_name}] Removing duplicate frames (This may take some time)...")

    def displayConversionCompletion(self, completion_data):
        self.status_bar.showMessage(f"[{completion_data['frame_name']}] Processing video complete!"
                                    f"{' Duplicated frames removed: ' + str(completion_data['frame_duplicates']) if completion_data['frame_duplicates'] != -1 else ''}", timeout=15000)

    def valid_video_conversion_form_input(self) -> bool:
        if (self.output_file_name.toPlainText()
                and (folder_path := self.output_folder_path.toPlainText())
                and (input_file := self.video_paths.toPlainText())):
            out_folder_exists = isdir(folder_path)
            input_file_exists = isfile(input_file)
            # Returning `out_folder_exists and input_file_exists` would be valid,
            # but would not send the message to the window
            if out_folder_exists and input_file_exists:
                return True
        self.status_bar.showMessage("Invalid video conversion form input. "
                                    "Please check and correct your selections.",
                                    timeout=5000)
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont("Bahnschrift")
    window = WamaiToolkitMainWindow()
    window.show()
    sys.exit(app.exec())