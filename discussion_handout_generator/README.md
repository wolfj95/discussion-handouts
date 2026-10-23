# Discussion Handout Generator

Generate personalized two-sided handouts for students. Each handout includes a customized front page with the student's name and selected passage, plus a standard back page with discussion questions.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create a sample back page PDF (or replace with your own):
```bash
python create_sample_back_page.py
```

## Usage

### Basic Usage

```bash
python generate_handouts.py students.csv back_page.pdf handouts.pdf
```

### Arguments

**Positional:**
- `students.csv` - CSV file containing student data (required)
- `back_page.pdf` - PDF file for the standard back page (required)
- `handouts.pdf` - Output filename (optional, defaults to `handouts.pdf`)

**Optional:**
- `-s, --session` - Session number to display in header (e.g., "3" or "3A")

### CSV Format

The CSV file must have `Name` and `Passage` columns. Optional columns:
- `Preferred Name` - used instead of `Name` when filled in
- `TF` - handouts are grouped by TF, with a separator page per group

Names in `Last,First` format are printed as `First Last`.

Example:
```csv
Name,Preferred Name,Email Address,TF,Passage
"Johnson,Alice",Ali,alice@example.edu,Morgan,"To be or not to be, that is the question..."
"Smith,Bob",,bob@example.edu,Morgan,"It was the best of times, it was the worst of times..."
```

See [sample_students.csv](sample_students.csv) for a sample file.

## Output

The script generates a single PDF with all student handouts. Each handout consists of:
- **Front page**:
  - Header with "T564A: Vibe Coding" (left) and "Discussion Handout | Session X" (right, if session specified)
  - Student's name
  - Selected passage
- **Back page**: Standard discussion questions (same for all students)

If the CSV has a `TF` column, handouts are grouped by TF and each group starts with a separator page showing the TF's name, the session number, and how many handouts are in the group. The separator has a blank back so double-sided printing stays aligned.

The pages are arranged so you can print double-sided and the handouts will be in the correct order.

## Font

All text uses Courier New (Courier) font for consistency with academic formatting.

## Examples

Generate handouts with default output name:
```bash
python generate_handouts.py students.csv back_page.pdf
```

Generate handouts with custom output name:
```bash
python generate_handouts.py my_students.csv my_back_page.pdf week3_handouts.pdf
```

Generate handouts with session number:
```bash
python generate_handouts.py students.csv back_page.pdf handouts.pdf --session 3
```

Or using the short flag:
```bash
python generate_handouts.py students.csv back_page.pdf -s 5
```

## Printing

The generated PDF is organized for duplex (double-sided) printing:
- Pages 1-2: Student 1 (front and back)
- Pages 3-4: Student 2 (front and back)
- And so on...

Configure your printer for double-sided printing with "flip on long edge" or "book-style" orientation.
