with open(r'D:\donation system\frontend\src\pages\NGODashboard.jsx', 'r') as f:
    content = f.read()

idx = content.find('const initialForm = {')
print(f'Found at index: {idx}')

if idx >= 0:
    brace_count = 0
    in_string = False
    string_char = None
    end_idx = -1
    
    for i in range(idx, len(content)):
        c = content[i]
        if not in_string:
            if c == '"' or c == "'":
                in_string = True
                string_char = c
            elif c == '{':
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    # Check if next non-whitespace is semicolon
                    j = i + 1
                    while j < len(content) and content[j].isspace():
                        j += 1
                    if j < len(content) and content[j] == ';':
                        end_idx = j + 1
                    else:
                        end_idx = i + 1
                    break
        else:
            if c == string_char:
                in_string = False
                string_char = None
    
    if end_idx > 0:
        new_content = content[:idx] + content[end_idx:]
        with open(r'D:\donation system\frontend\src\pages\NGODashboard.jsx', 'w') as f:
            f.write(new_content)
        print(f'Removed initialForm (indices {idx} to {end_idx})')
    else:
        print('Could not find end of initialForm')
else:
    print('initialForm not found')