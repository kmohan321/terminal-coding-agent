import json

with open("messages.jsonl", 'r') as f:
  data = [json.loads(line) for line in f]

id_map = {msg["id"]: msg for msg in data}
# print(id_map)

def tree_walker(current_leaf_id):
  messages = []
  curr_id = current_leaf_id

  while curr_id is not None:
    data = id_map[curr_id]
    curr_id = data["parent_id"]
    messages.append(data.copy())
  
  return list(reversed(messages))

messages = tree_walker("msg_003")
print(messages)