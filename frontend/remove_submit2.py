with open(r'D:\donation system\frontend\src\pages\NGODashboard.jsx', 'r') as f:
    content = f.read()

# Find the submitRequest function
idx = content.find('const submitRequest = async (e) => {')
print(f'Found submitRequest at index: {idx}')

if idx >= 0:
    # Find the end of the function by counting braces
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
                    end_idx = i + 1
                    break
        else:
            if c == string_char:
                in_string = False
                string_char = None
    
    if end_idx > 0:
        # Remove the function and any trailing blank line
        new_content = content[:idx] + content[end_idx:]
        with open(r'D:\donation system\frontend\src\pages\NGODashboard.jsx', 'w') as f:
            f.write(new_content)
        print(f'Removed submitRequest function (indices {idx} to {end_idx})')
    else:
        print('Could not find end of function')
else:
    print('submitRequest not found')