import csv
from datetime import datetime
from pathlib import Path


INPUT_FILE = Path("data/raw/cdr_sample.csv")
OUTPUT_FILE = Path("data/processed/cdr_clean.csv")

REQUIRED_COLUMNS = [
    "caller",
    "receiver",
    "timestamp",
    "duration_sec",
    "cell_tower",
]


def normalize_cdr():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    cleaned_records = []

    with open(INPUT_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # Check that all required columns exist
        if not all(column in reader.fieldnames for column in REQUIRED_COLUMNS):
            raise ValueError("CDR file is missing required columns.")

        for row in reader:
            # Remove records with missing caller/receiver
            if not row["caller"] or not row["receiver"]:
                continue

            # Standardize IDs
            caller = row["caller"].strip().upper()
            receiver = row["receiver"].strip().upper()

            # Standardize timestamp
            try:
                timestamp = datetime.strptime(
                    row["timestamp"].strip(),
                    "%Y-%m-%d %H:%M"
                ).isoformat()
            except ValueError:
                continue

            # Validate duration
            try:
                duration = int(row["duration_sec"])
            except ValueError:
                continue

            if duration < 0:
                continue

            cleaned_records.append({
                "caller": caller,
                "receiver": receiver,
                "timestamp": timestamp,
                "duration_sec": duration,
                "cell_tower": row["cell_tower"].strip().upper(),
            })

    # Write cleaned data
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=REQUIRED_COLUMNS
        )

        writer.writeheader()
        writer.writerows(cleaned_records)

    print(f"Cleaned {len(cleaned_records)} records.")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    normalize_cdr()