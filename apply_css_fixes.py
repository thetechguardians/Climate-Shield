import re

files = [
    'Frontend/style.css',
    'Frontend/Analysis/analysis.css'
]

hidden_css = """
.hidden {
  display: none !important;
  opacity: 0 !important;
  pointer-events: none !important;
  visibility: hidden !important;
}

.chatbot-panel:not(.hidden) {
  opacity: 1 !important;
  pointer-events: auto !important;
  visibility: visible !important;
  transform: translateY(0) !important;
}
"""

accent_css = """
  --accent: #0284c7;
  --accent-2: #0369a1;
"""

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add .hidden if it's missing or incomplete
    if '.hidden {' not in content:
        content += hidden_css
    elif '.chatbot-panel:not(.hidden)' not in content:
        content += "\n.chatbot-panel:not(.hidden) { opacity: 1 !important; pointer-events: auto !important; visibility: visible !important; }\n"

    # 2. Add --accent to [data-theme="light"]
    if '--accent: #0284c7' not in content:
        # find [data-theme="light"] {
        pattern = r'(\[data-theme="light"\]\s*\{)'
        content = re.sub(pattern, r'\1' + accent_css, content, count=1)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("CSS fixes applied successfully.")
