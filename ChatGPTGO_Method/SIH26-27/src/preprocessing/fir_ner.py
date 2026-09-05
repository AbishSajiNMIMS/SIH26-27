import spacy
from pathlib import Path


INPUT_FILE = Path("data/raw/fir_sample.txt")


def extract_entities():

    # Load English NLP model
    nlp = spacy.load("en_core_web_sm")

    # Read FIR
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        text = file.read()

    # Process text
    doc = nlp(text)

    print("\nEXTRACTED ENTITIES")
    print("------------------")

    for entity in doc.ents:

        print(
            f"{entity.text} -> {entity.label_}"
        )


if __name__ == "__main__":
    extract_entities()