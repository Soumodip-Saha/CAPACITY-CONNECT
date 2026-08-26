import os

login_html = '''{% extends "base.html" %}

{% block title %}Secure Officer Login - MoES / IMD CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-slate-100">
    <div class="max-w-md w-full space-y-6">
        
        <!-- Header -->
        <div class="text-center">
            <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-sky-500 to-blue-700 text-white flex items-center justify-center mx-auto shadow-lg shadow-sky-500/30">
                <i data-lucide="lock" class="w-8 h-8"></i>
            </div>
            <h2 class="mt-4 text-2xl font-black text-slate-900 tracking-tight">Capacity Building Portal Login</h2>
            <p class="text-xs text-slate-500 mt-1">Ministry of Earth Sciences / India Meteorological Department</p>
        </div>

        {% if error %}
            <div class="bg-rose-50 border border-rose-200 text-rose-700 px-4 py-3 rounded-xl text-xs flex items-center gap-2 animate-shake">
                <i data-lucide="alert-circle" class="w-4 h-4 shrink-0 text-rose-500"></i>
                <span>{{ error }}</span>
            </div>
        {% endif %}

        <!-- 1-Click Demo Logins Banner -->
        <div class="bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-amber-500/10 border border-amber-300/80 rounded-2xl p-4 shadow-sm">
            <div class="flex items-center justify-between mb-3">
                <span class="text-xs font-bold text-amber-900 flex items-center gap-1.5">
                    <i data-lucide="zap" class="w-4 h-4 text-amber-600"></i> Quick 1-Click Demo Login:
                </span>
                <span class="text-[10px] bg-amber-200/80 text-amber-900 px-2 py-0.5 rounded font-bold">Hackathon Demo</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-center text-xs">
                <a href="/auth/demo-login/admin" class="p-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold shadow-sm transition flex flex-col items-center gap-1">
                    <i data-lucide="shield" class="w-4 h-4"></i>
                    <span>Admin</span>
                </a>
                <a href="/auth/demo-login/trainer" class="p-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold shadow-sm transition flex flex-col items-center gap-1">
                    <i data-lucide="presentation" class="w-4 h-4"></i>
                    <span>Trainer</span>
                </a>
                <a href="/auth/demo-login/trainee" class="p-2.5 bg-sky-600 hover:bg-sky-700 text-white rounded-xl font-bold shadow-sm transition flex flex-col items-center gap-1">
                    <i data-lucide="graduation-cap" class="w-4 h-4"></i>
                    <span>Trainee</span>
                </a>
            </div>
        </div>

        <!-- Login Form -->
        <div class="bg-white p-8 rounded-3xl border border-slate-200 shadow-xl">
            <form action="/auth/login" method="post" class="space-y-4">
                <input type="hidden" name="next" value="{{ next }}">
                
                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Official Email Address</label>
                    <div class="relative">
                        <i data-lucide="mail" class="w-4 h-4 text-slate-400 absolute left-3 top-3.5"></i>
                        <input type="email" name="email" required placeholder="officer@imd.gov.in" class="w-full pl-10 pr-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Password</label>
                    <div class="relative">
                        <i data-lucide="key" class="w-4 h-4 text-slate-400 absolute left-3 top-3.5"></i>
                        <input type="password" name="password" required placeholder="••••••••" class="w-full pl-10 pr-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                    </div>
                </div>

                <div class="pt-2">
                    <button type="submit" class="w-full py-3 bg-gradient-to-r from-sky-600 to-blue-700 hover:from-sky-500 hover:to-blue-600 text-white font-bold rounded-xl shadow-lg shadow-sky-600/30 transition flex items-center justify-center gap-2 text-sm">
                        <i data-lucide="log-in" class="w-4 h-4"></i> Sign In to Capacity Connect
                    </button>
                </div>
            </form>

            <div class="mt-6 pt-4 border-t border-slate-100 text-center">
                <p class="text-xs text-slate-500">
                    Don't have an officer account yet?
                    <a href="/auth/register" class="font-bold text-sky-600 hover:text-sky-700 ml-1">Register Here</a>
                </p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

register_html = '''{% extends "base.html" %}

