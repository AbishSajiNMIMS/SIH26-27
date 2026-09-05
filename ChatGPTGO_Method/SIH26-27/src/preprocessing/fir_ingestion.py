from pathlib import Path


INPUT_FILE = Path("data/raw/fir_sample.txt")


def read_fir():

    if not INPUT_FILE.exists():
        print("FIR file not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        text = file.read()

    print("\nFIR INGESTION")
    print("-------------")
    print(f"File: {INPUT_FILE}")
    print(f"Characters: {len(text)}")

    print("\nCONTENT")
    print("-------")
    print(text)


if __name__ == "__main__":
    read_fir()