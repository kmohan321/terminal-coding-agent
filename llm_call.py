import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

from prompts import get_system_prompt
from session_manager import SessionManager


client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

session_mng = SessionManager("messages.jsonl")

def build_full_context(current_leaf_id):
    """
    Function for initilaizing the context (not complete will add more features).
    """
    linear_history = session_mng.get_history(current_leaf_id)
    return [get_system_prompt()] + linear_history


def chat_loop():

    current_leaf_id = session_mng.current_id()
    print("Agent Initialized. Type 'exit' to quit.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            break
          
        if current_leaf_id is None:
          current_leaf_id = session_mng.add_user_message(parent_id=None, content=user_input)
        else:
          current_leaf_id = session_mng.add_user_message(parent_id=current_leaf_id, content=user_input)

        messages = build_full_context(current_leaf_id)

        print("Agent is thinking...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            # tools=my_tools_schema  <-- You will add this in Milestone 4
        )
        
        reply = response.choices[0].message

        if reply.tool_calls:
            # The agent wants to execute a tool!
            print(f"Agent requested to use tools: {[t.function.name for t in reply.tool_calls]}")
            # [MOCK STEP] Here you would execute the local Python functions, capture stdout,
            # append the results to JSONL, and loop back to send the results to the LLM.
        else:

            print(f"\nAgent: {reply.content}")
            current_leaf_id = session_mng.add_agent_message(parent_id=current_leaf_id, content=reply.content)

if __name__ == "__main__":
    chat_loop()