import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# --- Setup ---
st.set_page_config(page_title="SIC Chatbot")
st.title("💬 Serious Illness Communication Chatbot")

# --- Load OpenAI API key ---
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# --- Load prompt from file ---
def load_prompt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

prompt0_text = load_prompt("prompts/final_prompt0.txt")
prompt1_text = load_prompt("prompts/final_prompt1.txt")
prompt2_text = load_prompt("prompts/final_prompt2.txt")

# --- Classifier system message ---
disclaimer_classifier = SystemMessage(content="""
You are a binary classifier that checks whether a user's message shows acceptance of a disclaimer.

You will receive a single message. Respond with:
[ACCEPTED] – if the user agrees, confirms, or gives informal consent (e.g., "yes", "sure", "okay", "yup", "let’s do it", "certainly", "ok", "absolutely", "of course").
[NOT ACCEPTED] – if they hesitate, ask questions, say "no", or avoid agreement.

Respond ONLY with [ACCEPTED] or [NOT ACCEPTED].
""")
disclaimer_llm = ChatOpenAI(model="gpt-3.5-turbo")

# --- Session state init ---
if "messages0" not in st.session_state:
    st.session_state.messages0 = [SystemMessage(content=prompt0_text)]
    st.session_state.prompt0_initialized = False
    st.session_state.prompt0_done = False
    st.session_state.disclaimer_shown = False
    st.session_state.waiting_for_ack = False

if "messages1" not in st.session_state:
    st.session_state.messages1 = [SystemMessage(content=prompt1_text)]
    st.session_state.prompt1_active = False
    st.session_state.prompt1_done = False
    st.session_state.awaiting_feedback_prompt = False
    st.session_state.feedback_given = False

if "messages2" not in st.session_state:
    st.session_state.messages2 = []
    st.session_state.prompt2_active = False
    st.session_state.prompt2_initialized = False

# === PROMPT 0 ===
if not st.session_state.prompt0_done:
    if not st.session_state.prompt0_initialized:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        first_response = llm.invoke(st.session_state.messages0)
        st.session_state.messages0.append(first_response)
        st.session_state.prompt0_initialized = True
        st.rerun()

    for msg in st.session_state.messages0:
        if isinstance(msg, AIMessage):
            st.chat_message("assistant").markdown(msg.content)
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").markdown(msg.content)

    user_input = st.chat_input("You:", key="prompt0_input")
    if user_input:
        st.session_state.messages0.append(HumanMessage(content=user_input))

        if st.session_state.waiting_for_ack:
            result = disclaimer_llm.invoke([
                disclaimer_classifier,
                HumanMessage(content=user_input)
            ]).content.strip()

            if result == "[ACCEPTED]":
                final_response = AIMessage(content="Thank you for accepting the disclaimer. You're now ready to begin the simulation.")
                st.success("✅ Disclaimer accepted.")
                st.session_state.messages0.append(final_response)
                st.session_state.prompt0_done = True
                st.session_state.prompt1_active = True
                st.rerun()
            else:
                st.warning("⚠️ That wasn't a clear acceptance. Please respond clearly (e.g., 'yes', 'okay').")
                follow_up = AIMessage(content="Just to confirm — do you acknowledge and accept the disclaimer so we can begin?")
                st.session_state.messages0.append(follow_up)
                st.rerun()

        llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        response = llm.invoke(st.session_state.messages0)
        st.session_state.messages0.append(response)

        if "do you acknowledge and accept this disclaimer" in response.content.lower():
            st.session_state.waiting_for_ack = True

        if "ready to begin the simulation" in response.content.lower():
            st.success("✅ Prompt 0 complete. You may proceed.")
            st.session_state.prompt0_done = True
            st.session_state.prompt1_active = True

        st.rerun()

# === PROMPT 1 ===
elif st.session_state.prompt1_active:
    st.subheader("🔊 Prompt 1: Simulated Patient Encounter")

    if len(st.session_state.messages1) == 1:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        first_response = llm.invoke(st.session_state.messages1)
        st.session_state.messages1.append(first_response)
        st.rerun()

    for msg in st.session_state.messages1:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").markdown(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").markdown(msg.content)

    user_input = st.chat_input("You:", key="prompt1_input")
    if user_input:
        st.session_state.messages1.append(HumanMessage(content=user_input))
        llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

        if user_input.lower().strip() == "end encounter":
            end_msg = AIMessage(content="I acknowledge the emotional intensity of these conversations. Thank you for participating in this training. Would you like to move on to the feedback and evaluation section?")
            st.session_state.messages1.append(end_msg)
            st.session_state.prompt1_done = True
            st.session_state.awaiting_feedback_prompt = True
            st.rerun()

        elif st.session_state.awaiting_feedback_prompt and not st.session_state.feedback_given:
            if user_input.lower().strip() in ["yes", "sure", "ok", "okay"]:
                st.session_state.messages1.append(AIMessage(content="Thank you. The feedback section will now begin."))
                transcript = "\n".join([
                    f"You (Doctor): {m.content}" if isinstance(m, HumanMessage) else f"Patient: {m.content}"
                    for m in st.session_state.messages1 if isinstance(m, (HumanMessage, AIMessage))
                ])

                # Request feedback with summary
                feedback_instruction = prompt2_text.replace("{transcript}", transcript)
                feedback_prompt = f"""
You are a feedback coach who has read the full transcript of a simulated patient-clinician encounter.

First, briefly summarize the conversation (3-4 sentences) so the user knows you understood it.
Then, give kind, evidence-based communication feedback based on the conversation.

Transcript:
{transcript}

Begin your feedback:
{feedback_instruction}
"""
                st.session_state.messages2 = [SystemMessage(content=feedback_prompt)]

                st.session_state.prompt1_active = False
                st.session_state.prompt2_active = True
                st.session_state.prompt2_initialized = False
                st.session_state.feedback_given = True
                st.rerun()
            elif user_input.lower().strip() in ["no", "not now"]:
                skip_msg = AIMessage(content="No problem. Thank you again for your participation.")
                st.session_state.messages1.append(skip_msg)
                st.session_state.feedback_given = True
                st.rerun()
            else:
                clarify = AIMessage(content="Would you like to proceed to the feedback and evaluation section? (yes/no)")
                st.session_state.messages1.append(clarify)
                st.rerun()

        else:
            response = llm.invoke(st.session_state.messages1)
            st.session_state.messages1.append(response)
            st.rerun()

# === PROMPT 2 ===
elif st.session_state.prompt2_active:
    st.subheader("📍 Prompt 2: Feedback and Evaluation")

    if not st.session_state.prompt2_initialized:
        llm = ChatOpenAI(model="gpt-4o", temperature=0.4)
        first_response = llm.invoke(st.session_state.messages2)
        st.session_state.messages2.append(first_response)
        st.session_state.prompt2_initialized = True
        st.rerun()

    for msg in st.session_state.messages2:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").markdown(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").markdown(msg.content)

    user_input = st.chat_input("You:", key="prompt2_input")
    if user_input:
        st.session_state.messages2.append(HumanMessage(content=user_input))
        llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
        response = llm.invoke(st.session_state.messages2)
        st.session_state.messages2.append(response)
        st.rerun()
