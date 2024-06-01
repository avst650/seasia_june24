import streamlit as st
import PyPDF2

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)
    text = ""

    for page in range(num_pages):
        page_obj = pdf_reader.pages[page]
        text += page_obj.extract_text()

    return text

def main():
    st.title("PDF Text Extractor")

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
        st.header("Extracted Text:")
        st.text(text)

if __name__ == "__main__":
    main()




