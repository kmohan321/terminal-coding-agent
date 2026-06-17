import os
from groq import Groq
from dotenv import load_dotenv
import uuid

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

import json
from datetime import datetime

# 1. The Dynamic System Prompt
def get_system_prompt():
    """
    The system prompt must be aware of its environment. 
    We inject the current working directory so the agent knows where it is.
    """
    current_dir = os.getcwd()
    date = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "role": "system",
        "content": f"""You are a minimal CLI coding agent running on a local machine.
Current Working Directory: {current_dir}
Current Date: {date}

You have access to local tools. If a task requires reading files, running tests, or editing code, output a tool call. 
Do NOT ask for permission to run tools, just run them.
When you are completely finished, output your final response to the user."""
    }

# 2. Context Initialization
def build_full_context(jsonl_filepath, current_leaf_id):
    """
    Reads the tree, linearizes it, and prepends the system prompt.
    """
    # Fallback if no history exists yet
    if not os.path.exists(jsonl_filepath) or current_leaf_id is None:
        return [get_system_prompt()]

    # Your exact tree walker logic
    with open(jsonl_filepath, 'r') as f:
        data = [json.loads(line) for line in f]
    
    id_map = {msg["id"]: msg for msg in data}
    messages = []
    
    curr_id = current_leaf_id
    while curr_id is not None:
        msg_obj = id_map[curr_id]
        
        # Extract only the keys the LLM API expects (role, content, tool_calls, etc.)
        # We strip out 'id' and 'parent_id' because the LLM doesn't need to see our internal tree metadata
        clean_msg = {"role": msg_obj["role"], "content": msg_obj.get("content")}
        
        if "tool_calls" in msg_obj:
            clean_msg["tool_calls"] = msg_obj["tool_calls"]
        if "tool_call_id" in msg_obj:
            clean_msg["tool_call_id"] = msg_obj["tool_call_id"]
            
        messages.append(clean_msg)
        curr_id = msg_obj.get("parent_id")
    
    # Reverse to chronological order and prepend the system prompt
    linear_history = list(reversed(messages))
    return [get_system_prompt()] + linear_history

# 3. The Execution Loop (Milestone 2)
def chat_loop():
    SESSION_FILE = "session.jsonl" # Local Approach
    current_leaf_id = None # In a real app, you'd read the last line of the file to get this
    
    print("Agent Initialized. Type 'exit' to quit.")
    current_leaf_id = None
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit']:
            break
          
        # [MOCK STEP] Here you would generate an ID, append the user message to session.jsonl, 
        # and update current_leaf_id.
        if current_leaf_id is None:
          id = str(uuid.uuid4())
          current_leaf_id = id
          new_message = {"id": current_leaf_id, "parent_id": None, "role": "user", "content": user_input}
        else:
          id = str(uuid.uuid4())
          new_message = {"id": id, "parent_id": current_leaf_id, "role": "user", "content": user_input}
          current_leaf_id = id
        
        with open("session.jsonl", "a") as f:
          f.write(json.dumps(new_message) + "\n")
        
        # 1. Initialize Context
        messages = build_full_context(SESSION_FILE, current_leaf_id)
        
        # 2. Call the LLM
        print("Agent is thinking...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            # tools=my_tools_schema  <-- You will add this in Milestone 4
        )
        
        reply = response.choices[0].message
        
        # 3. Evaluate the Response
        if reply.tool_calls:
            # The agent wants to execute a tool!
            print(f"Agent requested to use tools: {[t.function.name for t in reply.tool_calls]}")
            # [MOCK STEP] Here you would execute the local Python functions, capture stdout,
            # append the results to JSONL, and loop back to send the results to the LLM.
        else:
            # The agent just wants to talk
            print(f"\nAgent: {reply.content}")

            id = str(uuid.uuid4())
            new_message = {"id": id, "parent_id": current_leaf_id, "role": "assistant", "content": reply.content}
            current_leaf_id = id
        
            with open("session.jsonl", "a") as f:
              f.write(json.dumps(new_message) + "\n")

            # [MOCK STEP] Append this assistant message to your JSONL and update current_leaf_id.

if __name__ == "__main__":
    chat_loop()