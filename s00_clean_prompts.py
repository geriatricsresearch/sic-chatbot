# Prompts ----

## Convert to text files ----
from docx import Document
import re

## Function
def docx_to_txt(input_path, output_path):
    doc = Document(input_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

## Write to text file
docx_to_txt('prompts/SIC Chatbot Prompts 5.29_Prognosis Only.docx',
            'prompts/SIC Chatbot Prompts 5.29_Prognosis Only.txt')

## Save full prompt
with open('prompts/SIC Chatbot Prompts 5.29_Prognosis Only.txt', 'r', encoding='utf-8') as file:
    full_prompt = file.read()
full_prompt = re.sub(r'[^\x00-\x7F]+', ' ', full_prompt) 


## Separate files ----
split_marker = 'Prompt 2:'
parts = full_prompt.split(split_marker, maxsplit=1)

if len(parts) == 2:
    prompt1 = parts[0].strip()
    prompt2 = 'Prompt 2:\n' + parts[1].strip()  # Add header back for clarity

    # Save both to separate files
    with open('prompts/prompt1_patient.txt', 'w', encoding='utf-8') as f:
        f.write(prompt1)

    with open('prompts/prompt2_feedback.txt', 'w', encoding='utf-8') as f:
        f.write(prompt2)

    print('Prompts split and saved successfully.')
else:
    print('Could not find the marker *Prompt 2:* in the file.')
    
## Save
with open('prompts/prompt1_patient.txt', 'r', encoding='utf-8') as f:
    prompt1 = f.read()

with open('prompts/prompt2_feedback.txt', 'r', encoding='utf-8') as f:
    prompt2 = f.read()
    
## Prompt 1 ----
prompt1_removal = '''
Before the conversation starts, please ask the clinician to provide the following details
Patient and/or love one s (s): 
Clinical context: 
Psychosocial context: 
Cultural/ethical context: 
Should the simulated patient act as the patient, loved one(s), or both?
What challenge(s) do you anticipate during this conversation?
'''

prompt1_cleaned = prompt1.replace(prompt1_removal, '')

prompt1_cleaned = prompt1.replace('After you confirm understanding, wait for the clinician to type  begin encounter  to start the conversation.', 'After you confirm understanding, tell the clinician that they may start the conversation by speaking directly to the patient or their loved one depending on the scenario. Please say *Starting encounter* to show the encounter is starting. When it ends please state *Ending encounter* When ending encounter, let user know they need to type "feedback" or "end encounter" to move on. "When speaking as more than one person, clearly label who is speaking before each line."')

## Prompt 2 ----
prompt2_cleaned = prompt2.split('Elements to be incorporated at a later date:')[0]
prompt2_cleaned = prompt2_cleaned + 'We will evalute the following transcript: '

## Prompt 0 ----
prompt0 = '''
You are the gatekeeper assistant for a serious illness communication training chatbot. Your role is to guide the user through a three-step confirmation process before starting the simulation. You must not begin the simulation until all three steps are completed.

Steps: (You do NOT need to print each step out before asking questions!)

Step 1:
Ask: "Would you like to simulate a patient encounter?"
If the user gives a clear yes, say "Got it." and proceed to Step 2.

Step 2:
Say: "Warning:
This chatbot is intended for educational use only. It is designed to simulate serious illness conversations to help clinicians practice communication skills in a safe, role-played environment.

Do not share real patient information. Please avoid entering any protected health information (PHI), including names, medical record numbers, dates of birth, addresses, or any details that could identify a real person.

By continuing, you acknowledge that all scenarios used in this simulation are fictional, and you agree to participate using hypothetical or de-identified case examples only."
Ask: "Do you acknowledge and accept this warning before we proceed?"
If the user gives a clear yes, say "Thank you for confirming." and proceed to Step 3.

Step 3:
Say: "You can now describe a hypothetical patient scenario you would like to simulate, or I can provide one for you."
Ask: "Would you like to describe the patient, or should I choose for you?"

If a user decides to describe the patient, ask about the following:
''' + prompt1_removal + '''

If a user says to choose for them, then provide that information for them. Do not ask them to provide information.

- If the user describes a case, acknowledge it.
- If the user says something like "you choose" or "choose one for me", you must generate a realistic example of a patient with a serious illness.
    - Provide the description of the patient you have generated. Describe illness, support, characteristics needed for doctor.

In the last message, say "You are ready to begin the simulation."
Then, describe the scenario whether it was user-generated or created by AI.

Then stop responding.
'''

## Save all ----
with open("prompts/final_prompt0.txt", "w", encoding="utf-8") as f:
    f.write(prompt0)

with open("prompts/final_prompt1.txt", "w", encoding="utf-8") as f:
    f.write(prompt1_cleaned)

with open("prompts/final_prompt2.txt", "w", encoding="utf-8") as f:
    f.write(prompt2_cleaned)