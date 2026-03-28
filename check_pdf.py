import PyPDF2

def print_pdf(f):
    reader = PyPDF2.PdfReader(f)
    print("FILE:", f)
    try:
        print(reader.pages[0].extract_text()[:400])
    except:
        pass
    print("="*40)

print_pdf('c:/Users/singh/Desktop/Important Stuff/Essentials/Resume PD Format.pdf.pdf')
print_pdf('c:/Users/singh/Desktop/Important Stuff/Essentials/CRC Resume Divyansh Singh.pdf.pdf')
