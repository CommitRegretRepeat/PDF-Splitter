from pathlib import Path
import csv
from pypdf import PdfReader, PdfWriter


def prompt_path(prompt: str) -> Path:
    p = Path(input(prompt).strip().strip('"').strip("'"))
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    return p


def prompt_output_dir(prompt: str) -> Path:
    """
    Prompts for an output directory path.
    Creates it if it doesn't exist.
    """
    p = Path(input(prompt).strip().strip('"').strip("'"))
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)
    if not p.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {p}")
    return p


def read_ranges_csv(csv_path: Path):
    """
    Reads a CSV where:
      - col 0 = start_page (1-based)
      - col 1 = end_page   (1-based)
      - col 2 = output filename (with or without .pdf)

    Skips blank rows. If the first row looks like a header, it is skipped.
    Returns list of tuples: (start_page:int, end_page:int, output_file:str)
    """
    encodings_to_try = ("utf-8-sig", "utf-8", "cp1252")

    last_err = None
    for enc in encodings_to_try:
        try:
            with csv_path.open(newline="", encoding=enc) as f:
                reader = csv.reader(f)

                rows = []
                for r_idx, row in enumerate(reader, start=1):
                    # Skip completely empty rows
                    if not row or all(not (c or "").strip() for c in row):
                        continue

                    # Need at least 3 columns
                    if len(row) < 3:
                        raise ValueError(
                            f"CSV row {r_idx}: expected 3 columns (start, stop, filename), got {len(row)}: {row}"
                        )

                    c0 = (row[0] or "").strip()
                    c1 = (row[1] or "").strip()
                    c2 = (row[2] or "").strip()

                    # Skip header if present
                    if r_idx == 1:
                        header_tokens = {c0.lower(), c1.lower(), c2.lower()}
                        if (
                            "start" in c0.lower()
                            or "stop" in c1.lower()
                            or "filename" in c2.lower()
                            or header_tokens.issuperset({"start", "stop", "filename"})
                        ):
                            continue

                    try:
                        start_page = int(c0)
                        end_page = int(c1)
                    except ValueError:
                        raise ValueError(
                            f"CSV row {r_idx}: start/stop must be integers (1-based). Got: {c0!r}, {c1!r}"
                        )

                    if not c2:
                        raise ValueError(f"CSV row {r_idx}: filename column (col 2) is blank.")

                    rows.append((start_page, end_page, c2))

                return rows

        except UnicodeDecodeError as e:
            last_err = e
            continue

    raise last_err if last_err else RuntimeError("Failed to read CSV (unknown error).")

def print_startup_instructions():
    print("\n" + "=" * 60)
    print("PDF Splitter - CSV Page Range Tool")
    print("=" * 60)
    print("\nThis program splits a master PDF into multiple PDFs")
    print("based on page ranges defined in a CSV file.\n")

    print("CSV FORMAT REQUIREMENTS:")
    print("--------------------------------------------------")
    print("Column 1: start_page  (1-based integer)")
    print("Column 2: end_page    (1-based integer)")
    print("Column 3: output_filename (with or without .pdf)")
    print("\nExample CSV:")
    print("start,stop,filename")
    print("1,5,Introduction")
    print("6,10,Chapter1.pdf")
    print("11,20,Appendix")
    print("\nNotes:")
    print("- Pages are 1-based (first page = 1)")
    print("- start_page must be <= end_page")
    print("- Blank rows are ignored")
    print("- A header row is allowed")
    print("- Files will be saved into a new folder")
    print("  named after the master PDF")
    print("\n" + "=" * 60 + "\n")

def main():
    print_startup_instructions()

    master_pdf = prompt_path("Enter filepath of tech submittal: ")
    ranges_csv = prompt_path("Enter ranges CSV filepath: ")
    base_output_dir = prompt_output_dir("Enter base output directory path: ")

    # Create a subfolder named after the master PDF (without extension)
    master_name = master_pdf.stem
    out_dir = base_output_dir / master_name

    # Create folder (safe if already exists)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output folder: {out_dir}")

    reader = PdfReader(str(master_pdf))
    total_pages = len(reader.pages)

    ranges = read_ranges_csv(ranges_csv)

    for i, (start_page, end_page, output_file) in enumerate(ranges, start=1):
        # Sanity checks
        if start_page < 1 or end_page < 1:
            raise ValueError(f"Row {i}: pages must be >= 1 (got {start_page}-{end_page})")
        if end_page < start_page:
            raise ValueError(f"Row {i}: end_page < start_page ({start_page}-{end_page})")
        if end_page > total_pages:
            raise ValueError(
                f"Row {i}: end_page {end_page} exceeds total pages {total_pages}"
            )

        # Ensure .pdf suffix
        output_file = output_file.strip()
        if not output_file.lower().endswith(".pdf"):
            output_file += ".pdf"

        writer = PdfWriter()

        # CSV uses 1-based pages, pypdf uses 0-based indices
        for p in range(start_page - 1, end_page):
            writer.add_page(reader.pages[p])

        out_path = out_dir / output_file

        # Avoid overwriting
        counter = 1
        original_stem = Path(output_file).stem
        while out_path.exists():
            out_path = out_dir / f"{original_stem}_{counter}.pdf"
            counter += 1

        with out_path.open("wb") as out_f:
            writer.write(out_f)

        print(f"[OK] {out_path} (pages {start_page}-{end_page})")

    print("Done.")

if __name__ == "__main__":
    main()
