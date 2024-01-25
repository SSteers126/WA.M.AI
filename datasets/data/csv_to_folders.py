import os
from os import listdir, makedirs
from os.path import isfile, exists
from pathlib import Path
from shutil import copy, copy2

from time import time
from itertools import combinations

import pandas as pd

SRC_FOLDER = Path("TEST-okinimesumama-expert-24-played-incomplete/")


def gen_label_combo(zones: list[str]) -> str:
    """
    Generate a folder name based on the zones that are True. Used to keep naming conventions consistent

    :param zones: All zones that are true. \
    *(Ensure that you only pass the names of zones that are true, as opposed to all zones)*
    :return: A string for the folder to be used for that zone combination
    """
    if not zones:
        return "None"
    return "_".join(zones)


def gen_folder_labels(labels: list[str], include_none: bool) -> list[str]:
    """
    Generates all folder names to include to allow a sample with any combination of zones enabled
    to be sent to its respective folder.

    :param labels: The set of labels/zones to use
    :param include_none: Whether the first item should be a folder name for samples where no zones are enabled
    :return: A list of all necessary folder names to categorise any given sample
    """
    combos = []
    for L in range(len(labels) + 1):
        for combo in combinations(labels, L):
            combos.append(combo)

    # Can't use "N/A" in a label_path for no labels, so use None instead
    folder_names = []

    # Exclude first entry (combo of no items) if include_none is `False`
    start_index = 1
    if include_none:
        start_index = 0

    # The first item is no labels, which is already accounted for with "None",
    # so we ignore it for appending folder names.
    for combo in combos[start_index:]:
        folder_names.append(gen_label_combo(combo))

    return folder_names

def gen_eight_zone_folder_labels():
    return gen_folder_labels(["b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8"], True)

def eight_zone_csv_labels_to_folders(dataset_folder: Path, label_file_name: str = "labels.csv",
                                     data_file_extensions: tuple[str] = ("png",)) -> None:
    """
    Takes a label file generated by the toolkit's labeller for eight zone note presence,
    and uses that to organise the frames into folders based on the state of the buttons.

    :param dataset_folder: The label_path to the folder containing *both* the label file and frames
    :param label_file_name: The name of the label file to use to organise the frames
    :param data_file_extensions: The file extension(s) of the frames
    :return:
    """

    dataset_folder = Path(dataset_folder)
    folder_name = dataset_folder.parts[-1]  # Get dataset folder name
    # Make a new folder for the dataset, and add the current time to avoid over-writing another dataset
    reorganised_folder_name = folder_name + "_ordered_" + str(round(time(), 2))
    reorganised_folder = dataset_folder / ".." / reorganised_folder_name
    if not exists(reorganised_folder):
        makedirs(reorganised_folder)

    label_folder_names = gen_eight_zone_folder_labels()
    for label_folder in label_folder_names:
        label_folder_path = reorganised_folder / label_folder
        if not exists(label_folder_path):
            makedirs(label_folder_path)

    label_path = dataset_folder / label_file_name
    df = pd.read_csv(label_path)
    # Gets rows as named tuples with names based on columns
    # faster than `itterrows()`



    for row in df.itertuples():
        labelled_file_name = row.file_name
        button_state = [row.b1, row.b2, row.b3, row.b4,
                        row.b5, row.b6, row.b7, row.b8]

        enabled_zones = []

        # Get the names of each zone that is enabled
        for count, state in enumerate(button_state):
            if state:
                enabled_zones.append(f"b{count+1}")
        # Generate a matching folder name to place the sample within
        sample_label_folder = gen_label_combo(enabled_zones)

        # Ensure the file is a valid sample file, and not something else
        if isfile(file_path := dataset_folder / labelled_file_name) \
                and labelled_file_name.split(".")[-1] in data_file_extensions:
            # Copy the sample to the respective folder
            copy2(file_path, reorganised_folder / sample_label_folder / labelled_file_name)

    # for file in listdir(dataset_folder):
    #     # File is either labels or data
    #     if isfile(file_path := dataset_folder / file) and file.split(".")[-1] in data_file_extensions:
    #         ...

# print(gen_eight_zone_folder_labels())
eight_zone_csv_labels_to_folders(SRC_FOLDER)

# eight_zone_csv_labels_to_folders(SRC_FOLDER)
