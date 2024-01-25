from datasets.toolkit.label_tools.label_generators import generic_boolean_label_df_generator

DF_COLUMNS = ("file_name",
              "b1", "b2", "b3", "b4",
              "b5", "b6", "b7", "b8")


def generate_eight_zone_label_df(label_list: list[tuple[str, str]]):
    return generic_boolean_label_df_generator.generate_boolean_label_df(label_list, DF_COLUMNS)
