#This is the script to parse the CSV Data

import wmill
import csv
import io


def main(csvFile: bytes):
    
    text = csvFile.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    
    for row in reader:
        
        if any(row.values()):
            rows.append(row)

    return rows
