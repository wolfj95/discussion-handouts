# Passage Aggregator

Pulls each student's selected passage out of their Canvas text-entry submission and writes it into the `Passage` column of the course roster.

No dependencies beyond the Python standard library.

## Expected files

Place these in this directory (both are gitignored):

- `roster.csv` - the course roster with a `Name` column in `Last,First` format. A `Passage` column is added if it's missing; any existing passages are overwritten for students who submitted.
- `passage_submissions/` - the unzipped Canvas "Download Submissions" folder. Files are named like `lastfirst_123456_text.html` (or `lastfirst_LATE_123456_text.html`).

## Usage

```bash
python extract_passages.py
```

The script:
1. Extracts the text from each submission's HTML.
2. Matches the filename to a roster name, trying `lastfirst`, `firstlast`, and first-word-of-first-name variants, then falling back to fuzzy matching.
3. Writes the passage into `roster.csv` (in place).
4. Writes any submissions it couldn't match to `unmatched_passages.txt` for manual review.

Fuzzy matching can occasionally pick the wrong student when two names are similar, so skim the `✓ Matched:` lines in the output.
