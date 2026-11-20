import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    text = f.read()

matches = re.findall(r'id="([^"]*modal[^"]*)"', text, re.IGNORECASE)
print("Modals found:", matches)
