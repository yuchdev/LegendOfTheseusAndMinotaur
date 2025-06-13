import json
import re
import sys

# Canonical characters
CHARACTERS = {
    "Monstradamus", "IsoldA", "Nutscracker", "Organizm(-:",
    "Theseus", "Ariadne", "UGLI 666", "Romeo-y-Cohiba", "Sartrik"
}

# Aliases
ALIASES = {
    "Nut$cracker": "Nutscracker",
    "UGLI666": "UGLI 666",
    "Isolda": "IsoldA",
    "Romeo": "Romeo-y-Cohiba",
    "Organizm)-": "Organizm(-:",
    "Organizm(-": "Organizm(-:",
    "Organizm)-:": "Organizm(-:",
    "TheZeus": "Theseus"
}

MOODS = {
    "positive": [
        "calm",
        "caring",
        "joyful",
        "hopeful",
        "loving",
        "proud",
        "solemn"
    ],
    "neutral": [
        "confused",
        "curious",
        "indifferent",
        "contemplative",
        "resigned"
    ],
    "negative": [
        "angry",
        "anxious",
        "ashamed",
        "fearful",
        "sad",
        "manipulative"
    ],
    "complex": [
        "defensive",
        "desperate",
        "impatient",
        "jealous",
        "nauseous",
        "playful",
        "sarcastic",
        "skeptical",
        "surprised"
    ]
}


def is_chapter_separator(line):
    stripped = line.strip()
    return stripped and stripped[0] in ":;" and all(c in ":;-()" for c in stripped)


def resolve_character(name):
    if name in CHARACTERS:
        return name, None
    elif name in ALIASES:
        return ALIASES[name], name
    return None, None


def parse_play_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw_lines = [line.rstrip('\n') for line in f]

    chapters = []
    current_chapter = []
    i = 0

    while i < len(raw_lines):
        line = raw_lines[i].strip()

        if not line:
            i += 1
            continue

        if is_chapter_separator(line):
            if current_chapter:
                chapters.append(current_chapter)
                current_chapter = []
            i += 1
            continue

        # Inline format: "Character: line"
        colon_match = re.match(r"^(.+?):\s+(.*)", line)
        if colon_match:
            name = colon_match.group(1).strip()
            resolved, alias = resolve_character(name)
            if resolved:
                text = colon_match.group(2).strip()
                current_chapter.append({
                    "character": resolved,
                    "to": "",
                    "mood": "",
                    "text": text,
                    **({"alias": alias} if alias else {})
                })
                i += 1
                continue

        # Standalone name, followed by multi-line speech
        name = line
        resolved, alias = resolve_character(name)
        if resolved:
            i += 1
            speech_lines = []
            while i < len(raw_lines):
                next_line = raw_lines[i]
                if is_chapter_separator(next_line.strip()):
                    break
                colon_match = re.match(r"^(.+?):\s+(.*)", next_line.strip())
                if colon_match and resolve_character(colon_match.group(1).strip())[0]:
                    break
                name_line = next_line.strip()
                if name_line in CHARACTERS or name_line in ALIASES:
                    break
                speech_lines.append(next_line)
                i += 1

            text = "\n".join(paragraph for paragraph in "\n".join(speech_lines).split('\n\n'))
            current_chapter.append({
                "character": resolved,
                "to": "",
                "mood": "",
                "text": text.strip(),
                **({"alias": alias} if alias else {})
            })
            continue

        # Unknown line
        i += 1

    if current_chapter:
        chapters.append(current_chapter)

    return chapters


def convert_to_json(input_path, output_path):
    data = parse_play_file(input_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Converted play saved to {output_path}")


def main():
    """
    :return: system exit code
    """
    if len(sys.argv) != 3:
        print("Usage: python play_json.py <input_path> <output_path>")
        return 1
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    try:
        convert_to_json(input_path, output_path)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


# Usage example
if __name__ == "__main__":
    sys.exit(main())
