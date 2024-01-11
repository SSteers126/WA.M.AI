# from ..video_conv_testing import video_to_frames

from hashlib import sha512
from os import listdir
from os import remove as remove_file
from pathlib import Path


import cv2
from PIL import Image
from PySide6.QtCore import QRunnable, Slot, QObject, Signal

from .image_duplicate_removal import remove_duplicate_images, remove_labels
# from PySide6.QtWidgets import QProgressDialog

class VideoDuplicateRemovalSignals(QObject):
    frame_removal = Signal(str)
    label_removal = Signal(str)
    finished = Signal(dict)


class VideoDuplicateRemovalWorker(QRunnable):
    '''
    VideoConversionWorker thread
    '''

    def __init__(self, dataset_path: str | Path, label_path="", remove_dataframe_labels=False):
        super(VideoDuplicateRemovalWorker, self).__init__()
        self.dataset_path = dataset_path
        self.label_path = label_path
        self.remove_dataframe_labels = remove_dataframe_labels
        self.signals = VideoDuplicateRemovalSignals()

    @Slot()  # QtCore.Slot
    def run(self):
        dataset_path = Path(self.dataset_path)
        label_path = Path(self.label_path)
        # Use the last folder name as a name to use for signals to help identify it
        # (assumed this folder will be likely to be names after the respective dataset)
        removal_job_name = dataset_path.parts[-1]
        self.signals.frame_removal.emit(removal_job_name)
        removed_frames = remove_duplicate_images(dataset_path)
        # Remove labels from the given label file if requested
        if self.remove_dataframe_labels:
            self.signals.label_removal.emit(removal_job_name)
            remove_labels(label_path, removed_frames)

        self.signals.finished.emit({"job_name": removal_job_name, "frames_removed": len(removed_frames)})


class VideoConversionSignals(QObject):
    error = Signal(tuple)
    cur_frame = Signal(int)
    progress = Signal(dict)
    pruning = Signal(str)
    finished = Signal(dict)


class VideoConversionWorker(QRunnable):
    '''
    VideoConversionWorker thread
    '''

    def __init__(self, *args, **kwargs):
        super(VideoConversionWorker, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.signals = VideoConversionSignals()

    @Slot()  # QtCore.Slot
    def run(self):
        '''
        Worker thread for converting a video to a PNG image sequence
        '''

        # print(self.args, self.kwargs)
        output_folder = Path(self.kwargs["output_path"])
        video_capture = cv2.VideoCapture(self.kwargs["video_path"])

        frame_extract_success, image = video_capture.read()
        frame = 0
        self.signals.progress.emit({"frame_name": self.kwargs["frame_name"], "frame_num": frame})

        while frame_extract_success:
            frame_name = f"{self.kwargs['frame_name']}-{str(frame).zfill(10)}.png"

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_frame = Image.fromarray(image)

            if self.kwargs["resize"]:
                if self.kwargs["resize_options"]["keep_aspect"]:
                    match self.kwargs["resize_options"]["aspect_locked_dimension"]:
                        # Resize relative to the chosen dimension
                        case "Width":
                            width, height = self.resize_dimensions_with_aspect(pil_frame.width,
                                                                               pil_frame.height,
                                                                               self.kwargs["resize_options"]["width"])

                        case "Height":
                            height, width = self.resize_dimensions_with_aspect(pil_frame.height,
                                                                               pil_frame.width,
                                                                               self.kwargs["resize_options"]["height"])

                        case _:
                            # This should never be possible, but kept here as a fallback in a worst-case scenario
                            width, height = (self.kwargs["resize_options"]["width"],
                                             self.kwargs["resize_options"]["height"])

                else:
                    width, height = self.kwargs["resize_options"]["width"], self.kwargs["resize_options"]["height"]

                # Ensure dimensions to not round to 0, but keep rounding
                # to be closest to calculations instead of just ceiling
                width, height = max(1, width), max(1, height)
                pil_frame = pil_frame.resize((width, height), resample=Image.Resampling.LANCZOS)

            pil_frame.save(output_folder / frame_name, optimize=self.kwargs["compress_frames"])

            # else:
            #     # opencv does not support `Path`s
            #     cv2.imwrite(str((output_folder / frame_name).resolve()), image)

            frame_extract_success, image = video_capture.read()
            frame += 1
            self.signals.progress.emit({"frame_name": self.kwargs["frame_name"], "frame_num": frame})

        frame_duplicates = -1

        if self.kwargs["remove_duplicate_frames"]:
            self.signals.pruning.emit(self.kwargs["frame_name"])
            frame_duplicates = len(remove_duplicate_images(output_folder))

        self.signals.finished.emit({"frame_name": self.kwargs["frame_name"], "frame_duplicates": frame_duplicates})


    def resize_dimensions_with_aspect(self, dimension1, dimension2, dimension1_new):
        scale_factor = dimension1_new / float(dimension1)  # Ensure output is a float for more accurate results
        dimension2_new = int(dimension2 * scale_factor)
        return dimension1_new, dimension2_new
