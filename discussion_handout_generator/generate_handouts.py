#!/usr/bin/env python3
"""
Generate personalized handouts for students.
Each handout has a custom front page with the student's name and passage,
and a standard back page.
"""

import csv
import sys
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT
from pypdf import PdfReader, PdfWriter


def format_name(name):
    """
    Format a student name. If the name is in "Last,First" format,
    convert it to "First Last" format.

    Args:
        name: The student name string

    Returns:
        Formatted name string
    """
    if not name:
        return name

    # Check if name contains a comma (Last,First format)
    if ',' in name:
        parts = name.split(',', 1)  # Split only on first comma
        if len(parts) == 2:
            last_name = parts[0].strip()
            first_name = parts[1].strip()
            return f"{first_name} {last_name}"

    # If no comma, return name as-is
    return name


def create_front_page(student_name, passage, session_number=None):
    """
    Create a front page PDF for a student with their name and passage.
    Returns a BytesIO object containing the PDF.

    Args:
        student_name: Name of the student
        passage: Selected passage text
        session_number: Optional session number for the header
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Set margins
    margin_left = 72  # 1 inch
    margin_right = width - 72
    margin_top = height - 72

    # Draw header
    c.setFont("Courier-Oblique", 12)

    # Left aligned: Course name
    c.drawString(margin_left, margin_top + 20, "T564A: Vibe Coding")

    # Right aligned: Discussion Handout | Session X
    if session_number:
        header_right = f"Discussion Handout | Session {session_number}"
    else:
        header_right = "Discussion Handout"

    # Calculate x position for right-aligned text
    text_width = c.stringWidth(header_right, "Courier-Oblique", 12)
    c.drawString(margin_right - text_width, margin_top + 20, header_right)

    # Draw line under header
    c.line(margin_left, margin_top + 10, margin_right, margin_top + 10)

    # Draw student name
    c.setFont("Courier-Bold", 14)
    c.drawString(margin_left, margin_top - 10, student_name)

    # Draw a line under the name
    c.line(margin_left, margin_top - 20, margin_right, margin_top - 20)

    # Draw "Selected Passage" heading
    c.setFont("Courier-Bold", 12)
    c.drawString(margin_left, margin_top - 50, "Selected Passage:")

    # Draw the passage using Paragraph for text wrapping
    style = ParagraphStyle(
        'CustomCourier',
        fontName='Courier',
        fontSize=11,
        leading=16,
        alignment=TA_LEFT,
        leftIndent=0,
        rightIndent=0,
    )

    # Create paragraph with the passage
    para = Paragraph(passage, style)

    # Calculate available width and height for the paragraph
    available_width = margin_right - margin_left
    available_height = margin_top - 180  # Leave space at bottom and for header

    # Wrap and draw the paragraph
    w, h = para.wrap(available_width, available_height)
    para.drawOn(c, margin_left, margin_top - 80 - h)

    c.save()
    buffer.seek(0)
    return buffer


def create_tf_separator_page(tf_name, student_count, session_number=None):
    """
    Create a separator page that marks the start of a TF's section of handouts.
    Returns a BytesIO object containing a two-page PDF (separator + blank back),
    so that duplex printing stays aligned.

    Args:
        tf_name: Name of the TF for this section
        student_count: Number of handouts in this section
        session_number: Optional session number to display
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # TF name, large and centered
    c.setFont("Courier-Bold", 48)
    c.drawCentredString(width / 2, height / 2 + 20, tf_name)

    # Supporting details underneath
    c.setFont("Courier", 16)
    if session_number:
        c.drawCentredString(width / 2, height / 2 - 30, f"Session {session_number}")
    c.drawCentredString(width / 2, height / 2 - 55, f"{student_count} handouts")

    c.showPage()

    # Blank back page so the next handout starts on a new sheet
    c.showPage()

    c.save()
    buffer.seek(0)
    return buffer


