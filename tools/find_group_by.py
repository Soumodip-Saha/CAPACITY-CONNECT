import os

for root, dirs, files in os.walk("app"):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as fp:
                content = fp.read()
            if "qq.correct_option" in content or "qq.question_text" in content:
                print(f"Found in {path}")
