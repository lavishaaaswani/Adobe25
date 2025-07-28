# PDF Structure Extractor

This project processes PDF files to extract their structural information, such as the document title and an outline of headings, and outputs the results in JSON format. It is designed for batch processing of PDFs, making it useful for document analysis, archiving, or content indexing.

## Features
- **Automatic Title Detection**: Identifies the main title from the first page of the PDF.
- **Heading Extraction**: Detects headings (H1, H2, H3) based on font size, weight, and position.
- **Batch Processing**: Processes all PDF files in a specified input directory.
- **JSON Output**: Outputs structured data for each PDF, including title and outline.
- **Docker Support**: Easily run the project in a containerized environment.

## Requirements
- Python 3.9+
- [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Prepare Input Files
Place your PDF files in the `app/input/` directory (or the directory you specify).

### 2. Run the Script
```bash
python main.py
```
By default, the script processes PDFs from `/app/input` and writes JSON files to `/app/output`.

### 3. Output
For each PDF, a corresponding `.json` file is created in the output directory. Example:

**Input:** `app/input/file02.pdf`

**Output:** `app/output/file02.json`
```json
{
  "title": "Overview",
  "outline": [
    { "level": "H3", "text": "Revision History", "page": 2 },
    { "level": "H3", "text": "Table of Contents", "page": 3 },
    { "level": "H3", "text": "Acknowledgements", "page": 4 }
    // ...
  ]
}
```

## Running with Docker

1. **Build the Docker image:**
   ```bash
   docker build -t pdf-structure-extractor .
   ```
2. **Run the container:**
   ```bash
   docker run --rm -v $(pwd)/app/input:/app/input -v $(pwd)/app/output:/app/output pdf-structure-extractor
   ```
   This mounts your local `app/input` and `app/output` directories into the container.

## Customization
- **Input/Output Paths:**
  - Change the `input_dir` and `output_dir` variables in `main.py` if you want to use different folders.
- **Heading Detection:**
  - The logic for heading detection can be customized in the `PDFProcessor` class in `main.py`.

## File Structure
```
app/
  input/    # Place your PDF files here
  output/   # JSON output files will be saved here
main.py     # Main processing script
Dockerfile  # For containerized execution
requirements.txt
README.md
```

## License
MIT License (add your license if different)
