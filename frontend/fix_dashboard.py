with open(r'D:\donation system\frontend\src\pages\NGODashboard.jsx', 'r') as f:
    content = f.read()

# Find the start of the modal
idx = content.find('showCreate && (')
print(f'Start index: {idx}')

# Find the matching closing by counting braces and parens
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
                end_pos = i + 1
                print(f'Found end at index: {idx + i}')
                print(f'Total length: {end_pos - idx}')
                # Show the surrounding context
                print(f'Context: ...{content[idx-50:idx+i+50]}...')
                break
    else:
        if c == string_char:
            in_string = False
            string_char = None

# Now we know the exact positions, let's do the replacement
# Replace {showCreate && ( with {showCreate ? (
# And replace the final )} with ) : null}

# Find all occurrences
import re

# First, replace the opening
new_content = content.replace('showCreate && (', 'showCreate ? (')

# Now we need to replace the closing )} with ) : null}
# But only for the modal. The modal ends with '        )}' at the end
# Let's find the specific pattern: '        )}' at the end of the modal

# Actually, let's do a more targeted replacement
# Replace the specific pattern: '        )}' at the end of the modal with '        ) : null}'

# Find the last occurrence of '        )}' in the modal section
# The modal ends around position 26214 + length

# Let's do a simpler approach: replace the ternary properly
# The original: {showCreate && ( ... )}
# Should become: {showCreate ? ( ... ) : null}

# Find the start and end of the modal
start_idx = content.find('showCreate && (')
if start_idx == -1:
    print('Start not found')
else:
    # Find the end by scanning
    paren = 0
    brace = 0
    in_str = False
    str_char = None
    end_idx = -1
    for i in range(start_idx, len(content)):
        c = content[i]
        if not in_str:
            if c == '"' or c == "'":
                in_str = True
                str_char = c
            elif c == '(':
                paren += 1
            elif c == ')':
                paren -= 1
            elif c == '{':
                brace += 1
            elif c == '}':
                brace -= 1
                if paren == 0 and brace == 0:
                    end_pos = i + 1
                    break
        else:
            if c == content[i-1] == '\\':
                pass
            elif c == str_char:
                in_str = False
                str_char = None

    if end_idx > 0:
        # Extract the modal content
        modal_content = content[start_idx:end_pos]
        print(f'Modal length: {len(modal_content)}')
        # Replace the start and end
        new_modal = modal_content.replace('showCreate && (', 'showCreate ? (', 1)
        new_modal = new_modal[:-2] + ' : null}'  # Replace ')}' with ' : null}'
        # Replace in content
        new_content = content[:start_idx] + new_modal + content[end_pos:]
        with open(r'D:\donation system\frontend\src\pages\NGODashboard.jsx', 'w') as f:
            f.write(new_content)
        print('File updated successfully')
    else:
        print('Start not found')