import csv
from importlib.resources import files


TRACK_NAMES = {}

csv_data = files('gt_telem.data').joinpath('track_names.csv').read_text()
reader = csv.DictReader(csv_data.splitlines())
for row in reader:
    TRACK_NAMES[int(row["id"])] = row["name"]