{% block title %}Officer Registration - MoES / IMD CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-3xl mx-auto px-4 py-12">
    <div class="text-center mb-8">
        <span class="bg-sky-100 text-sky-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
            Portal Registration
        </span>
        <h1 class="text-3xl font-black text-slate-900 mt-2">Join CAPACITY CONNECT</h1>
        <p class="text-xs sm:text-sm text-slate-500 mt-1">Register as a Trainee or Subject Matter Trainer for Earth Science & Meteorology programs</p>
    </div>

    {% if error %}
        <div class="bg-rose-50 border border-rose-200 text-rose-700 p-4 rounded-2xl text-xs flex items-center gap-2 mb-6 animate-shake">
            <i data-lucide="alert-circle" class="w-4 h-4 shrink-0 text-rose-500"></i>
            <span>{{ error }}</span>
        </div>
    {% endif %}

    {% if success %}
        <div class="bg-emerald-50 border border-emerald-200 text-emerald-800 p-6 rounded-3xl text-sm mb-6 space-y-3 animate-fade-in">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-emerald-600 text-white flex items-center justify-center shrink-0">
                    <i data-lucide="check" class="w-6 h-6"></i>
                </div>
                <div>
                    <h3 class="font-bold text-base">Registration Submitted Successfully</h3>
                    <p class="text-xs text-emerald-700">{{ success }}</p>
                </div>
            </div>
            <div class="pt-2">
                <a href="/auth/login" class="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-700 text-white rounded-xl font-bold text-xs hover:bg-emerald-600 transition">
                    Go to Login Page <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                </a>
            </div>
        </div>
    {% endif %}

    <div class="bg-white p-8 sm:p-10 rounded-3xl border border-slate-200 shadow-xl">
        <form action="/auth/register" method="post" class="space-y-6">
            
            <!-- Role Selection -->
            <div>
                <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Select Your Role</label>
                <div class="grid grid-cols-2 gap-4">
                    <label class="relative flex flex-col p-4 rounded-2xl border-2 cursor-pointer transition border-sky-500 bg-sky-50/50 has-[:checked]:border-sky-600 has-[:checked]:bg-sky-100/60">
                        <input type="radio" name="role" value="trainee" checked class="sr-only" onchange="toggleRoleFields('trainee')">
                        <div class="flex items-center justify-between mb-1">
                            <span class="font-bold text-slate-900 text-sm">🎓 Trainee / Officer</span>
                            <i data-lucide="check-circle-2" class="w-4 h-4 text-sky-600"></i>
                        </div>
                        <span class="text-[11px] text-slate-500">Immediate access to enroll in courses & assessments</span>
                    </label>

                    <label class="relative flex flex-col p-4 rounded-2xl border-2 cursor-pointer transition border-slate-200 hover:border-slate-300 has-[:checked]:border-emerald-600 has-[:checked]:bg-emerald-50">
                        <input type="radio" name="role" value="trainer" class="sr-only" onchange="toggleRoleFields('trainer')">
                        <div class="flex items-center justify-between mb-1">
                            <span class="font-bold text-slate-900 text-sm">👨‍🏫 Trainer / Faculty</span>
                            <i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-600"></i>
                        </div>
                        <span class="text-[11px] text-slate-500">Requires Admin approval before publishing courses</span>
                    </label>
                </div>
            </div>

            <!-- Credentials -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Full Name *</label>
                    <input type="text" name="full_name" required placeholder="e.g. Dr. Amit Sharma" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Official Email Address *</label>
                    <input type="email" name="email" required placeholder="e.g. asharm@imd.gov.in" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Password *</label>
                    <input type="password" name="password" required placeholder="Minimum 6 characters" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Designation</label>
                    <input type="text" name="designation" placeholder="e.g. Meteorologist Grade-I / Scientist-E" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                </div>
            </div>

            <!-- Organizational & Technical Profile -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Department / Observatory Center</label>
                    <input type="text" name="department" placeholder="e.g. IMD RMC Kolkata / NWP Division" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Years of Experience</label>
                    <input type="number" name="experience_years" value="3" min="0" max="45" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                </div>
            </div>

            <div>
                <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Qualifications</label>
                <input type="text" name="qualifications" placeholder="e.g. M.Sc. Atmospheric Science, Ph.D. Meteorology" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
            </div>

            <div>
                <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Core Skills & Competencies (comma separated)</label>
                <input type="text" name="skills" placeholder="e.g. Radar Meteorology, WRF Model, Python MetPy, Cyclone Tracking" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                <span class="text-[10px] text-slate-400 mt-1 block">Used by the Competency Mapping Engine to match courses and specialized workshops.</span>
            </div>

            <div>
                <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Research Interests & Domain Focus</label>
                <input type="text" name="interests" placeholder="e.g. Severe Storms, Monsoon Dynamics, Satellite Remote Sensing" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
            </div>

            <div>
                <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Professional Bio / Summary</label>
                <textarea name="bio" rows="3" placeholder="Brief summary of your meteorological responsibilities and capacity goals..." class="w-full px-4 py-2 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none"></textarea>
            </div>

            <div class="pt-2">
                <button type="submit" class="w-full py-3.5 bg-gradient-to-r from-sky-600 to-blue-700 hover:from-sky-500 hover:to-blue-600 text-white font-bold rounded-xl shadow-lg shadow-sky-600/30 transition text-sm">
                    Complete Officer Registration
                </button>
            </div>
        </form>

        <div class="mt-6 pt-4 border-t border-slate-100 text-center">
            <p class="text-xs text-slate-500">
                Already registered?
                <a href="/auth/login" class="font-bold text-sky-600 hover:text-sky-700 ml-1">Sign In to Account</a>
            </p>
        </div>
    </div>
</div>

<script>
function toggleRoleFields(role) {
    // dynamically adjust styling if needed
}
</script>
{% endblock %}
'''

with open("app/templates/auth/login.html", "w", encoding="utf-8") as f:
    f.write(login_html)

with open("app/templates/auth/register.html", "w", encoding="utf-8") as f:
    f.write(register_html)

print("app/templates/auth/login.html & register.html created successfully")
