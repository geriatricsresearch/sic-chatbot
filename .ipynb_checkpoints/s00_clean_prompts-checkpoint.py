
"""
s00_clean_prompts_v2.py

This script cleans and splits a .docx file containing multi-part chatbot prompt content
(intended for a serious illness communication training chatbot). It outputs the cleaned and
separated prompts into individual text files for use in a Streamlit chatbot application.

Version: V2
Author: Edie Espejo
"""

from docx import Document
import re

# -----------------------
# Function: Convert .docx to .txt
# -----------------------
def docx_to_txt(input_path, output_path):
    """
    Converts a .docx file into a plain .txt file.

    Args:
        input_path (str): Path to the .docx input file.
        output_path (str): Path to the output .txt file.
    """
    doc = Document(input_path)
    text = '\n'.join([para.text for para in doc.paragraphs])

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

# Convert raw docx prompt file to txt
docx_to_txt('prompts/SIC Chatbot Prompts 5.30_Prognosis Only.docx',
            'prompts/SIC Chatbot Prompts 5.30_Prognosis Only.txt')

# Read full text file
with open('prompts/SIC Chatbot Prompts 5.30_Prognosis Only.txt', 'r', encoding='utf-8') as file:
    full_prompt = file.read()

# Remove non-ASCII characters
full_prompt = re.sub(r'[^\x00-\x7F]+', ' ', full_prompt) 

# -----------------------
# Split into Prompt 0, 1, and 2
# -----------------------
marker0 = 'Prompt 0:'
marker1 = 'Prompt 1:'
marker2 = 'Prompt 2:'

if all(m in full_prompt for m in [marker0, marker1, marker2]):
    _, after_0 = full_prompt.split(marker0, maxsplit=1)
    prompt0, after_1 = after_0.split(marker1, maxsplit=1)
    prompt1, prompt2 = after_1.split(marker2, maxsplit=1)

    prompt0 = f'{marker0}\n{prompt0.strip()}'
    prompt1 = f'{marker1}\n{prompt1.strip()}'
    prompt2 = f'{marker2}\n{prompt2.strip()}'

    with open('prompts/prompt0_disclaimer.txt', 'w', encoding='utf-8') as f:
        f.write(prompt0)

    with open('prompts/prompt1_patient.txt', 'w', encoding='utf-8') as f:
        f.write(prompt1)

    with open('prompts/prompt2_feedback.txt', 'w', encoding='utf-8') as f:
        f.write(prompt2)

    print('All prompts split and saved successfully.')
else:
    print('One or more markers (Prompt 0/1/2) not found in full_prompt.')

# -----------------------
# Reload and apply revisions
# -----------------------

# Load prompts back
with open('prompts/prompt0_disclaimer.txt', 'r', encoding='utf-8') as f:
    prompt0 = f.read()

with open('prompts/prompt1_patient.txt', 'r', encoding='utf-8') as f:
    prompt1 = f.read()

with open('prompts/prompt2_feedback.txt', 'r', encoding='utf-8') as f:
    prompt2 = f.read()

# Revise Prompt 0 to stop after disclaimer
prompt0 = re.sub(
    'If the clinician accepts the disclaimer, then proceed to prompt 1.',
    'Stop here if the clinician accepts the disclaimer. Do not proceed to prompt 1.',
    prompt0
)

# Rewrite Prompt 1 entirely with clarified structure
prompt1 = """<INSERT CLEANED PROMPT 1 TEXT HERE>"""  # For maintainability, place long prompt text in external file or load from finalized version

# Trim Prompt 2 at optional elements section
prompt2 = prompt2.split('Elements to be incorporated at a later date:')[0]

# Add custom instruction to Prompt 2 for chatbot exit
prompt2 += ' At any point during this feedback conversation, direct the clinician that they may type "done", "exit", or "quit" to indicate they would like to end the session. When this happens, acknowledge their response warmly and professionally, and thank them again for their participation. Do not continue the conversation once they have chosen to exit. Restate at the end of the conversation that they may type "exit" to finish the conversation.'

# -----------------------
# Save finalized prompts
# -----------------------
with open("prompts/final_prompt0.txt", "w", encoding="utf-8") as f:
    f.write(prompt0)

with open("prompts/final_prompt1.txt", "w", encoding="utf-8") as f:
    f.write(prompt1)

with open("prompts/final_prompt2.txt", "w", encoding="utf-8") as f:
    f.write(prompt2)
