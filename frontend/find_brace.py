with open(r'D:\donation system\frontend\src\pages\NGODashboard.jsx', 'r') as f:
    content = f.read()

# Find the exact position of 'showCreate && ('
idx = content.find('showCreate && (')
print(f'Found at index: {idx}')

# Find the matching closing ')}' 
# Count braces and parentheses
paren_count = 0
brace_count = 0
in_string = False
string_char = None

for i in range(idx, len(content)):
    c = content[i]
    if not in_string:
        if c == '"' or c == "'":
            in_string = True
            string_char = c
        elif c == '(':
            paren_count += 1
        elif c == ')':
            paren_count -= 1
        elif c == '{':
            brace_count += 1
        elif c == '}':
            brace_count -= 1
            if paren_count == 0 and brace_count == 0:
                print(f'Found matching }} at index {idx + i}: {content[idx:idx+i+1][:200]}')
                break
    else:
        if c == string_char:
            in_string = False
            string_char = None