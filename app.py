from flask import Flask, request, jsonify, render_template
from transformers import T5Tokenizer, T5ForConditionalGeneration
import os
import fitz  # PyMuPDF for PDFs
from docx import Document  # python-docx for DOCX files

app = Flask(__name__)

# Initialize the T5 model and tokenizer
model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)
model = T5ForConditionalGeneration.from_pretrained(model_name)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    input_text = request.form.get('text', '')  # Get text input, fallback to empty string if none
    length = request.form['length']
    style = request.form['style']

    # If no text is provided, try to read from the uploaded file
    if not input_text and 'fileUpload' in request.files:
        file = request.files['fileUpload']
        if file:
            input_text = extract_text_from_file(file)

    if not input_text:
        return jsonify({'summary': 'No input text provided.'}), 400

    summary = summarize_text(input_text, length, style)
    return jsonify({'summary': summary})

def extract_text_from_file(file):
    # Extract text based on file type
    if file.filename.endswith('.pdf'):
        text = extract_text_from_pdf(file)
    elif file.filename.endswith('.docx'):
        text = extract_text_from_docx(file)
    elif file.filename.endswith('.txt'):
        text = file.read().decode('utf-8')  # Read text files directly
    else:
        return "Unsupported file format."
    
    return text

def extract_text_from_pdf(file):
    # Use PyMuPDF to extract text from PDF
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in pdf_document:
        text += page.get_text()  # Extract text from each page
    return text

def extract_text_from_docx(file):
    # Use python-docx to extract text from DOCX
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])  # Get text from all paragraphs
    return text

def summarize_text(input_text, length, style):
    input_text = f"summarize: {input_text}"
    if length == 'long':
        max_len = 200  # Increased max length for long summaries
        min_len = 100  # Ensure a minimum length
    else:
        max_len = 60  # Short summary length
        min_len = 30

    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(
        input_ids, 
        max_length=max_len, 
        min_length=min_len, 
        length_penalty=2.0, 
        num_beams=4, 
        early_stopping=False if length == 'long' else True  # Different early stopping behavior
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    # Apply bullet point formatting if requested
    if style == 'bullet':
        summary = format_bullet_points(summary)

    return summary

def format_bullet_points(text):
    # Split sentences into bullet points
    sentences = text.split('. ')
    bullet_points = '\n- '.join(sentence.strip() for sentence in sentences if sentence).strip()
    return f"- {bullet_points}"

if __name__ == '__main__':
    app.run(debug=True)
