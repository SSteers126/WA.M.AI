# from ..video_conv_testing import video_to_frames
from PySide6.QtCore import QRunnable, Slot, QObject, Signal
from pathlib import Path
import cv2
from PIL import Image
from PySide6.QtWidgets import QProgressDialog


class VideoConversionSignals(QObject):
    finished = Signal()  # QtCore.Signal
    error = Signal(tuple)
    cur_frame = Signal(int)
    progress = Signal(dict)
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

        self.signals.finished.emit()


    def resize_dimensions_with_aspect(self, dimension1, dimension2, dimension1_new):
        scale_factor = dimension1_new / float(dimension1)  # Ensure output is a float for more accurate results
        dimension2_new = int(dimension2 * scale_factor)
        return dimension1_new, dimension2_new
