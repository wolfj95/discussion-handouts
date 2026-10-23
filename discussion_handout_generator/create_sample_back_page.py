#!/usr/bin/env python3
"""
Helper script to create a sample back page PDF.
You can replace this with your actual back page PDF.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sample_back_page():
    c = canvas.Canvas("back_page.pdf", pagesize=letter)
    width, height = letter

    # Set font
    c.setFont("Courier", 12)

    # Add sample content
    c.drawString(72, height - 72, "DISCUSSION QUESTIONS")
    c.drawString(72, height - 100, "")
    c.drawString(72, height - 120, "1. What themes emerge from your selected passage?")
    c.drawString(72, height - 150, "2. How does this passage relate to the broader text?")
    c.drawString(72, height - 180, "3. What literary devices does the author employ?")
    c.drawString(72, height - 210, "4. How does this passage connect to our previous readings?")
    c.drawString(72, height - 240, "5. What questions does this passage raise?")
    c.drawString(72, height - 300, "Notes:")

    # Add lines for notes
    y = height - 330
    for i in range(15):
        c.line(72, y, width - 72, y)
        y -= 20

    c.save()
    print("Sample back_page.pdf created successfully!")

if __name__ == "__main__":
    create_sample_back_page()
