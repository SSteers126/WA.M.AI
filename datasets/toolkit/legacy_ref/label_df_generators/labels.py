from os.path import exists
from pathlib import Path

import pandas as pd


def create_note_presence_label_file_stub_legacy(self, path):
    path = Path(path)
    columns = ["file_name",
               "b1", "b2", "b3", "b4",
               "b5", "b6", "b7", "b8"]
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


def add_note_presence_labels_legacy(self, path):
    data = [self.unlabelled_file_list[self.frame_select.value()][1]]

    for checkbox in self.label_checkboxes:
        data.append(checkbox.isChecked())
    self.label_dataframe.loc[len(self.label_dataframe.index)] = data
    with open(path, "w") as label_file:
        self.label_dataframe.to_csv(label_file, index=False)


def add_labelled_frame_legacy(self):
    if self.frame_select.value() == self.frame_select.maximum():
        self.status_bar.showMessage("Final frame for this dataset has been labelled.", timeout=15000)
    else:
        self.add_note_presence_labels_legacy(self.label_file_path)
        self.frame_select.setValue(self.frame_select.value() + 1)

    # Add label data to CSV - create if not made and add columns, add row, check if full?, load frame after last in csv?