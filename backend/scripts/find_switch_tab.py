import re

content = open("frontend/index.html", encoding="utf-8").read()
for m in re.finditer(r'function switchTab', content):
    start = max(0, m.start() - 50)
    end = min(len(content), m.end() + 500)
    print(content[start:end])
