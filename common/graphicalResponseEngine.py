import os
import fitz  # PyMuPDF
from PIL import Image
import io
import easyocr
from fuzzywuzzy import fuzz
import numpy as np

DROPBOX_LOCAL_FOLDER_PATH = "./dropbox"

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])  # Add languages if needed

def extract_relevant_image_from_dropbox(question):
    """Extracts the most relevant image from PDFs stored in Dropbox."""
    
    pdf_files = [f for f in os.listdir(DROPBOX_LOCAL_FOLDER_PATH) if f.endswith(".pdf")]
    
    best_image = None
    best_match_score = 0  # Best match based on relevance

    for pdf_name in pdf_files:
        pdf_path = os.path.join(DROPBOX_LOCAL_FOLDER_PATH, pdf_name)
        pdf_document = fitz.open(pdf_path)

        for page_num in range(len(pdf_document)):
            for img_index, img in enumerate(pdf_document[page_num].get_images(full=True)):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_data = base_image["image"]
                image = Image.open(io.BytesIO(image_data))

                # Extract text from image using EasyOCR
                match_score = check_image_relevance(image, question)
                
                # Extract potential captions from PDF
                captions = extract_text_near_image(pdf_document, page_num)
                for caption in captions:
                    match_score = max(match_score, fuzz.ratio(caption.lower(), question.lower()))

                if match_score > best_match_score:
                    best_match_score = match_score
                    best_image = image

    return best_image

def check_image_relevance(image, question):
    """Returns a score based on how relevant the image is to the question."""

    # Convert PIL Image to NumPy array for EasyOCR
    image_np = np.array(image)

    # Extract text from the image using EasyOCR
    result = reader.readtext(image_np)
    
    # Join extracted text
    extracted_text = " ".join([text[1] for text in result])
    
    # Compare text with the question
    relevance_score = fuzz.ratio(extracted_text.lower(), question.lower())
    return relevance_score

def extract_text_near_image(pdf_document, page_num):
    """Extracts text near an image in a PDF page to check if it's a caption."""
    page = pdf_document[page_num]
    text_blocks = page.get_text("blocks")  # Get text blocks
    
    captions = []
    for block in text_blocks:
        x, y, w, h, text, _, _ = block  # Extract text and position
        if y > 400:  # Example heuristic: Check text near the bottom of the page
            captions.append(text)

    return captions
