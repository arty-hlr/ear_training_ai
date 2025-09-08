import logging

from PyPDF2 import PdfReader, PdfWriter

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

from markdown_to_data import Markdown

def extract_pages(file_in, file_out, start, end):
    reader = PdfReader(file_in)
    writer = PdfWriter()

    for page in reader.pages[start-1:end]:
        writer.add_page(page)

    writer.write(file_out)

# # contents
# extract_pages('manual.pdf', 'contents.pdf', 11, 13)

def extract_text(filename):
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False

    converter = DocumentConverter()
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    result = converter.convert(filename)
    return result.document.export_to_markdown()

if __name__ == "__main__":
    with open('contents.md') as f:
        contents = f.read()

    md = Markdown(contents)
    chapters,pages = md.md_dict['table_1'].values()
    contents = dict(zip(chapters,pages))

    # for chapter in range(1,len(contents.keys())):
    #     assert contents[chapter] < contents[chapter+1]

    for chapter in range(1,len(contents.keys())):
        start = contents[chapter] + 30
        end = contents[chapter+1] - 1 + 30
        extract_pages('manual.pdf', f'chapters/chapter_{chapter:02}.pdf', start, end)
        text = extract_text(f'chapters/chapter_{chapter:02}.pdf')
        with open(f'chapters/chapter_{chapter:02}.md', 'w') as f:
            f.write(text)
