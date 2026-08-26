import os

competency_map_html = '''{% extends "base.html" %}

{% block title %}Competency Mapping Engine - CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 py-8 space-y-8">
    
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <div class="flex items-center gap-2 mb-1">
                <span class="text-xs font-bold text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-full uppercase border border-amber-200 flex items-center gap-1">
                    <i data-lucide="cpu" class="w-3.5 h-3.5"></i> Algorithmic Resource Allocation
                </span>
            </div>
            <h1 class="text-3xl font-black text-slate-900 mt-1">Trainer Competency Mapping Engine</h1>
            <p class="text-xs text-slate-500 mt-1">Identifies and ranks the most qualified trainers for specialized Earth Science & Meteorological subjects based on skill matrix, domain experience, and trainee feedback.</p>
        </div>
    </div>

    <!-- Search & Formulation Panel -->
    <div class="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
        <form action="/admin/competency-map" method="get" class="space-y-4">
            
            <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
                <div class="md:col-span-6">
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Target Subject or Skill Domain *</label>
                    <div class="relative">
                        <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-3"></i>
                        <input type="text" name="subject" value="{{ subject }}" required placeholder="e.g. Doppler Radar Nowcasting or WRF Model Tuning" class="w-full pl-9 pr-4 py-2.5 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-amber-500 focus:outline-none">
                    </div>
                </div>

                <div class="md:col-span-4">
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Domain Classification</label>
                    <select name="domain" class="w-full px-3 py-2.5 text-xs border border-slate-300 rounded-xl bg-white focus:ring-2 focus:ring-amber-500">
                        <option value="">All Earth Science Domains</option>
                        {% for d in domains %}
                            <option value="{{ d }}" {% if domain == d %}selected{% endif %}>{{ d }}</option>
                        {% endfor %}
                    </select>
                </div>

                <div class="md:col-span-2 flex items-end">
                    <button type="submit" class="w-full py-2.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-bold rounded-xl text-xs shadow transition flex items-center justify-center gap-1.5">
                        <i data-lucide="sparkles" class="w-4 h-4"></i> Run Match
                    </button>
                </div>
            </div>

            <!-- Preset Quick Topics -->
            <div class="pt-2 border-t border-slate-100">
                <span class="text-[11px] font-bold text-slate-400 uppercase mr-2">Quick Sample Prompts:</span>
                <div class="inline-flex flex-wrap gap-1.5 mt-1">
                    {% for top in preset_topics %}
                        <a href="/admin/competency-map?subject={{ top|urlencode }}" class="text-[10px] font-semibold bg-slate-100 hover:bg-amber-100 hover:text-amber-900 text-slate-700 px-2 py-0.5 rounded-lg border border-slate-200 transition">
                            {{ top }}
                        </a>
                    {% endfor %}
                </div>
            </div>
        </form>
    </div>

    <!-- Algorithm Match Results Header -->
    <div class="flex justify-between items-center">
        <div>
            <h2 class="text-lg font-black text-slate-900 flex items-center gap-2">
                <i data-lucide="trophy" class="w-5 h-5 text-amber-500"></i> Ranked Trainers for "{{ subject }}"
            </h2>
            <p class="text-xs text-slate-500 mt-0.5">Ranked by weighted composite of Skill Overlap (50%), Domain Alignment (25%), Seniority (15%), & Feedback (10%)</p>
        </div>
        <span class="text-xs bg-amber-100 text-amber-900 font-bold px-3 py-1 rounded-full border border-amber-300">
            {{ ranked_trainers|length }} Trainers Evaluated
        </span>
    </div>

    <!-- Ranked Cards Grid -->
    <div class="space-y-4">
        {% for t in ranked_trainers %}
            <div class="bg-white rounded-3xl p-6 sm:p-8 border-2 {% if t.total_score >= 80 %}border-emerald-400 shadow-md{% elif t.total_score >= 60 %}border-sky-300 shadow-sm{% else %}border-slate-200{% endif %} flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                
                <!-- Trainer Dossier -->
                <div class="space-y-3 flex-1">
                    <div class="flex flex-wrap items-center gap-2">
                        <span class="text-xs font-bold px-2.5 py-0.5 rounded-full uppercase {% if t.tier == 'Top Match' %}bg-emerald-100 text-emerald-800 border border-emerald-300{% elif t.tier == 'Strong Match' %}bg-sky-100 text-sky-800 border border-sky-300{% else %}bg-slate-100 text-slate-700{% endif %}">
                            {{ t.tier }}
                        </span>
                        <span class="text-xs text-slate-500 font-medium">{{ t.designation }}</span>
                        <span class="text-slate-300">&bull;</span>
                        <span class="text-xs text-slate-500">{{ t.department }}</span>
                    </div>

                    <h3 class="text-xl font-black text-slate-900">{{ t.full_name }}</h3>
                    <p class="text-xs text-slate-600 font-serif italic">{{ t.qualifications }} &bull; {{ t.experience_years }} Years Domain Experience</p>

                    <!-- Score Breakdown Bars -->
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 text-[11px] bg-slate-50 p-3 rounded-2xl border border-slate-100 max-w-xl">
                        <div>
                            <span class="text-slate-400 block text-[9px]">Skill Overlap</span>
                            <strong class="text-slate-900 font-bold">{{ t.skill_score }} / 50 pts</strong>
                        </div>
                        <div>
                            <span class="text-slate-400 block text-[9px]">Domain Relevance</span>
                            <strong class="text-slate-900 font-bold">{{ t.domain_score }} / 25 pts</strong>
                        </div>
                        <div>
                            <span class="text-slate-400 block text-[9px]">Experience Score</span>
                            <strong class="text-slate-900 font-bold">{{ t.exp_score }} / 15 pts</strong>
                        </div>
                        <div>
                            <span class="text-slate-400 block text-[9px]">Trainee Rating</span>
                            <strong class="text-amber-600 font-bold">{{ t.avg_rating }} ★ ({{ t.rating_score }} pts)</strong>
                        </div>
                    </div>

                    <!-- Matching Skills Pills -->
                    <div class="flex flex-wrap items-center gap-1.5 pt-1">
                        <span class="text-[10px] text-slate-400 font-bold uppercase mr-1">Matching Skills:</span>
                        {% for sk in t.matching_skills %}
                            <span class="bg-sky-50 text-sky-800 text-[10px] font-bold px-2 py-0.5 rounded-md border border-sky-200">
                                {{ sk }}
                            </span>
                        {% endfor %}
                    </div>
                </div>

                <!-- Match Score Dial & Action -->
                <div class="flex flex-col items-center justify-center shrink-0 p-4 bg-slate-50 rounded-2xl border border-slate-200 min-w-[160px] text-center space-y-3">
                    <div>
                        <div class="text-[10px] uppercase font-bold text-slate-400">Competency Fit</div>
                        <div class="text-3xl font-black {% if t.total_score >= 80 %}text-emerald-600{% elif t.total_score >= 60 %}text-sky-600{% else %}text-slate-600{% endif %}">
                            {{ t.total_score }}%
                        </div>
                    </div>

                    <button onclick="alert('Trainer {{ t.full_name }} successfully assigned to lead capacity building program for: {{ subject }}')" class="w-full px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs rounded-xl shadow transition">
                        Assign to Batch
                    </button>
                </div>
            </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
'''

