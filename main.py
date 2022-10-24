#!/usr/bin/env python3

"""automatic generation of pdf files with animal names specified in txt file
for study data collection

author: cb
last mod: 2022-10-24
"""

from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen.canvas import Canvas

import glob, os, io

from tqdm import tqdm

def add_name(infile, outfile, text='TEXT', page_to_merge=0, xcoor=165, ycoor=711):
    
    with open(infile, "rb") as f:
        input_pdf = PdfFileReader(f)
        page_count = input_pdf.getNumPages()

        inputpdf_page_to_be_merged = input_pdf.getPage(page_to_merge)

        packet = io.BytesIO()
        c = Canvas(packet,pagesize=(inputpdf_page_to_be_merged.mediaBox.getWidth(),inputpdf_page_to_be_merged.mediaBox.getHeight()))
        c.drawString(xcoor,ycoor,text)
        c.save()
        packet.seek(0)

        overlay_pdf = PdfFileReader(packet)
        overlay = overlay_pdf.getPage(0)

        output = PdfFileWriter()

        for PAGE in range(page_count):
            if PAGE == page_to_merge:
                inputpdf_page_to_be_merged.mergeRotatedTranslatedPage(overlay, 
                        inputpdf_page_to_be_merged.get('/Rotate') or 0, 
                        overlay.mediaBox.getWidth()/2, overlay.mediaBox.getWidth()/2)
                output.addPage(inputpdf_page_to_be_merged)
            else:
                Page_in_pdf = input_pdf.getPage(PAGE)
                output.addPage(Page_in_pdf)

        with open(outfile, "wb") as f:
            output.write(f)

        return

if __name__ == '__main__':
   
    with open('DeerLakesIds.txt') as f:
        ANIMAL_NAMES = f.read().split('\n')
        ANIMAL_NAMES.remove('') # Trailing line

    infiles = glob.glob('tutor_units_paper/*.pdf')

    for animal in tqdm(ANIMAL_NAMES):
        for f_in in infiles:
            f_out = f_in.replace('tutor_units_paper/', 'scaled_units/')
            f_out = f_out.replace('.pdf', '_'+animal+'.pdf')

            with open(f_in, "rb") as f:
                input_pdf = PdfFileReader(f)
                page_count = input_pdf.getNumPages()

            # cb: hacky way of pushing versions of the pdfs forward, could improve this but no time for now
            for count, page in enumerate(range(page_count)):
                if count == 0: # first
                    add_name(f_in, f_out+str(count), text=animal, page_to_merge=page, xcoor=165, ycoor=711)
                elif count == page_count-1: # last
                    add_name(f_out+str(count-1), f_out, text=animal, page_to_merge=page, xcoor=165, ycoor=711)
                else:
                    add_name(f_out+str(count-1), f_out+str(count), text=animal, page_to_merge=page, xcoor=165, ycoor=711)
    
    # clean up: remove all files in scaled_units that do not end in '.pdf'
    outfiles = glob.glob('scaled_units/*')
    for f in outfiles:
        if f[-1] in [str(i) for i in range(10)]:
            if os.path.isfile(f):
                os.remove(f)

# pdfunite scaled_units/*.pdf all_named_units.pdf
