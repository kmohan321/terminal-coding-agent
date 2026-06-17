import json
import uuid
import os

def tree_walker(id_map, current_leaf_id):
  messages = []
  curr_id = current_leaf_id

  while curr_id is not None:
    data = id_map[curr_id]
    clean_msg = {"role": data["role"], "content": data.get("content")}
    
    if "tool_calls" in data:
        clean_msg["tool_calls"] = data["tool_calls"]
    if "tool_call_id" in data:
        clean_msg["tool_call_id"] = data["tool_call_id"]
        
    messages.append(clean_msg)
    curr_id = data.get("parent_id")

  return list(reversed(messages))

class SessionManager:
  def __init__(self, session_path):
    self.path = session_path

    if not os.path.exists(self.path):
       with open(self.path, 'w') as f:
          pass

  def current_id(self):
    with open(self.path, 'r') as f:
      data = [json.loads(line) for line in f]

    if data:
       id = data[-1]["id"]
       return id
    return None
     
  def get_history(self, current_leaf_id):

    with open(self.path, 'r') as f:
      data = [json.loads(line) for line in f]

    id_map = {msg["id"]: msg for msg in data}
    messages = tree_walker(id_map, current_leaf_id)
    return messages
  
  def add_user_message(self, parent_id = None, content = None):

    id = str(uuid.uuid4())
    new_message = {"id": id, "parent_id": parent_id, "role": "user", "content": content}

    with open(self.path, "a") as f:
        f.write(json.dumps(new_message) + "\n")

    return id

  def add_agent_message(self, parent_id = None, content = None):

    id = str(uuid.uuid4())
    new_message = {"id": id, "parent_id": parent_id, "role": "assistant", "content": content}

    with open(self.path, "a") as f:
        f.write(json.dumps(new_message) + "\n")

    return id

  def add_tool_message(self):
    pass
