import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    text = f.read()

tabs = re.findall(r'<div id="(tab-[^"]+)"', text)
print("Tabs found in index.html:", tabs)
