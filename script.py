import json
import re

with open('data/finetune_validation.json', 'r') as file:
    data = json.load(file)

formatted_data = []

for entry in data:
    response_data = entry["response"]

    if isinstance(response_data, str):
        try:
            cleaned_response = re.sub(r'[\x00-\x1F]+', '', response_data)
            response_data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            continue 

    formatted_entry = {
        "industry": entry["industry"],
        "question": entry["question"],
        "response": {
            "answer": response_data.get("answer", ""),
            "references": response_data.get("references", [])
        }
    }
    formatted_data.append(formatted_entry)

output_path = 'data/formatted/formatted_finetune_validation.json'
with open(output_path, 'w') as output_file:
    json.dump({"data": formatted_data}, output_file, indent=4)

print(f"Data reformatted and saved to {output_path}")
