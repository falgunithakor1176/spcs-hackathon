
import csv
import os
import json

def validate_csv(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            return {"file": filename, "error": "Empty file"}
        
        col_count = len(headers)
        row_count = 0
        missing_values = {h: 0 for h in headers}
        seen = set()
        duplicates = 0
        samples = []

        for row in reader:
            row_count += 1
            if len(samples) < 5:
                samples.append(dict(zip(headers, row)))
            
            # Check missing
            for i, val in enumerate(row):
                if not val.strip():
                    missing_values[headers[i]] += 1
                    
            # Check duplicates (assuming first column is ID or full row tuple)
            row_tuple = tuple(row)
            if row_tuple in seen:
                duplicates += 1
            else:
                seen.add(row_tuple)

    # Filter out missing values that are 0
    missing_report = {k: v for k, v in missing_values.items() if v > 0}

    return {
        "file": filename,
        "row_count": row_count,
        "col_count": col_count,
        "missing_values": missing_report,
        "duplicates": duplicates,
        "samples": samples
    }

seed_dir = os.path.join("data", "seed")
reports = {}
for f in os.listdir(seed_dir):
    if f.endswith(".csv"):
        reports[f] = validate_csv(os.path.join(seed_dir, f))

with open("data_validation_results.json", "w", encoding="utf-8") as f:
    json.dump(reports, f, indent=2)

