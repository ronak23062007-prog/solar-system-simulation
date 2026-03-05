import os

files = ['graphics/renderer.py', 'ui/main_window.py', 'core/barnes_hut.py']
for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        content = content.replace('\\"', '"') # Remove backslash escapes
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
