from rapidfuzz.fuzz import ratio
import jellyfish


def normalize_name(name):
    """
    Basic name normalization.
    """

    return (
        name
        .strip()
        .upper()
        .replace(".", "")
        .replace(",", "")
    )


def compare_names(name1, name2):

    name1 = normalize_name(name1)
    name2 = normalize_name(name2)

    # Exact match
    if name1 == name2:
        return 100

    # Fuzzy similarity
    fuzzy_score = ratio(name1, name2)

    # Phonetic similarity
    soundex_match = (
        jellyfish.soundex(name1)
        == jellyfish.soundex(name2)
    )

    metaphone_match = (
        jellyfish.metaphone(name1)
        == jellyfish.metaphone(name2)
    )

    # Combine signals
    score = fuzzy_score

    if soundex_match:
        score += 10

    if metaphone_match:
        score += 10

    return min(score, 100)


def main():

    names = [
        "Rahul Sharma",
        "Rahul S.",
        "RAHUL SHARMA",
        "Rhaul Sharma",
        "Amit Kumar"
    ]

    reference = "Rahul Sharma"

    print("\nENTITY RESOLUTION")
    print("-----------------")
    print(f"Reference: {reference}\n")

    for name in names:

        score = compare_names(
            reference,
            name
        )
        if score >= 85:
            result = "LIKELY SAME"
        else:
            result = "REVIEW"

        print(
            f"{name:20} -> "
            f"{score:.2f} ({result})"
        )


if __name__ == "__main__":
    main()