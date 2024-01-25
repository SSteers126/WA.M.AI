from hashlib import sha512
from os import listdir
from os import remove as remove_file
from pathlib import Path

from pandas import read_csv
from PIL import Image


def remove_duplicate_images(images_dir: Path, image_extensions=(".png",)) -> list[str]:
    """
    Removes duplicate frames from a directory of images.
    One copy of the duplicated images will be kept, and all other copies are deleted.

    :param images_dir: The directory to search for duplicated frames.
    :param image_extensions: The file extensions of files to check for duplication. By default, only checks for images with the extension ".png".
    :return: A list of all filenames of the images that were duplicates (the last remaining copy that is kept are *not* included)
    """

    image_hashes = {}
    image_list = []

    images_dir = Path(images_dir)

    for filename in listdir(images_dir):
        for extension in image_extensions:
            if filename.endswith(extension):
                # Add all images to `image_list` - ignore other files (such as label files)
                image_list.append(filename)

                # Open the image via pillow to generate a hash via its content
                image_path = images_dir / filename
                cur_frame = Image.open(image_path)
                # Set the filename to be indexed at its hash - all duplicates will overwrite their previous instance,
                # so duplicates will be implicitly removed
                image_hashes[sha512(cur_frame.tobytes()).hexdigest()] = filename

                # File cannot have multiple extensions, so skip any that haven't been searched
                # when the correct one is found
                break

    non_duplicate_images = image_hashes.values()
    # TODO: test that taking non_duplicates from full list is viable, and returns identically. Should be faster? (and more readable)
    duplicate_images = []
    for image in image_list:
        # Delete duplicated frames
        if image not in non_duplicate_images:
            remove_file(images_dir / image)
            duplicate_images.append(image)
    return duplicate_images


def remove_labels(label_fp: str | Path, duplicate_labels: list[str]):
    """
    Removes rows from a label file and overwrites it with the respective labels removed

    :param label_fp: The file label_path of the label file to remove labels from
    :param duplicate_labels: The names of samples to remove the label row of within the file
    :return:
    """
    # Open DataFrame of label file
    label_fp = Path(label_fp)
    with open(label_fp, "r") as old_label_file:
        label_df = read_csv(old_label_file)

    # Remove the rows that contain the given labels
    for duplicate_label in duplicate_labels:
        label_df.drop(label_df.loc[label_df['file_name'] == duplicate_label].index, inplace=True)

    with open(label_fp, "w") as new_label_file:
        label_df.to_csv(new_label_file, index=False)