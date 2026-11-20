import re

content = open("frontend/index.html", encoding="utf-8").read()
matches = re.findall(r'id="(tab-[^"]+)"', content)
print("Tab IDs found:", matches)
