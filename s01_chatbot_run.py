# Mga Aklatan ----    
import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

import textwrap
from datetime import datetime
import re

# Oras ----
def timestamp():
    return datetime.now().strftime("%I:%M %p")

## Ang aking API Info ----
# from dotenv import load_dotenv
# load_dotenv()
import os
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]


# Initialize Session ----
if "prompt0_done" not in st.session_state:
    st.session_state.prompt0_done = False
if "scenario" not in st.session_state:
    st.session_state.scenario = ""
if "sim_messages" not in st.session_state:
    st.session_state.sim_messages = []
if "prompt1_done" not in st.session_state:
    st.session_state.prompt1_done = False
if "messages" not in st.session_state:
    # Load prompt0 from file
    with open("prompts/final_prompt0.txt", "r", encoding="utf-8") as f:
        prompt0 = f.read()
    st.session_state.messages = [SystemMessage(content=prompt0)]
    # Automatically trigger first assistant message
    llm_prompt0 = ChatOpenAI(model='gpt-4o', temperature=0.1)
    first_response = llm_prompt0.invoke(st.session_state.messages)
    st.session_state.messages.append(first_response)


# Streamlit page
st.set_page_config(page_title="SIC Chatbot")
st.title("Serious Illness Communication Chatbot")


# Show conversation history
st.subheader("🔹 Getting Started")
for msg in st.session_state.messages:
    if isinstance(msg, AIMessage):
        st.chat_message("assistant").markdown(msg.content)
    elif isinstance(msg, HumanMessage):
        st.chat_message("user").markdown(msg.content)

# Begin Prompt 0 Conversation
if not st.session_state.prompt0_done:
    user_input = st.chat_input("You:")
    if user_input:
        st.session_state.messages.append(HumanMessage(content=user_input))
        llm_prompt0 = ChatOpenAI(model='gpt-4o', temperature=0.1)
        response = llm_prompt0.invoke(st.session_state.messages)
        st.session_state.messages.append(response)

        # Transition to Prompt 1 if setup is complete
        if "ready to begin the simulation" in response.content.lower():
            st.session_state.prompt0_done = True
            st.session_state.scenario = response.content

        st.rerun()


# Prompt 1 logic starts only after Prompt 0 is done
if st.session_state.prompt0_done and not st.session_state.prompt1_done:
    # Load prompt1 from file
    with open("prompts/final_prompt1.txt", "r", encoding="utf-8") as f:
        prompt1 = f.read()

    # Initialize LLM
    llm_prompt1 = ChatOpenAI(model='gpt-4o', temperature=0.2)

    # Initialize Prompt 1 session messages
    cleaned_scenario = re.sub(r"You are ready to begin the simulation\.\s*", "", st.session_state.scenario)

    
    if not st.session_state.sim_messages:
        st.session_state.sim_messages = [
            SystemMessage(content=prompt1),
            HumanMessage(content="We have the following scenario:\n\n" + '"' + cleaned_scenario + '"')
        ]
        # GPT's first response to the scenario
        first_response = llm_prompt1.invoke(st.session_state.sim_messages)
        st.session_state.sim_messages.append(first_response)

    # Display conversation
    st.subheader("🗣️ Simulated Patient Encounter")
    for msg in st.session_state.sim_messages:
        if isinstance(msg, AIMessage):
            st.chat_message("assistant").markdown(msg.content)
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").markdown(msg.content)

    # Chat input for simulation
    user_input = st.chat_input("You (Doctor):", key="prompt1_input")
    if user_input:
        if user_input.lower() in ["quit", "exit", "end encounter"]:
            st.session_state.prompt1_done = True
            st.success("✅ Encounter ended. Moving to feedback (Prompt 2)...")
            st.rerun()
        else:
            st.session_state.sim_messages.append(HumanMessage(content=user_input))
            response = llm_prompt1.invoke(st.session_state.sim_messages)
            st.session_state.sim_messages.append(response)
            st.rerun()
            
# Prompt 2 Feedback Loop ----
if st.session_state.prompt1_done:
    st.subheader("📝 Feedback")

    # Load prompt2 template from file
    with open("prompts/final_prompt2.txt", "r", encoding="utf-8") as f:
        prompt2_template = f.read()

    # Create transcript from sim_messages
    transcript = ""
    for msg in st.session_state.sim_messages:
        if isinstance(msg, HumanMessage):
            transcript += f"You (Doctor): {msg.content}\n"
        elif isinstance(msg, AIMessage):
            transcript += f"Patient: {msg.content}\n"

    # Fill in transcript into prompt2 template
    filled_prompt2 = prompt2_template.replace("{transcript}", transcript)

    # Initialize LLM
    llm_prompt2 = ChatOpenAI(model='gpt-4o', temperature=0.2)

    # Only generate feedback once
    if "feedback_response" not in st.session_state:
        response = llm_prompt2.invoke([SystemMessage(content=filled_prompt2)])
        st.session_state.feedback_response = response

    # Show feedback only (no HumanMessage)
    st.chat_message("assistant").markdown(st.session_state.feedback_response.content)

    # Optional: Allow user to follow up with feedback input
    user_input = st.chat_input("You (follow-up):", key="feedback_input")
    if user_input:
        if user_input.lower() in ["done", "exit", "quit", "end"]:
            final_request = HumanMessage(
                content="Based on the conversation transcript below, say a brief and natural final message to the doctor as the patient is ending the conversation.\n\nTranscript:\n" + transcript
            )
            final_response = llm_prompt2.invoke([final_request])
            st.chat_message("assistant").markdown(final_response.content)
        else:
            followup = HumanMessage(content=user_input)
            followup_response = llm_prompt2.invoke([
                SystemMessage(content="You are continuing a feedback conversation. The previous feedback given to the doctor was:\n\n"
                              + st.session_state.feedback_response.content +
                              "\n\nNow respond to the following follow-up question from the doctor:"),
            followup
            ])
            st.chat_message("assistant").markdown(followup_response.content)

            