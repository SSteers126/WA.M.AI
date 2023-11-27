import pandas as pd

from os import walk
from os.path import isfile, join

from pathlib import Path

# TODO: Add absolute option to choose whether paths become absolute when compiled,
#  then use that to make a function that can store the compiled labels as a singular CSV

class NoLabelFilesFoundError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def compile_label_files_in_directory(directory: Path, label_file_name: str) -> list[Path]:
    """
    Looks for all files with the name `label_file_name`, and returns all absolute paths of those files.

    :param directory: The root directory to check for label files within
    :param label_file_name: The name of the label file to look for (assumes all requested label files have this name)

    :return: A list of all `pathlib.Path` of the found label files. If no label files are found, an empty list will be returned.
    """

    if type(directory) == str:
        directory = Path(directory)
    # Include subclasses like `WindowsPath`, `PosixPath` etc
    elif not isinstance(directory, Path):
        raise ValueError("`directory` must be a `Path` to the requested dataset.")

    label_file_paths = []

    if not directory.is_dir():
        raise ValueError(f"The `directory` '{directory}' is not valid. Please check your arguments.")

    else:
        for cur_path, directories, files in walk(directory):
            for file in files:
                if file == label_file_name:
                    label_file_paths.append(Path(join(cur_path, file)))
                    break

    if not label_file_paths:
        raise NoLabelFilesFoundError("No label files were found in this directory.")

    return label_file_paths


def compile_dataset_labels(label_file_paths: list[Path]) -> pd.DataFrame:
    """
    Checks all label files within `label_file_paths`, loads each file one at a time, and concatenates all rows
    into a single `DataFrame`. All paths are made absolute to ensure consistency with usage from other libraries.

    :param label_file_paths: The paths of all label files to concatenate together. All files must be `CSV` files

    :return: A `DataFrame` with all label file rows concatenated together, with paths resolved to be absolute.
    """

    # Anything that can be iterated through in the same way as a list will work, so tuples and sets are fine
    if type(label_file_paths) in (list, tuple, set):
        if not all(isinstance(label_file, Path) for label_file in label_file_paths):
            raise ValueError("All paths within `label_file_paths` must be a `pathlib.Path`.")
    else:
        raise ValueError("A list of paths containing all label files is required.")

    dataframes = []

    for label_file in label_file_paths:
        try:
            df = pd.read_csv(label_file)
        except pd.errors.ParserError:
            raise ValueError("Invalid label file given - Ensure all files are CSV files.")

        # Get the folder the CSV resides in - it should be in the same folder as the data,
        # so we can use that to get their paths too.
        data_folder = label_file.parent
        for row_num, row in df.iterrows():
            sample_path = (data_folder / row[0]).resolve()

            if isfile(sample_path):
                df.loc[row_num, "file_name"] = str(sample_path)
            else:
                raise ValueError(f"'{row[0]}' does not resolve to a real file. Check that all files are present. "
                                 f"(File path checked: {sample_path})")

        dataframes.append(df)

    return pd.concat(dataframes, axis=0)


def dataset_labels_to_dataframe(dataset_directory: Path, label_file_name: str) -> pd.DataFrame:
    """
    Convenience function that runs `compile_label_files_in_directory` and `compile_dataset_labels`.

    :param dataset_directory: The directory of the dataset to collect and compile label files from.
    :param label_file_name: The name of the label file (assumes that the name of the file will be the same for each dataset within the directory)

    :return: A `DataFrame` that holds all entries from each label file found, with all file paths resolved to be absolute.
    """
    return compile_dataset_labels(compile_label_files_in_directory(dataset_directory, label_file_name))


# Testing
if __name__ == "__main__":
    path = Path("FiNALE set 1/")
    final_dataframe = dataset_labels_to_dataframe(path, "8_zone_presence_labels.csv")
    print(final_dataframe)
    # print(final_dataframe.iloc[3000:])
