import re

content = open("frontend/index.html", encoding="utf-8").read()
for m in re.finditer(r'fetchLeads\(\)', content):
    start = max(0, m.start() - 100)
    end = min(len(content), m.end() + 100)
    print(content[start:end])
    print("-" * 50)