admin_announcements_html = '''{% extends "base.html" %}

{% block title %}Bulletin & Announcement Manager - CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 py-8 space-y-8">
    
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <span class="text-xs font-bold text-purple-700 bg-purple-50 px-2.5 py-0.5 rounded-full uppercase border border-purple-200">Portal Communications</span>
            <h1 class="text-3xl font-black text-slate-900 mt-1">Announcements & Circulars Manager</h1>
            <p class="text-xs text-slate-500 mt-1">Publish homepage alerts, national training notices, MoES achievements, and newly launched course spotlights.</p>
        </div>
        <button onclick="document.getElementById('publishModal').classList.toggle('hidden')" class="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs rounded-xl shadow flex items-center gap-1.5">
            <i data-lucide="plus-circle" class="w-4 h-4"></i> Publish New Notice
        </button>
    </div>

    <!-- Announcements List -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        {% for a in announcements %}
            <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
                <div class="space-y-2">
                    <div class="flex justify-between items-center">
                        <span class="bg-purple-50 text-purple-800 text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase border border-purple-200">{{ a.category }}</span>
                        <span class="text-[10px] font-bold px-2 py-0.5 rounded {% if a.priority == 'Urgent' %}bg-rose-100 text-rose-800{% elif a.priority == 'Important' %}bg-amber-100 text-amber-800{% else %}bg-slate-100 text-slate-700{% endif %}">
                            {{ a.priority }}
                        </span>
                    </div>

                    <h3 class="text-base font-bold text-slate-900 leading-snug">{{ a.title }}</h3>
                    <p class="text-xs text-slate-600 leading-relaxed">{{ a.content }}</p>
                </div>

                <div class="pt-3 border-t border-slate-100 flex justify-between items-center text-xs">
                    <span class="text-slate-400 font-mono text-[10px]">{{ a.created_at[:10] }}</span>
                    <form action="/admin/announcements/{{ a.id }}/delete" method="post">
                        <button type="submit" onclick="return confirm('Delete this announcement?')" class="text-xs text-rose-600 font-bold hover:underline">
                            Delete Notice
                        </button>
                    </form>
                </div>
            </div>
        {% endfor %}
    </div>
</div>

<!-- Modal Publish Announcement -->
<div id="publishModal" class="hidden fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl p-6 sm:p-8 max-w-lg w-full border border-slate-200 shadow-2xl space-y-4">
        <div class="flex justify-between items-center">
            <h3 class="font-bold text-slate-900 text-base">Publish Portal Announcement</h3>
            <button onclick="document.getElementById('publishModal').classList.add('hidden')" class="p-1 text-slate-400 hover:text-slate-600"><i data-lucide="x" class="w-5 h-5"></i></button>
        </div>
        <form action="/admin/announcements/create" method="post" class="space-y-3">
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Title</label>
                <input type="text" name="title" required placeholder="e.g. National Training on Satellite Radiance" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
            <div class="grid grid-cols-2 gap-3">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Category</label>
                    <select name="category" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white">
                        <option value="Announcement">Announcement</option>
                        <option value="Circular">Official Circular</option>
                        <option value="Workshop">National Workshop</option>
                        <option value="Achievement">Achievement Highlight</option>
                        <option value="New Course">New Course Spotlight</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Priority</label>
                    <select name="priority" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white">
                        <option value="Normal">Normal</option>
                        <option value="Important">Important</option>
                        <option value="Urgent">Urgent</option>
                    </select>
                </div>
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Content / Circular Details</label>
                <textarea name="content" rows="4" required placeholder="Official announcement text..." class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl"></textarea>
            </div>
            <button type="submit" class="w-full py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-xl text-xs shadow">Publish Bulletin</button>
        </form>
    </div>
</div>
{% endblock %}
'''

with open("app/templates/admin/competency_map.html", "w", encoding="utf-8") as f:
    f.write(competency_map_html)

with open("app/templates/admin/announcements.html", "w", encoding="utf-8") as f:
    f.write(admin_announcements_html)

print("Admin templates Part 2 created successfully")
