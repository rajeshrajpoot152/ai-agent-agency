import re

content = open("frontend/index.html", encoding="utf-8").read()
for m in re.finditer(r'leads-tbody', content):
    start = max(0, m.start() - 200)
    end = min(len(content), m.end() + 1000)
    print("Match at position:", m.start())
    print(content[start:end])
    print("="*60)