def generate_handouts(csv_file, back_page_pdf, output_file, session_number=None):
    """
    Generate a PDF with all student handouts.

    Args:
        csv_file: Path to CSV file with columns 'name' and 'passage'
        back_page_pdf: Path to the standard back page PDF
        output_file: Path for the output PDF file
        session_number: Optional session number for the header
    """
    # Read the back page PDF into memory
    try:
        with open(back_page_pdf, 'rb') as f:
            back_page_data = f.read()
        back_page_buffer = BytesIO(back_page_data)
        back_page_reader = PdfReader(back_page_buffer)
    except FileNotFoundError:
        print(f"Error: Back page PDF '{back_page_pdf}' not found.")
        print("Please ensure the back page PDF exists.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading back page PDF: {e}")
        sys.exit(1)

    # Create PDF writer for the output
    writer = PdfWriter()

    # Read student data from CSV
    try:
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            # Validate CSV has required columns
            if 'Name' not in reader.fieldnames or 'Passage' not in reader.fieldnames:
                print("Error: CSV must have 'Name' and 'Passage' columns")
                sys.exit(1)

            # Read all students into a list first
            students = []
            for row in reader:
                name = row['Name'].strip() if row['Name'] else ""
                passage = row['Passage'].strip() if row['Passage'] else ""

                if not name:
                    print(f"Warning: Skipping row with empty name")
                    continue

                # Check if there's a preferred name, otherwise use the regular name
                if 'Preferred Name' in reader.fieldnames and row['Preferred Name']:
                    preferred_name = row['Preferred Name'].strip()
                    if preferred_name:
                        name = preferred_name

                # Get TF group if available
                tf_group = ""
                if 'TF' in reader.fieldnames and row['TF']:
                    tf_group = row['TF'].strip()

                students.append({
                    'name': name,
                    'passage': passage,
                    'tf_group': tf_group
                })

            if not students:
                print("Error: No valid student entries found in CSV")
                sys.exit(1)

            # Sort students by TF group
            students.sort(key=lambda s: s['tf_group'])

            # Count handouts per TF for the separator pages
            tf_counts = {}
            for student in students:
                tf_counts[student['tf_group']] = tf_counts.get(student['tf_group'], 0) + 1

            # Generate handouts in sorted order
            student_count = 0
            current_tf = None
            for student in students:
                # Add a separator page and print section header when TF changes
                if student['tf_group'] != current_tf:
                    current_tf = student['tf_group']
                    tf_label = current_tf if current_tf else 'No TF assigned'
                    print(f"\n--- TF: {tf_label} ---")

                    separator_buffer = create_tf_separator_page(
                        tf_label, tf_counts[current_tf], session_number
                    )
                    for page in PdfReader(separator_buffer).pages:
                        writer.add_page(page)

                # Format the name (convert Last,First to First Last)
                formatted_name = format_name(student['name'])

                # Create front page (passage can be empty)
                if not student['passage']:
                    print(f"Note: Creating handout for {formatted_name} with no passage")
                front_page_buffer = create_front_page(formatted_name, student['passage'], session_number)
                front_page_reader = PdfReader(front_page_buffer)

                # Add front page to output
                writer.add_page(front_page_reader.pages[0])

                # Add back page to output - clone from the original reader
                writer.add_page(back_page_reader.pages[0])

                student_count += 1
                print(f"Added handout for: {formatted_name}")

            if student_count == 0:
                print("Error: No valid student entries found in CSV")
                sys.exit(1)

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)

    # Write output PDF
    try:
        with open(output_file, 'wb') as f:
            writer.write(f)
        print(f"\nSuccess! Generated handouts for {student_count} students.")
        print(f"Output saved to: {output_file}")
    except Exception as e:
        print(f"Error writing output PDF: {e}")
        sys.exit(1)


def main():
    """Main function to handle command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate personalized student handouts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python generate_handouts.py students.csv back_page.pdf handouts.pdf
  python generate_handouts.py students.csv back_page.pdf --session 3
  python generate_handouts.py students.csv back_page.pdf handouts.pdf -s 5
        """
    )

    parser.add_argument(
        'csv_file',
        help='CSV file with student names and passages (columns: name, passage)'
    )
    parser.add_argument(
        'back_page_pdf',
        help='PDF file for the standard back page'
    )
    parser.add_argument(
        'output_file',
        nargs='?',
        default='handouts.pdf',
        help='Output PDF file (default: handouts.pdf)'
    )
    parser.add_argument(
        '-s', '--session',
        type=str,
        dest='session_number',
        help='Session number to display in header (e.g., "3" or "3A")'
    )

    args = parser.parse_args()

    generate_handouts(args.csv_file, args.back_page_pdf, args.output_file, args.session_number)


if __name__ == '__main__':
    main()
