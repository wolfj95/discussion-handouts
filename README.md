# Discussion Handouts

Tools for turning students' Canvas passage submissions into printed, personalized discussion handouts for T564A: Vibe Coding.

| Directory | What it does |
|---|---|
| [`passage_aggregator/`](passage_aggregator/) | Pulls each student's passage out of their Canvas submission and writes it into the roster |
| [`discussion_handout_generator/`](discussion_handout_generator/) | Turns the roster into a single printable PDF: one two-sided handout per student, grouped by TF |

> **Student data stays out of git.** Rosters, submissions, back pages, and generated PDFs are all gitignored (FERPA). Only code, docs, and `sample_*.csv` files are committed. Run `git status` before committing to double-check.

## Setup

Requires Python 3.9+.

```bash
python3 -m venv env
source env/bin/activate
pip install -r discussion_handout_generator/requirements.txt
```

The passage aggregator uses only the standard library.

## Workflow for each session

Replace `N` with the session number throughout.

### 1. Download submissions from Canvas

In Canvas, open the passage assignment for the session and choose **Download Submissions**. Unzip the download into `passage_aggregator/passage_submissions/`, replacing any files from the previous session:

```bash
rm -rf passage_aggregator/passage_submissions
unzip ~/Downloads/submissions.zip -d passage_aggregator/passage_submissions
```

### 2. Aggregate passages into the roster

Copy the current course roster to `passage_aggregator/roster.csv`. It needs these columns:

```
Name,Preferred Name,Email Address,TF,Passage
```

`Name` is `Last,First`. The `Passage` column is filled in by the script (it's added if missing). Extra columns, such as a `Status` column, are kept. **Remove any students who have dropped the course first.** The handout generator prints a handout for every row.

Then run:

```bash
cd passage_aggregator
python extract_passages.py
```

### 3. Resolve unmatched passages

The script lists every submission it matched and writes any it couldn't match to `passage_aggregator/unmatched_passages.txt`. For each entry in that file:

1. Work out which student it belongs to from the filename (e.g. `kierajones_624180_text.html` → `Jones,Kiera`).
2. Paste the passage into that student's `Passage` cell in `roster.csv`.

Also skim the `✓ Matched:` lines in the output. Fuzzy matching can occasionally assign a passage to a student with a similar name. Students who didn't submit will have an empty `Passage`. They still get a handout, just with a blank passage section.

### 4. Move the roster to the handout generator

```bash
cp passage_aggregator/roster.csv discussion_handout_generator/students.csv
```

### 5. Create the back page for the session

The back page (discussion questions, notes space, etc.) is the same for every student. Create it as a **single-page, letter-size PDF** and save it as `discussion_handout_generator/back_page.pdf`. Only the first page of the PDF is used.

The easiest route is to write it in Google Docs or Word and export it to PDF. For a plain-text starting point, `create_sample_back_page.py` writes a basic `back_page.pdf` you can adapt by editing the questions in the script:

```bash
cd discussion_handout_generator
python create_sample_back_page.py
```

### 6. Generate the handouts

```bash
cd discussion_handout_generator
python generate_handouts.py students.csv back_page.pdf handouts-session-N.pdf -s N
```

The output PDF contains, for each TF (alphabetically):
- a **separator page** with the TF's name, the session number, and the handout count, plus a blank back;
- one **front page** (header, student name, passage) and one **back page** per student.

Print double-sided (flip on long edge). The separator pages make it easy to split the stack into each TF's handouts.

### 7. (Optional) Archive the session

Keep a copy of the session's inputs and output locally, e.g.:

```bash
mkdir -p 2026/session-N
cp students.csv back_page.pdf handouts-session-N.pdf 2026/session-N/
```

Year folders are gitignored.

See each tool's README for details: [passage aggregator](passage_aggregator/README.md) · [handout generator](discussion_handout_generator/README.md).
