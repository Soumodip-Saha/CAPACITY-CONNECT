import os
import re

for root, dirs, files in os.walk("app"):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as fp:
                lines = fp.readlines()
            for idx, line in enumerate(lines, 1):
                if re.search(r'fetchone\(\)\s*\[\s*0\s*\]', line) or re.search(r'row\s*\[\s*0\s*\]', line):
                    print(f"{path}:{idx}: {line.strip()}")
