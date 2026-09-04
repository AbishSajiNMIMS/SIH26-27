import hashlib
from pathlib import Path


EVIDENCE_FILE = Path(
    "data/evidence/sample_fir.txt"
)


def calculate_sha256(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            data = file.read(4096)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


def main():

    if not EVIDENCE_FILE.exists():
        print("Evidence file not found.")
        return

    file_hash = calculate_sha256(
        EVIDENCE_FILE
    )

    print("\nEVIDENCE INTEGRITY")
    print("------------------")
    print(f"File: {EVIDENCE_FILE}")
    print(f"SHA-256: {file_hash}")


if __name__ == "__main__":
    main()