import json
import glob
import re
import os

from constants import CHARACTERS, ALIASES

# Matches uppercase and lowercase variants, omitting \bhis\b
PRONOUNS = [
    r"\b[Hh]e(?:'ll)?\b",
    r"\b[Ss]he(?:'ll)?\b",
    r"\b[Hh]er\b",
    r"\b[Hh]ers\b",
    r"\b[Tt]hey(?:'ll)?\b",
    r"\b[Tt]hem\b",
    r"\b[Tt]heir\b",
    r"\b[Tt]heirs\b"
]

PATTERN = re.compile("|".join(PRONOUNS), flags=re.IGNORECASE)

def has_third_person_mention(text):
    return bool(PATTERN.search(text))

def main():
    for filepath in glob.glob('scripted_events/day-0*.json'):
        day_match = re.search(r'day-(0\d+)\.json', filepath)
        if not day_match:
            continue
        day_id = day_match.group(1)
        results = []
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for event in data:
                if event.get('event_type') == 'dialogue':
                    if 'third_person' in event:
                        continue
                    to_field = event.get('to', [])
                    if isinstance(to_field, list) and len(to_field) == 1 or not to_field:
                        if has_third_person_mention(event.get('text', '')):
                            results.append(event)
        with open(f'third-persons-day-{day_id}.json', 'w', encoding='utf-8') as out:
            json.dump(results, out, indent=2)

if __name__ == '__main__':
    main()