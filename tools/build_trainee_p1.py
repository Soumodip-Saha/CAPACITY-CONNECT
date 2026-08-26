import os

dashboard_html = '''{% extends "base.html" %}

{% block title %}Trainee Dashboard - MoES / IMD CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    
    <!-- Welcome Header -->
    <div class="bg-gradient-to-r from-moes-navy via-slate-900 to-sky-900 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden">
        <div class="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
                <div class="flex items-center gap-2 mb-2">
                    <span class="bg-sky-500/20 text-sky-300 text-xs px-2.5 py-0.5 rounded-full font-bold border border-sky-400/30">Trainee Learning Suite</span>
                    <span class="text-xs text-slate-400">{{ user.department }}</span>
                </div>
                <h1 class="text-2xl sm:text-3xl font-black tracking-tight">Welcome back, {{ user.full_name }}!</h1>
                <p class="text-xs sm:text-sm text-slate-300 mt-1">{{ user.designation }} &bull; Atmospheric & Earth Sciences Capacity Track</p>
            </div>
            <div class="flex items-center gap-3">
                <a href="/trainee/profile" class="px-4 py-2.5 bg-slate-800/80 hover:bg-slate-700 text-white rounded-xl text-xs font-bold border border-slate-700 transition flex items-center gap-1.5">
                    <i data-lucide="user-check" class="w-4 h-4 text-sky-400"></i> My Profile & Skills
                </a>
                <a href="/trainee/courses" class="px-4 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-xl text-xs font-bold shadow transition flex items-center gap-1.5">
                    <i data-lucide="plus-circle" class="w-4 h-4"></i> Browse New Courses
                </a>
            </div>
        </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-xs text-slate-500 font-medium mb-1">Enrolled Courses</div>
            <div class="text-2xl font-black text-slate-900">{{ enrollments|length }}</div>
            <div class="text-[11px] text-sky-600 mt-1 font-semibold">Active learning pathways</div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-xs text-slate-500 font-medium mb-1">Certificates Earned</div>
            <div class="text-2xl font-black text-amber-600">{{ certificates|length }}</div>
            <div class="text-[11px] text-amber-700 mt-1 font-semibold">Official MoES Credentials</div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-xs text-slate-500 font-medium mb-1">Quizzes Available</div>
            <div class="text-2xl font-black text-emerald-600">{{ quizzes|length }}</div>
            <div class="text-[11px] text-emerald-700 mt-1 font-semibold">Assessments ready</div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-xs text-slate-500 font-medium mb-1">Experience Logged</div>
            <div class="text-2xl font-black text-purple-600">{{ user.experience_years }} Yrs</div>
            <div class="text-[11px] text-purple-700 mt-1 font-semibold">Domain seniority</div>
        </div>
    </div>

    <!-- Main Grid: My Courses & Upcoming Quizzes -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- Left: Enrolled Courses List (8 cols) -->
        <div class="lg:col-span-8 space-y-6">
            <div class="flex justify-between items-center">
                <h2 class="text-lg font-black text-slate-900 flex items-center gap-2">
                    <i data-lucide="book-open" class="w-5 h-5 text-sky-600"></i> My Active Courses
                </h2>
                <span class="text-xs text-slate-400">{{ enrollments|length }} in progress / completed</span>
            </div>

            {% if enrollments %}
                <div class="space-y-4">
                    {% for e in enrollments %}
                        <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition">
                            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-3">
                                <div>
                                    <span class="bg-sky-50 text-sky-700 text-[10px] font-bold px-2 py-0.5 rounded uppercase border border-sky-200">{{ e.domain }}</span>
                                    <span class="text-slate-400 text-xs ml-2 font-mono">{{ e.code }}</span>
                                </div>
                                {% if e.enrollment_status == 'completed' %}
                                    <span class="bg-emerald-100 text-emerald-800 text-xs font-bold px-2.5 py-0.5 rounded-full flex items-center gap-1">
                                        <i data-lucide="check-circle" class="w-3.5 h-3.5"></i> Completed
                                    </span>
                                {% else %}
                                    <span class="bg-sky-100 text-sky-800 text-xs font-bold px-2.5 py-0.5 rounded-full">
                                        In Progress ({{ e.progress_percent }}%)
                                    </span>
                                {% endif %}
                            </div>

                            <h3 class="text-base font-bold text-slate-900 mb-1">
                                <a href="/trainee/courses/{{ e.course_id }}" class="hover:text-sky-600 transition">{{ e.title }}</a>
                            </h3>
                            <p class="text-xs text-slate-500 mb-4">Instructor: <strong>{{ e.trainer_name or "MoES Certified Faculty" }}</strong></p>

                            <!-- Progress Bar -->
                            <div class="space-y-1.5 mb-4">
                                <div class="flex justify-between text-[11px] text-slate-500 font-medium">
                                    <span>Course Progress</span>
                                    <span>{{ e.progress_percent }}%</span>
                                </div>
                                <div class="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                                    <div class="h-full bg-gradient-to-r from-sky-500 to-emerald-500 rounded-full" style="width: {{ e.progress_percent }}%"></div>
                                </div>
                            </div>

                            <div class="flex justify-between items-center pt-3 border-t border-slate-100 text-xs">
                                <span class="text-slate-400">Enrolled on {{ e.enrolled_at[:10] }}</span>
                                <a href="/trainee/courses/{{ e.course_id }}" class="px-4 py-1.5 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-lg shadow-sm transition flex items-center gap-1.5">
                                    Resume Learning <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                                </a>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="bg-white rounded-2xl p-8 border border-slate-200 text-center text-slate-500">
                    <i data-lucide="book-marked" class="w-12 h-12 text-slate-300 mx-auto mb-3"></i>
                    <h3 class="font-bold text-slate-800 text-base">You have not enrolled in any courses yet</h3>
                    <p class="text-xs text-slate-500 mt-1 max-w-sm mx-auto">Explore our MoES/IMD specialized domain catalog and enroll in high-resolution modeling, radar meteorology, and satellite courses.</p>
                    <a href="/trainee/courses" class="inline-block mt-4 px-5 py-2.5 bg-sky-600 text-white text-xs font-bold rounded-xl shadow">Explore Courses</a>
                </div>
            {% endif %}

            <!-- Recommended Courses -->
            <div class="pt-6">
                <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 flex items-center gap-2">
                    <i data-lucide="sparkles" class="w-4 h-4 text-amber-500"></i> Recommended For Your Skill Profile
                </h3>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {% for rec in recommended %}
                        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
                            <div>
                                <span class="text-[10px] font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded uppercase">{{ rec.domain }}</span>
                                <h4 class="font-bold text-slate-900 text-sm mt-2 line-clamp-1">{{ rec.title }}</h4>
                                <p class="text-xs text-slate-500 line-clamp-2 mt-1">{{ rec.description }}</p>
                            </div>
                            <div class="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-xs">
                                <span class="text-slate-400">{{ rec.duration_hours }} hrs &bull; {{ rec.level }}</span>
                                <form action="/trainee/enroll/{{ rec.id }}" method="post">
                                    <button type="submit" class="px-3 py-1 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-lg text-xs">Enroll</button>
                                </form>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Right: Upcoming Quizzes & Earned Certificates (4 cols) -->
        <div class="lg:col-span-4 space-y-6">
            
            <!-- Quizzes Card -->
            <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-bold text-slate-900 text-sm flex items-center gap-2">
                        <i data-lucide="file-check" class="w-4 h-4 text-emerald-600"></i> Available Assessments
                    </h3>
                    <span class="text-[11px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">{{ quizzes|length }}</span>
                </div>

                {% if quizzes %}
                    <div class="space-y-3">
                        {% for q in quizzes %}
                            <div class="p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition space-y-2">
                                <div class="font-bold text-slate-900 text-xs leading-snug">{{ q.quiz_title }}</div>
                                <div class="text-[11px] text-slate-500">{{ q.course_title }}</div>
                                <div class="flex justify-between items-center text-[11px] pt-1">
                                    <span class="text-slate-400"><i data-lucide="clock" class="w-3 h-3 inline"></i> {{ q.duration_mins }} Mins</span>
                                    {% if q.has_passed %}
                                        <span class="text-emerald-700 font-bold bg-emerald-100 px-2 py-0.5 rounded">Passed ({{ q.best_score }}%)</span>
                                    {% else %}
                                        <a href="/trainee/assessment/{{ q.quiz_id }}" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg shadow-sm">
                                            Start Quiz
                                        </a>
                                    {% endif %}
                                </div>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <p class="text-xs text-slate-400 text-center py-4">No active quizzes pending for enrolled courses.</p>
                {% endif %}
            </div>

            <!-- Certificates Card -->
            <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-bold text-slate-900 text-sm flex items-center gap-2">
                        <i data-lucide="award" class="w-4 h-4 text-amber-500"></i> Earned Certificates
                    </h3>
                    <span class="text-[11px] bg-amber-100 text-amber-800 font-bold px-2 py-0.5 rounded-full">{{ certificates|length }}</span>
                </div>

                {% if certificates %}
                    <div class="space-y-3">
                        {% for c in certificates %}
                            <div class="p-3.5 rounded-xl border border-amber-200 bg-amber-50/50 space-y-2">
                                <div class="flex justify-between items-start">
                                    <div class="font-bold text-slate-900 text-xs">{{ c.course_title }}</div>
                                    <span class="text-[10px] font-bold text-amber-800 bg-amber-200 px-1.5 py-0.5 rounded">{{ c.grade }}</span>
                                </div>
                                <div class="text-[11px] font-mono text-slate-500">{{ c.certificate_id }}</div>
                                <div class="pt-2 flex justify-between items-center">
                                    <span class="text-[10px] text-slate-400">{{ c.issue_date }}</span>
                                    <a href="/trainee/certificate/{{ c.certificate_id }}" class="text-xs font-bold text-amber-700 hover:text-amber-800 flex items-center gap-1">
                                        View Certificate <i data-lucide="external-link" class="w-3 h-3"></i>
                                    </a>
                                </div>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <p class="text-xs text-slate-400 text-center py-4">Score &ge; 70% in course assessments to automatically generate verifiable MoES certificates.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

profile_html = '''{% extends "base.html" %}

