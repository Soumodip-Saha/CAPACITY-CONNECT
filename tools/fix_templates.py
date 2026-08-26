import re
import os

files_to_fix = [
    "app/main.py",
    "app/routes/auth_routes.py",
    "app/routes/trainee_routes.py",
    "app/routes/trainer_routes.py",
    "app/routes/admin_routes.py"
]

def fix_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern: templates.TemplateResponse("template.html", {...}) -> templates.TemplateResponse(request=request, name="template.html", context={...})
    # Or templates.TemplateResponse("template.html", context, status_code=400) -> templates.TemplateResponse(request=request, name="template.html", context=context, status_code=400)
    
    # We can replace `templates.TemplateResponse(\s*("|\')` with `templates.TemplateResponse(request=request, name=\1`
    # and replace the second positional arg with `context=`
    # Better: let's write clean helper or regex
    
    # Let's inspect and rewrite using regex or standard patterns:
    content = re.sub(
        r'templates\.TemplateResponse\(\s*(["\'][^"\']+["\'])\s*,\s*(\{)',
        r'templates.TemplateResponse(request=request, name=\1, context=\2',
        content
    )
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fixed: {filepath}")

for fp in files_to_fix:
    fix_file(fp)
