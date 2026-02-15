# PDF Page Range Splitter

A Python utility that splits a master PDF into multiple smaller PDF files based on page ranges defined in a CSV file.

The script reads a CSV file containing start/end page numbers and output filenames, then generates individual PDF files for each specified range.

---

## Features

- Splits a master PDF into multiple PDFs  
- Reads page ranges from a CSV file  
- Supports optional header rows  
- Skips blank rows automatically  
- Automatically creates an output folder named after the master PDF  
- Prevents overwriting by appending numeric suffixes when needed  
- Handles common CSV encodings:
  - `utf-8-sig`
  - `utf-8`
  - `cp1252`

---

## Author

This tool was designed and developed by Jai Banala.
All credit for authorship and implementation belongs to the creator.