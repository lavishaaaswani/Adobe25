import os
import json
import fitz  # PyMuPDF
from typing import Dict, List, Optional
import re

class PDFProcessor:
    def __init__(self):
        self.heading_profiles = {
            'H1': {
                'min_size': 17.5,
                'max_size': float('inf'),
                'weight': 'bold',
                'case': 'any',
                'min_length': 5
            },
            'H2': {
                'min_size': 18,
                'max_size': 23.9,
                'weight': 'bold',
                'case': 'title',
                'min_length': 4
            },
            'H3': {
                'min_size': 14,
                'max_size': 17.9,
                'weight': 'any',
                'case': 'any',
                'min_length': 3
            }
        }

        self.ignore_patterns = [
            r'^[\W_]+$',         # punctuation
            r'^[0-9]{1,3}$',     # short numbers
            r'^(http|www|\.com)',
            r'\b(rsvp|date|time|address):?',
            r'^\s*$'
        ]

        self.special_cases = {
            r'hope.*see.*there': 'HOPE TO SEE YOU THERE!'
        }

    def clean_text(self, text: str) -> str:
        text = text.strip()
        for pattern, replacement in self.special_cases.items():
            if re.search(pattern, text, re.IGNORECASE):
                return replacement
        text = re.sub(r'[\s\-_]+$', '', text)
        text = ' '.join(text.split())
        text = re.sub(r'(\w)\s+([.,;!?])', r'\1\2', text)
        return text

    def is_ignored_text(self, text: str) -> bool:
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.ignore_patterns)

    def get_font_properties(self, spans: List) -> Dict:
        max_size = max(span["size"] for span in spans)
        is_bold = any("bold" in span["font"].lower() for span in spans)
        color = spans[0].get("color", 0)
        return {
            'size': max_size,
            'is_bold': is_bold,
            'color': color
        }

    def determine_heading_level(self, text: str, font_props: Dict) -> Optional[str]:
        if self.is_ignored_text(text):
            return None

        text_case = 'upper' if text.isupper() else 'title' if text.istitle() else 'any'

        for level, profile in self.heading_profiles.items():
            size_ok = profile['min_size'] <= font_props['size'] <= profile['max_size']
            weight_ok = (
                profile['weight'] == 'any' or
                (profile['weight'] == 'bold' and font_props['is_bold']) or
                (profile['weight'] == 'regular' and not font_props['is_bold'])
            )
            case_ok = profile['case'] == 'any' or profile['case'] == text_case
            length_ok = len(text) >= profile['min_length']

            if size_ok and weight_ok and case_ok and length_ok:
                return level

        # ✅ Fallback rules if nothing matches above
        if 14.0 <= font_props['size'] <= 16.5 and font_props['is_bold'] and 2 <= len(text.split()) <= 5:
            return 'H2'

        if font_props['size'] >= 20 and len(text) >= 10:
            return 'H1'

        if 13.5 <= font_props['size'] <= 16.5 and len(text.split()) <= 6:
            return 'H3'

        return None

    def extract_pdf_structure(self, pdf_path: str) -> Dict:
        doc = fitz.open(pdf_path)
        result = {
            "title": "",
            "outline": []
        }

        elements = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            width, height = page.rect.width, page.rect.height

            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue

                for line in block["lines"]:
                    if not line["spans"]:
                        continue

                    line_text = "".join(span["text"] for span in line["spans"])
                    font_props = self.get_font_properties(line["spans"])
                    clean = self.clean_text(line_text)

                    if not clean:
                        continue

                    x0, x1 = line["bbox"][0], line["bbox"][2]
                    line_width = x1 - x0
                    page_margin = width * 0.15
                    is_centered = (x0 > page_margin and x1 < width - page_margin) or (line_width >= width * 0.6)

                    print(f"TEXT: {clean} | SIZE: {font_props['size']:.2f} | BOLD: {font_props['is_bold']} | PAGE: {page_num}")

                    elements.append({
                        'text': clean,
                        'props': font_props,
                        'page': page_num,
                        'bbox': line["bbox"],
                        'center_pos': is_centered
                    })

        # ✅ Title detection: centered large text near top of first page
        if elements:
            first_page_elements = [e for e in elements if e['page'] == 0]
            candidate = max(
                [e for e in first_page_elements if e['center_pos'] and e['bbox'][1] < height * 0.3],
                key=lambda x: x['props']['size'],
                default=None
            )
            if candidate and len(candidate['text']) >= 5:
                result["title"] = candidate['text']

        # ✅ Heading detection
        for elem in elements:
            level = self.determine_heading_level(elem['text'], elem['props'])
            if level:
                result["outline"].append({
                    "level": level,
                    "text": elem['text'],
                    "page": elem['page']
                })

        doc.close()
        return result


def process_pdfs(input_dir: str, output_dir: str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    processor = PDFProcessor()

    print(f"📁 Files in input dir ({input_dir}):")
    print(os.listdir(input_dir))

    for filename in os.listdir(input_dir):
        print(f"🔍 Found file: {filename}")

        if filename.lower().endswith('.pdf'):
            print(f"📄 Processing file: {filename}")
            pdf_path = os.path.join(input_dir, filename)

            try:
                output_path = os.path.join(
                    output_dir,
                    f"{os.path.splitext(filename)[0]}.json"
                )

                structure = processor.extract_pdf_structure(pdf_path)

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(structure, f, indent=2, ensure_ascii=False)

                print(f"✅ Processed: {filename}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {str(e)}")


if __name__ == "__main__":
    input_dir = "app/input"
    output_dir = "app/output"
    process_pdfs(input_dir, output_dir)
