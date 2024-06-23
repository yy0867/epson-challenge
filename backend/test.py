import pdfkit

config = pdfkit.configuration(wkhtmltopdf=r'/usr/local/bin/wkhtmltopdf')
pdfkit.from_file(
    'file_to_print.html',
    'example.pdf',
    configuration=config,
    options={"enable-local-file-access": ""}
)