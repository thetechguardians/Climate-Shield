import os

files = ['Frontend/style.css', 'Frontend/Analysis/analysis.css']
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace the incorrectly formatted CSS selector
    content = content.replace('[data-theme=" light\\]', '[data-theme="light"]')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
