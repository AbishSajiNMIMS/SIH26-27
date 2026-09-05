import re
from pathlib import Path


INPUT_FILE = Path("data/raw/fir_sample.txt")


def find_persons(text):
    """
    Very simple person extraction for our prototype.
    In the final system this will come from NER.
    """

    persons = re.findall(
        r"\b(?:Rahul|Amit|P001|P002|P003|P004)\b",
        text
    )

    return list(dict.fromkeys(persons))


def resolve_pronouns(text, persons):

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    last_person = None

    resolved = []

    for sentence in sentences:

        # Check whether this sentence contains a known person
        for person in persons:

            if re.search(
                rf"\b{re.escape(person)}\b",
                sentence,
                re.IGNORECASE
            ):
                last_person = person

        # Very simple prototype rule
        if re.search(
            r"\b(he|she|they)\b",
            sentence,
            re.IGNORECASE
        ) and last_person:

            sentence = re.sub(
                r"\b(he|she|they)\b",
                last_person,
                sentence,
                flags=re.IGNORECASE
            )

        resolved.append(sentence)

    return " ".join(resolved)


def main():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    persons = find_persons(text)

    resolved_text = resolve_pronouns(
        text,
        persons
    )

    print("\nPERSONS FOUND")
    print("-------------")

    for person in persons:
        print(person)

    print("\nRESOLVED TEXT")
    print("-------------")
    print(resolved_text)


if __name__ == "__main__":
    main()