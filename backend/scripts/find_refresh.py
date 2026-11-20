import re

content = open("frontend/index.html", encoding="utf-8").read()
for m in re.finditer(r'function refreshUniversalData', content):
    start = max(0, m.start() - 50)
    end = min(len(content), m.end() + 300)
    print(content[start:end])
