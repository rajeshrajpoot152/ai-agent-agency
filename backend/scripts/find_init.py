import re

content = open("frontend/index.html", encoding="utf-8").read()
for m in re.finditer(r'window\.addEventListener\(["\']load["\']|document\.addEventListener\(["\']DOMContentLoaded["\']|function init\(', content):
    start = max(0, m.start() - 50)
    end = min(len(content), m.end() + 300)
    print(content[start:end])
