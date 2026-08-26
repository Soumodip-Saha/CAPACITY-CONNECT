import os

custom_css = '''/* Custom styles for CAPACITY CONNECT */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=JetBrains+Mono:wght@400;600;700&display=swap');

body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.font-serif {
    font-family: 'Playfair Display', Georgia, serif;
}

.font-mono {
    font-family: 'JetBrains Mono', monospace;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    20%, 60% { transform: translateX(-4px); }
    40%, 80% { transform: translateX(4px); }
}

.animate-fade-in {
    animation: fadeIn 0.25s ease-out forwards;
}

.animate-shake {
    animation: shake 0.3s ease-in-out;
}

/* Print Certificate Specific Styling */
@media print {
    body * {
        visibility: hidden;
    }
    #certificateNode, #certificateNode * {
        visibility: visible;
    }
    #certificateNode {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        margin: 0;
        padding: 40px;
        box-shadow: none !important;
        border: 4px solid #b45309 !important;
    }
    nav, header, footer, .print\\:hidden {
        display: none !important;
    }
}
'''

app_js = '''// CAPACITY CONNECT - Global UI Interactions
document.addEventListener('DOMContentLoaded', () => {
    if (window.lucide) {
        lucide.createIcons();
    }
});

// Toast notification helper
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-6 right-6 z-50 px-5 py-3 rounded-2xl shadow-xl text-xs font-bold text-white transition-all transform animate-fade-in ${
        type === 'success' ? 'bg-emerald-600' : type === 'error' ? 'bg-rose-600' : 'bg-slate-900'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 4000);
}
'''

run_py = '''import uvicorn
import os
import sys

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    
    print("=" * 70)
    print("  CAPACITY CONNECT - MoES & IMD Digital Capacity Building Portal")
    print("=" * 70)
    print(f"  * Server URL:      http://{host}:{port}")
    print("  * Public Portal:   http://127.0.0.1:8000")
    print("  * Course Catalog:  http://127.0.0.1:8000/trainee/courses")
    print("  * Admin Console:   http://127.0.0.1:8000/admin/dashboard")
    print("  * 1-Click Login:   Use the '1-Click Demo Login' button on top header")
    print("=" * 70)
    print("  Demo Accounts:")
    print("  - Admin:   admin@imd.gov.in           (Password: Admin@123)")
    print("  - Trainer: dr.m.sharma@imd.gov.in     (Password: Trainer@123)")
    print("  - Trainee: trainee.verma@imd.gov.in   (Password: Trainee@123)")
    print("=" * 70)

    uvicorn.run("app.main:app", host=host, port=port, reload=True)
'''

with open("app/static/css/custom.css", "w", encoding="utf-8") as f:
    f.write(custom_css)

with open("app/static/js/app.js", "w", encoding="utf-8") as f:
    f.write(app_js)

with open("run.py", "w", encoding="utf-8") as f:
    f.write(run_py)

print("Static CSS, JS, and run.py generated successfully")
