with open('graph/llm.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for idx, line in enumerate(lines):
    if idx >= 215 and 'elif language == "mr":' in line:
        skip = True
    if skip and 'def call_llm' in line:
        skip = False
        new_lines.append("\n\n")
    if not skip:
        new_lines.append(line)

with open('graph/llm.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Cleaned successfully with enumerate.")
