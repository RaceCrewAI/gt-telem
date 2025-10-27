import csv
import os


TRACK_NAMES = {}

track_names_path = os.path.join(os.path.dirname(__file__), "track_names.csv")
with open(track_names_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        TRACK_NAMES[int(row["id"])] = row["name"]