{% block title %}Trainee Profile & Credentials - CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-5xl mx-auto px-4 py-10 space-y-8">
    
    <div>
        <span class="text-xs font-bold uppercase tracking-wider text-sky-600 bg-sky-50 px-2.5 py-1 rounded">Professional Dossier</span>
        <h1 class="text-3xl font-black text-slate-900 mt-2">Trainee Profile & Qualifications</h1>
        <p class="text-xs text-slate-500 mt-1">Manage your scientific background, observational center, core skills, and verifiable certifications</p>
    </div>

    {% if success %}
        <div class="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-2xl text-xs flex items-center gap-2 animate-fade-in">
            <i data-lucide="check-circle" class="w-4 h-4 text-emerald-600"></i>
            <span>{{ success }}</span>
        </div>
    {% endif %}

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- Left: Edit Profile Form (8 cols) -->
        <div class="lg:col-span-8 bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
            <form action="/trainee/profile" method="post" class="space-y-6">
                
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Full Name *</label>
                        <input type="text" name="full_name" value="{{ user.full_name }}" required class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Official Email</label>
                        <input type="email" disabled value="{{ user.email }}" class="w-full px-4 py-2.5 text-sm border border-slate-200 bg-slate-50 text-slate-500 rounded-xl cursor-not-allowed">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Designation</label>
                        <input type="text" name="designation" value="{{ user.designation or '' }}" placeholder="e.g. Meteorologist Grade-I" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Department / Center</label>
                        <input type="text" name="department" value="{{ user.department or '' }}" placeholder="e.g. IMD Cyclone Warning Division" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                    </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Qualifications</label>
                        <input type="text" name="qualifications" value="{{ user.qualifications or '' }}" placeholder="e.g. M.Sc. Atmospheric Science" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Years of Experience</label>
                        <input type="number" name="experience_years" value="{{ user.experience_years or 0 }}" min="0" max="45" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                    </div>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Core Skills & Competencies (comma separated)</label>
                    <input type="text" name="skills" value="{{ user.skills or '' }}" placeholder="e.g. Synoptic Meteorology, Radar Interpretation, WRF" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Research Interests & Domain Focus</label>
                    <input type="text" name="interests" value="{{ user.interests or '' }}" placeholder="e.g. Tropical Cyclones, Severe Weather" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">Bio / Work Experience Summary</label>
                    <textarea name="bio" rows="4" class="w-full px-4 py-2.5 text-sm border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none">{{ user.bio or '' }}</textarea>
                </div>

                <div class="pt-2">
                    <button type="submit" class="px-6 py-3 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-xl shadow transition text-xs">
                        Save Profile Changes
                    </button>
                </div>
            </form>
        </div>

        <!-- Right: Certificates & Badges Showcase (4 cols) -->
        <div class="lg:col-span-4 space-y-6">
            
            <div class="bg-gradient-to-br from-amber-500/10 to-orange-500/10 p-6 rounded-3xl border border-amber-300/80 shadow-sm space-y-4">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-amber-500 text-slate-950 flex items-center justify-center font-bold">
                        <i data-lucide="award" class="w-6 h-6"></i>
                    </div>
                    <div>
                        <h3 class="font-bold text-slate-900 text-sm">MoES Official Credentials</h3>
                        <p class="text-[11px] text-slate-500">Issued by Training Directorate</p>
                    </div>
                </div>

                {% if certificates %}
                    <div class="space-y-3 pt-2">
                        {% for c in certificates %}
                            <div class="p-3 bg-white rounded-xl border border-amber-200 shadow-sm space-y-1">
                                <div class="text-xs font-bold text-slate-900">{{ c.course_title }}</div>
                                <div class="text-[11px] text-emerald-700 font-bold">Grade: {{ c.grade }} ({{ c.score_percentage }}%)</div>
                                <div class="text-[10px] font-mono text-slate-400">{{ c.certificate_id }}</div>
                                <div class="pt-2">
                                    <a href="/trainee/certificate/{{ c.certificate_id }}" class="text-[11px] font-bold text-sky-600 hover:underline">
                                        View Certificate &rarr;
                                    </a>
                                </div>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <p class="text-xs text-slate-500 leading-relaxed">Complete course assessments with a score of 70% or higher to automatically add your digital certifications here.</p>
                {% endif %}
            </div>

            <!-- Skills Badges Card -->
            <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3">
                <h3 class="font-bold text-slate-900 text-xs uppercase tracking-wider">Active Competency Badges</h3>
                <div class="flex flex-wrap gap-1.5">
                    {% if user.skills %}
                        {% for s in user.skills.split(',') %}
                            <span class="bg-sky-50 text-sky-800 text-xs font-semibold px-2.5 py-1 rounded-lg border border-sky-200">
                                {{ s.strip() }}
                            </span>
                        {% endfor %}
                    {% else %}
                        <span class="text-xs text-slate-400">No skills added yet.</span>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

