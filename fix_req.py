import sys
import codecs

with open('requirements.txt', 'r', encoding='utf-16') as f:
    content = f.read()

with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
