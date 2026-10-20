"""Split the collection into one-page PDFs, then package them as a ZIP."""
from pathlib import Path
import re
import unicodedata
import zipfile
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'output/pdf'
DEST = OUTPUT / 'Modul_8_separata_blad'
DEST.mkdir(parents=True, exist_ok=True)
source = PdfReader(OUTPUT / 'Modul_8_studieblad.pdf')
assert len(source.pages) == 36, 'Expected 31 worksheets and five answer pages.'
written = []
for index, page in enumerate(source.pages):
    text = page.extract_text()
    if index < 31:
        section = re.search(r'/\s+(\d\.\d)', text).group(1)
        title = next(line for line in text.splitlines()
                     if line.strip() and not line.startswith(('MODUL', 'Namn')))
        slug = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode().lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
        name = f'{section}_{slug}.pdf'
    else:
        name = f'Facit_kapitel_{index - 30}.pdf'
    target = DEST / name
    writer = PdfWriter()
    writer.add_page(page)
    with target.open('wb') as stream:
        writer.write(stream)
    assert len(PdfReader(target).pages) == 1
    written.append(target)
with zipfile.ZipFile(OUTPUT / 'Modul_8_separata_blad.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for target in sorted(written):
        archive.write(target, f'{DEST.name}/{target.name}')
print(f'Created {len(written)} separate PDFs and ZIP.')