courses_html = '''{% extends "base.html" %}

{% block title %}Course Catalog - MoES / IMD CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
    
    <!-- Title & Search Bar -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <span class="text-xs font-bold uppercase tracking-wider text-sky-600 bg-sky-50 px-2.5 py-1 rounded">Curricula Repository</span>
            <h1 class="text-3xl font-black text-slate-900 mt-2">MoES & IMD Capacity Building Courses</h1>
            <p class="text-xs sm:text-sm text-slate-500 mt-1">Specialized training programs in Atmospheric, Oceanic, Seismological, and Climate Sciences</p>
        </div>

        <!-- Search Form -->
        <form action="/trainee/courses" method="get" class="flex gap-2 w-full md:w-auto">
            <input type="hidden" name="domain" value="{{ selected_domain }}">
            <div class="relative w-full sm:w-80">
                <i data-lucide="search" class="w-4 h-4 text-slate-400 absolute left-3 top-3"></i>
                <input type="text" name="search" value="{{ search }}" placeholder="Search courses or topics..." class="w-full pl-9 pr-4 py-2 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none bg-white">
            </div>
            <button type="submit" class="px-4 py-2 bg-sky-600 text-white font-bold text-xs rounded-xl shadow">Search</button>
        </form>
    </div>

    <!-- Domain Filters Pills -->
    <div class="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        <a href="/trainee/courses" class="px-3.5 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition {% if not selected_domain %}bg-sky-600 text-white shadow{% else %}bg-white border border-slate-200 text-slate-700 hover:bg-slate-50{% endif %}">
            All Domains
        </a>
        {% for d in domains %}
            <a href="/trainee/courses?domain={{ d|urlencode }}&search={{ search }}" class="px-3.5 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition {% if selected_domain == d %}bg-sky-600 text-white shadow{% else %}bg-white border border-slate-200 text-slate-700 hover:bg-slate-50{% endif %}">
                {{ d }}
            </a>
        {% endfor %}
    </div>

    <!-- Courses Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for c in courses %}
            <div class="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-lg transition flex flex-col justify-between">
                <div class="p-6 space-y-4">
                    <div class="flex justify-between items-center gap-2">
                        <span class="bg-sky-50 text-sky-800 text-[10px] font-bold px-2.5 py-1 rounded-full uppercase border border-sky-200">
                            {{ c.domain }}
                        </span>
                        <span class="text-slate-400 text-xs font-mono font-semibold">{{ c.code }}</span>
                    </div>

                    <h3 class="text-lg font-bold text-slate-900 leading-snug">
                        <a href="/trainee/courses/{{ c.id }}" class="hover:text-sky-600 transition">{{ c.title }}</a>
                    </h3>

                    <p class="text-xs text-slate-500 line-clamp-3 leading-relaxed">
                        {{ c.description }}
                    </p>

                    <div class="grid grid-cols-2 gap-2 text-xs bg-slate-50 p-3 rounded-xl border border-slate-100">
                        <div>
                            <span class="text-slate-400 block text-[10px]">Lead Trainer</span>
                            <strong class="text-slate-800">{{ c.trainer_name or "MoES Faculty" }}</strong>
                        </div>
                        <div>
                            <span class="text-slate-400 block text-[10px]">Duration & Level</span>
                            <strong class="text-slate-800">{{ c.duration_hours }} Hrs &bull; {{ c.level }}</strong>
                        </div>
                    </div>
                </div>

                <div class="p-6 pt-0 border-t border-slate-100 flex items-center justify-between mt-2">
                    <span class="text-xs text-slate-400">{{ c.enrolled_count }} Officers Enrolled</span>

                    {% if c.user_enrollment_id %}
                        <a href="/trainee/courses/{{ c.id }}" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow transition flex items-center gap-1.5">
                            <i data-lucide="play" class="w-3.5 h-3.5"></i> Resume ({{ c.user_progress }}%)
                        </a>
                    {% else %}
                        <form action="/trainee/enroll/{{ c.id }}" method="post">
                            <button type="submit" class="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold rounded-xl shadow transition flex items-center gap-1.5">
                                <i data-lucide="plus" class="w-3.5 h-3.5"></i> Enroll Now
                            </button>
                        </form>
                    {% endif %}
                </div>
            </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
'''

with open("app/templates/trainee/dashboard.html", "w", encoding="utf-8") as f:
    f.write(dashboard_html)

with open("app/templates/trainee/profile.html", "w", encoding="utf-8") as f:
    f.write(profile_html)

with open("app/templates/trainee/courses.html", "w", encoding="utf-8") as f:
    f.write(courses_html)

print("Trainee templates Part 1 created successfully")
