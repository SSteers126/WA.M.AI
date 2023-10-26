import cv2
from pathlib import Path
vidcap = cv2.VideoCapture(r'E:\OBS\Encoded\Maimai training 1.mp4')
print(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
# success,image = vidcap.read()
# count = 0
# while success:
#   cv2.imwrite("out/frame%d.png" % count, image)     # save frame as PNG file
#   success,image = vidcap.read()
#   # print('Read a new frame: ', success)
#   count += 1


def video_to_frames(video, output_folder, output_frame_name):
    output_folder = Path(output_folder)
    video_capture = cv2.VideoCapture(video)
    frame = 0

    frame_extract_success, image = video_capture.read()
    while frame_extract_success:
        cv2.imwrite(str((output_folder / f"{output_frame_name}-{format(frame, '0.10d')}.png").resolve()), image)
        frame_extract_success, image = video_capture.read()
        frame += 1
