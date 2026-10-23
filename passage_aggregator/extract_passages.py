#!/usr/bin/env python3
"""
Extract passages from student HTML submissions and aggregate them into roster.csv
"""

import os
import csv
import re
from pathlib import Path
from html.parser import HTMLParser
from difflib import get_close_matches


class PassageExtractor(HTMLParser):
    """HTML parser to extract text from the div containing the passage"""

    def __init__(self):
        super().__init__()
        self.in_div = False
        self.text_parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            self.in_div = True

    def handle_endtag(self, tag):
        if tag == 'div':
            self.in_div = False

    def handle_data(self, data):
        if self.in_div:
            self.text_parts.append(data)

    def get_text(self):
        return ''.join(self.text_parts)


def normalize_name(name):
    """Normalize a name for matching (lowercase, remove spaces and special chars)"""
    return re.sub(r'[^a-z]', '', name.lower())


def extract_student_name_from_filename(filename):
    """
    Extract student name from filename like 'lehewhaley_476378_text.html'
    Returns normalized name from filename
    """
    # Remove _LATE_, numbers, _text.html
    name_part = re.sub(r'_LATE_\d+_text\.html$', '', filename)
    name_part = re.sub(r'_\d+_text\.html$', '', name_part)
    return name_part


def extract_passage_from_html(html_path):
    """Extract the passage text from an HTML file"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        parser = PassageExtractor()
        parser.feed(html_content)
        text = parser.get_text()

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip() if text else None
    except Exception as e:
        print(f"Error reading {html_path}: {e}")
        return None


def build_name_lookup(roster_data):
    """
    Build a lookup dictionary mapping normalized names to roster rows
    Returns: dict mapping normalized name -> (row_index, full_name, email)
    """
    lookup = {}

    for idx, row in enumerate(roster_data):
        if idx == 0:  # Skip header
            continue

        full_name = row[0]  # "Last,First" format
        email = row[1]

        # Try multiple name formats for matching
        # Format 1: lastfirst
        normalized = normalize_name(full_name)
        lookup[normalized] = (idx, full_name, email)

        # Format 2: firstlast
        if ',' in full_name:
            last, first = full_name.split(',', 1)
            first = first.strip()
            last = last.strip()

            # Handle names with parentheses like "Shuhan (Nancy)"
            first_clean = re.sub(r'\s*\([^)]*\)', '', first)

            firstlast = normalize_name(first_clean + last)
            lookup[firstlast] = (idx, full_name, email)

            # Also try with just first word of first name
            first_word = first_clean.split()[0] if first_clean else first
            firstwordlast = normalize_name(first_word + last)
            lookup[firstwordlast] = (idx, full_name, email)

    return lookup


def find_student_in_roster(filename_name, name_lookup):
    """
    Find a student in the roster based on the filename
    Returns: (row_index, full_name, email) or None
    """
    normalized_filename = normalize_name(filename_name)

    # Direct match
    if normalized_filename in name_lookup:
        return name_lookup[normalized_filename]

    # Try fuzzy matching
    all_normalized_names = list(name_lookup.keys())
    matches = get_close_matches(normalized_filename, all_normalized_names, n=1, cutoff=0.8)

    if matches:
        return name_lookup[matches[0]]

    return None


def main():
    # Paths
    base_dir = Path(__file__).parent
    roster_path = base_dir / 'roster.csv'
    submissions_dir = base_dir / 'passage_submissions'
    unmatched_path = base_dir / 'unmatched_passages.txt'

    # Read roster
    print("Reading roster...")
    with open(roster_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        roster_data = list(reader)

    # Find the "Passage" column by name, adding it if it doesn't exist
    if 'Passage' not in roster_data[0]:
        roster_data[0].append('Passage')
    passage_col = roster_data[0].index('Passage')

    # Pad short rows so every row has a passage cell
    for i in range(1, len(roster_data)):
        while len(roster_data[i]) < len(roster_data[0]):
            roster_data[i].append('')

    # Build name lookup
    name_lookup = build_name_lookup(roster_data)

    # Process HTML files
    print("Processing HTML files...")
    html_files = list(submissions_dir.glob('*.html'))
    matched_count = 0
    unmatched = []

    for html_file in html_files:
        # Extract passage
        passage = extract_passage_from_html(html_file)
        if not passage:
            print(f"⚠️  No passage found in {html_file.name}")
            continue

        # Extract student name from filename
        filename_name = extract_student_name_from_filename(html_file.name)

        # Find student in roster
        match = find_student_in_roster(filename_name, name_lookup)

        if match:
            row_idx, full_name, email = match
            roster_data[row_idx][passage_col] = passage
            matched_count += 1
            print(f"✓ Matched: {html_file.name} -> {full_name}")
        else:
            unmatched.append((html_file.name, passage))
            print(f"✗ No match: {html_file.name}")

    # Write updated roster
    print("\nWriting updated roster...")
    with open(roster_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(roster_data)

    # Write unmatched passages
    if unmatched:
        print(f"\nWriting {len(unmatched)} unmatched passages...")
        with open(unmatched_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("UNMATCHED PASSAGES - Please manually review\n")
            f.write("=" * 80 + "\n\n")

            for filename, passage in unmatched:
                f.write(f"File: {filename}\n")
                f.write("-" * 80 + "\n")
                f.write(f"{passage}\n")
                f.write("\n" + "=" * 80 + "\n\n")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total HTML files processed: {len(html_files)}")
    print(f"Successfully matched: {matched_count}")
    print(f"Unmatched: {len(unmatched)}")
    print(f"\nRoster updated: {roster_path}")
    if unmatched:
        print(f"Unmatched passages saved to: {unmatched_path}")
    print("=" * 80)


if __name__ == '__main__':
    main()
