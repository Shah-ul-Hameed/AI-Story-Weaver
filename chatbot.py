import openai
import os
from PIL import Image
from io import BytesIO
import requests
from dotenv import load_dotenv
import streamlit as st
from fpdf import FPDF

# Load environment variables from .env file
load_dotenv()

# Retrieve the OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_poem_or_story(theme, element=None):
    prompt = f"Write a short, imaginative, and engaging {'poem' if element is None else 'story'} for children about {theme}."
    if element:
        prompt += f" Include a {element} in the story."
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].text.strip()

def generate_image_from_text(text):
    response = openai.Image.create(
        prompt=text,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    image_response = requests.get(image_url)
    image = Image.open(BytesIO(image_response.content))
    image_path = "generated_image.png"
    image.save(image_path)
    return image_path

def save_to_pdf(poem_or_story, image_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_fill_color(245, 245, 220)
    pdf.multi_cell(0, 10, poem_or_story)
    
    # Add image to PDF
    if image_path:
        pdf.add_page()
        pdf.image(image_path, x=10, y=10, w=180)  # Adjust dimensions as needed
    
    pdf_filename = "generated_poem_or_story.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

def main():
    st.title("Children's Poem & Story Generator")
    
    theme = st.text_input("Enter a theme or topic (e.g., 'a magical forest'):")
    element = st.text_input("Enter a specific element to include (optional, e.g., 'boy', 'girl', 'school', 'park'):")
    
    if st.button("Generate Poem/Story"):
        if theme:
            text = generate_poem_or_story(theme, element)
            st.subheader("Generated Poem/Story:")
            st.write(text)
            
            # Generate Image
            image_path = generate_image_from_text(text)
            st.subheader("Generated Image:")
            st.image(image_path, caption="Generated Illustration", use_container_width=True)
            
            # Save to PDF with Image
            pdf_filename = save_to_pdf(text, image_path)
            with open(pdf_filename, "rb") as pdf_file:
                st.download_button(
                    label="Download as PDF",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
        else:
            st.warning("Please enter a theme to generate content.")

if __name__ == "__main__":
    main()