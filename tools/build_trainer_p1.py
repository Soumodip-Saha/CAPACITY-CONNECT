import os

dashboard_html = '''{% extends "base.html" %}

{% block title %}Trainer Suite - MoES / IMD CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    
    <!-- Welcome Header -->
    <div class="bg-gradient-to-r from-emerald-950 via-slate-900 to-moes-navy rounded-3xl p-6 sm:p-8 text-white shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <div class="flex items-center gap-2 mb-2">
                <span class="bg-emerald-500/20 text-emerald-300 text-xs px-2.5 py-0.5 rounded-full font-bold border border-emerald-500/30">Faculty & Subject Expert Suite</span>
                <span class="text-xs text-slate-400">{{ user.department }}</span>
            </div>
            <h1 class="text-2xl sm:text-3xl font-black tracking-tight">{{ user.full_name }}</h1>
            <p class="text-xs sm:text-sm text-slate-300 mt-1">{{ user.designation }} &bull; Trainer Competency Index: <strong>94.5%</strong></p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
            <a href="/trainer/quiz/create" class="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow transition flex items-center gap-1.5">
                <i data-lucide="plus-circle" class="w-4 h-4"></i> Create Assessment
            </a>
            <a href="/trainer/library" class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold border border-slate-700 transition flex items-center gap-1.5">
                <i data-lucide="upload-cloud" class="w-4 h-4"></i> Upload Resource
            </a>
        </div>
    </div>

    <!-- 4 Stats Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-xs text-slate-500 font-medium mb-1">Assigned Courses</div>
            <div class="text-2xl font-black text-slate-900">{{ stats.total_courses }}</div>
            <div class="text-[11px] text-emerald-600 mt-1 font-semibold">Active curricula</div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-xs text-slate-500 font-medium mb-1">Enrolled Trainees</div>
            <div class="text-2xl font-black text-sky-600">{{ stats.total_students }}</div>
            <div class="text-[11px] text-sky-700 mt-1 font-semibold">Officers participating</div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-xs text-slate-500 font-medium mb-1">MCQ Quizzes Active</div>
            <div class="text-2xl font-black text-purple-600">{{ stats.total_quizzes }}</div>
            <div class="text-[11px] text-purple-700 mt-1 font-semibold">Evaluations published</div>
        </div>

        <div class="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-xs text-slate-500 font-medium mb-1">Trainee Rating</div>
            <div class="text-2xl font-black text-amber-600">{{ stats.avg_rating }} / 5.0 ★</div>
            <div class="text-[11px] text-amber-700 mt-1 font-semibold">Exceptional feedback</div>
        </div>
    </div>

    <!-- Active Courses & Trainee Roster -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- Left: Course Curricula Managed (7 cols) -->
        <div class="lg:col-span-7 space-y-6">
            <div class="flex justify-between items-center">
                <h2 class="text-lg font-black text-slate-900 flex items-center gap-2">
                    <i data-lucide="book-open" class="w-5 h-5 text-emerald-600"></i> My Authoring Curricula
                </h2>
                <a href="/trainer/courses" class="text-xs text-emerald-700 font-bold hover:underline">Manage All &rarr;</a>
            </div>

            <div class="space-y-4">
                {% for c in stats.courses %}
                    <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition space-y-3">
                        <div class="flex justify-between items-center">
                            <span class="bg-emerald-50 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded uppercase border border-emerald-200">{{ c.domain }}</span>
                            <span class="text-slate-400 text-xs font-mono">{{ c.code }}</span>
                        </div>
                        <h3 class="text-base font-bold text-slate-900 leading-snug">{{ c.title }}</h3>
                        <div class="flex justify-between items-center text-xs text-slate-500 pt-2 border-t border-slate-100">
                            <span>{{ c.duration_hours }} Hours &bull; {{ c.level }}</span>
                            <a href="/trainer/courses/{{ c.id }}/manage" class="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-lg text-xs flex items-center gap-1">
                                <i data-lucide="edit-3" class="w-3.5 h-3.5"></i> Edit Syllabus & Materials
                            </a>
                        </div>
                    </div>
                {% endfor %}
            </div>

            <!-- Recent Feedback from Trainees -->
            <div class="pt-4 space-y-4">
                <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
                    <i data-lucide="message-square" class="w-4 h-4 text-purple-600"></i> Recent Trainee Feedback & Ratings
                </h3>
                <div class="space-y-3">
                    {% for f in feedbacks %}
                        <div class="bg-white p-4 rounded-2xl border border-slate-200 text-xs space-y-1.5 shadow-sm">
                            <div class="flex justify-between items-center">
                                <span class="font-bold text-slate-900">{{ f.trainee_name }}</span>
                                <span class="text-amber-600 font-bold">Trainer Rating: {{ f.rating_trainer }}/5 ★</span>
                            </div>
                            <p class="text-slate-600 italic">"{{ f.comments }}"</p>
                            <span class="text-[10px] text-slate-400 block pt-1">{{ f.course_title }}</span>
                        </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Right: Enrolled Trainees Roster (5 cols) -->
        <div class="lg:col-span-5 space-y-6">
            
            <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-bold text-slate-900 text-sm flex items-center gap-2">
                        <i data-lucide="users" class="w-4 h-4 text-sky-600"></i> Enrolled Trainee Roster
                    </h3>
                    <span class="text-xs text-slate-400 font-bold">{{ trainees|length }} active</span>
                </div>

                <div class="space-y-3">
                    {% for t in trainees %}
                        <div class="p-3.5 rounded-2xl border border-slate-200 bg-slate-50/60 text-xs space-y-2">
                            <div class="flex justify-between items-start">
                                <div>
                                    <div class="font-bold text-slate-900">{{ t.trainee_name }}</div>
                                    <div class="text-[11px] text-slate-500">{{ t.trainee_department }}</div>
                                </div>
                                <span class="text-[10px] font-bold px-2 py-0.5 rounded {% if t.status == 'completed' %}bg-emerald-100 text-emerald-800{% else %}bg-sky-100 text-sky-800{% endif %}">
                                    {{ t.progress_percent }}%
                                </span>
                            </div>
                            <div class="text-[10px] text-slate-400 truncate">{{ t.course_title }}</div>
                        </div>
                    {% endfor %}
                </div>
            </div>

            <!-- Recent Quiz Submissions -->
            <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <h3 class="font-bold text-slate-900 text-sm flex items-center gap-2">
                        <i data-lucide="file-check" class="w-4 h-4 text-emerald-600"></i> Recent Assessment Attempts
                    </h3>
                </div>

                <div class="space-y-3">
                    {% for a in stats.recent_attempts %}
                        <div class="p-3 rounded-2xl border border-slate-200 bg-slate-50/60 text-xs space-y-1">
                            <div class="flex justify-between items-center">
                                <span class="font-bold text-slate-900">{{ a.trainee_name }}</span>
                                <span class="font-bold {% if a.is_passed %}text-emerald-700{% else %}text-amber-700{% endif %}">{{ a.percentage }}%</span>
                            </div>
                            <div class="text-[11px] text-slate-500">{{ a.quiz_title }}</div>
                        </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

courses_manage_html = '''{% extends "base.html" %}

{% block title %}Manage Course Syllabus - CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-6xl mx-auto px-4 py-8 space-y-8">
    
    <!-- Course Title Bar -->
    <div class="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <div class="flex items-center gap-2 mb-1">
                <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full uppercase border border-emerald-200">{{ course.domain }}</span>
                <span class="text-xs font-mono text-slate-400">{{ course.code }}</span>
            </div>
            <h1 class="text-2xl font-black text-slate-900">{{ course.title }}</h1>
            <p class="text-xs text-slate-500 mt-1">{{ course.duration_hours }} Hours &bull; {{ course.level }}</p>
        </div>

        <div class="flex items-center gap-2">
            <a href="/trainer/dashboard" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition">
                &larr; Back to Portal
            </a>
            <a href="/trainer/quiz/create?course_id={{ course.id }}" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow transition flex items-center gap-1.5">
                <i data-lucide="plus" class="w-3.5 h-3.5"></i> Add Quiz for this Course
            </a>
        </div>
    </div>

    <!-- Modules and Lessons Hierarchy -->
    <div class="space-y-6">
        <div class="flex justify-between items-center">
            <h2 class="text-lg font-black text-slate-900 flex items-center gap-2">
                <i data-lucide="layers" class="w-5 h-5 text-sky-600"></i> Course Modules & Interactive Lessons
            </h2>
            <button onclick="document.getElementById('addModuleModal').classList.toggle('hidden')" class="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold rounded-xl shadow flex items-center gap-1.5">
                <i data-lucide="plus" class="w-3.5 h-3.5"></i> Add New Module
            </button>
        </div>

        {% for m in modules %}
            <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm space-y-4">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <div>
                        <span class="text-[10px] font-bold uppercase text-slate-400">Module {{ m.order_num }}</span>
                        <h3 class="text-base font-bold text-slate-900">{{ m.title }}</h3>
                        <p class="text-xs text-slate-500 mt-0.5">{{ m.summary or "" }}</p>
                    </div>
                    <button onclick="openAddLessonModal({{ m.id }}, '{{ m.title|replace('\'', '\\\'') }}')" class="px-3.5 py-1.5 bg-emerald-50 text-emerald-800 hover:bg-emerald-100 rounded-xl text-xs font-bold border border-emerald-200 flex items-center gap-1">
                        <i data-lucide="plus" class="w-3 h-3"></i> Add Lesson
                    </button>
                </div>

                <!-- Lessons in Module -->
                <div class="space-y-2 pl-4">
                    {% for l in m.lessons %}
                        <div class="p-3 bg-slate-50 rounded-2xl border border-slate-200 flex justify-between items-center text-xs">
                            <div class="flex items-center gap-3">
                                <span class="bg-slate-200 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded uppercase">{{ l.lesson_type }}</span>
                                <span class="font-bold text-slate-800">{{ l.title }}</span>
                            </div>
                            <span class="text-slate-400 text-[11px]">{{ l.duration_mins }} Minutes</span>
                        </div>
                    {% else %}
                        <p class="text-xs text-slate-400 italic py-2">No lessons added to this module yet.</p>
                    {% endfor %}
                </div>
            </div>
        {% endfor %}
    </div>
</div>

<!-- Modal: Add Module -->
<div id="addModuleModal" class="hidden fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl p-6 max-w-md w-full border border-slate-200 shadow-2xl space-y-4">
        <div class="flex justify-between items-center">
            <h3 class="font-bold text-slate-900 text-base">Add New Course Module</h3>
            <button onclick="document.getElementById('addModuleModal').classList.add('hidden')" class="p-1 text-slate-400 hover:text-slate-600"><i data-lucide="x" class="w-5 h-5"></i></button>
        </div>
        <form action="/trainer/courses/{{ course.id }}/modules/add" method="post" class="space-y-3">
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Module Title</label>
                <input type="text" name="title" required placeholder="e.g. Module 3: Radar Signal Processing" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Module Summary</label>
                <textarea name="summary" rows="2" placeholder="Brief summary of topics covered" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl"></textarea>
            </div>
            <button type="submit" class="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-xl text-xs shadow">Save Module</button>
        </form>
    </div>
</div>

<!-- Modal: Add Lesson -->
<div id="addLessonModal" class="hidden fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl p-6 max-w-md w-full border border-slate-200 shadow-2xl space-y-4">
        <div class="flex justify-between items-center">
            <h3 class="font-bold text-slate-900 text-base">Add Lesson to Module</h3>
            <button onclick="document.getElementById('addLessonModal').classList.add('hidden')" class="p-1 text-slate-400 hover:text-slate-600"><i data-lucide="x" class="w-5 h-5"></i></button>
        </div>
        <form action="/trainer/courses/{{ course.id }}/lessons/add" method="post" class="space-y-3">
            <input type="hidden" name="module_id" id="modal_module_id" value="">
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Lesson Title</label>
                <input type="text" name="title" required placeholder="e.g. 2.1 Velocity Dealiasing Algorithms" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
            <div class="grid grid-cols-2 gap-3">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Lesson Type</label>
                    <select name="lesson_type" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white">
                        <option value="video">Recorded Video Lecture</option>
                        <option value="presentation">Slide Deck (PPT/PDF)</option>
                        <option value="document">Technical Document</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Duration (Mins)</label>
                    <input type="number" name="duration_mins" value="25" min="5" max="180" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                </div>
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Content / Embed URL</label>
                <input type="text" name="content_url" placeholder="https://www.youtube.com/embed/... or /static/docs/..." class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Lecture Key Notes</label>
                <textarea name="notes" rows="2" placeholder="Key concepts, mathematical equations, or reference links" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl"></textarea>
            </div>
            <button type="submit" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs shadow">Publish Lesson</button>
        </form>
    </div>
</div>

<script>
function openAddLessonModal(moduleId, moduleTitle) {
    document.getElementById('modal_module_id').value = moduleId;
    document.getElementById('addLessonModal').classList.remove('hidden');
}
</script>
{% endblock %}
'''

courses_list_html = '''{% extends "base.html" %}

{% block title %}Manage Courses - Trainer Suite{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 py-8 space-y-8">
    <div class="flex justify-between items-center">
        <div>
            <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full uppercase border border-emerald-200">Curricula Management</span>
            <h1 class="text-3xl font-black text-slate-900 mt-1">Author & Manage Courses</h1>
        </div>
        <button onclick="document.getElementById('createCourseModal').classList.toggle('hidden')" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow flex items-center gap-1.5">
            <i data-lucide="plus" class="w-4 h-4"></i> Create New Course
        </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for c in courses %}
            <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
                <div>
                    <div class="flex justify-between items-center mb-2">
                        <span class="bg-emerald-50 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded uppercase">{{ c.domain }}</span>
                        <span class="text-xs font-mono text-slate-400">{{ c.code }}</span>
                    </div>
                    <h3 class="text-base font-bold text-slate-900 leading-snug">{{ c.title }}</h3>
                    <p class="text-xs text-slate-500 line-clamp-2 mt-1">{{ c.description }}</p>
                </div>

                <div class="pt-3 border-t border-slate-100 flex justify-between items-center text-xs">
                    <span class="text-slate-400">{{ c.enrollment_count }} Trainees</span>
                    <a href="/trainer/courses/{{ c.id }}/manage" class="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-lg text-xs">
                        Manage Content &rarr;
                    </a>
                </div>
            </div>
        {% endfor %}
    </div>
</div>

<!-- Modal Create Course -->
<div id="createCourseModal" class="hidden fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl p-6 sm:p-8 max-w-lg w-full border border-slate-200 shadow-2xl space-y-4">
        <div class="flex justify-between items-center">
            <h3 class="font-bold text-slate-900 text-base">Create New MoES/IMD Course</h3>
            <button onclick="document.getElementById('createCourseModal').classList.add('hidden')" class="p-1 text-slate-400 hover:text-slate-600"><i data-lucide="x" class="w-5 h-5"></i></button>
        </div>
        <form action="/trainer/courses/create" method="post" class="space-y-3">
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Course Title</label>
                <input type="text" name="title" required placeholder="e.g. Dual-Pol Radar Data Quality Control" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
            <div class="grid grid-cols-2 gap-3">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Course Code</label>
                    <input type="text" name="code" required placeholder="e.g. IMD-RAD-205" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl uppercase">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Domain</label>
                    <select name="domain" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white">
                        <option value="Numerical Weather Prediction">Numerical Weather Prediction</option>
                        <option value="Radar Meteorology">Radar Meteorology</option>
                        <option value="Satellite Meteorology">Satellite Meteorology</option>
                        <option value="Cyclone Forecasting">Cyclone Forecasting</option>
                        <option value="Agrometeorology">Agrometeorology</option>
                        <option value="Seismology & Tsunami">Seismology & Tsunami</option>
                    </select>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Level</label>
                    <select name="level" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white">
                        <option value="Beginner">Beginner</option>
                        <option value="Intermediate">Intermediate</option>
                        <option value="Advanced">Advanced</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Duration (Hours)</label>
                    <input type="number" name="duration_hours" value="20" min="5" max="100" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                </div>
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Description</label>
                <textarea name="description" rows="3" required placeholder="Detailed overview of technical topics and competencies targeted..." class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl"></textarea>
            </div>
            <button type="submit" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs shadow">Publish New Curriculum</button>
        </form>
    </div>
</div>
{% endblock %}
'''

with open("app/templates/trainer/dashboard.html", "w", encoding="utf-8") as f:
    f.write(dashboard_html)

with open("app/templates/trainer/course_manage.html", "w", encoding="utf-8") as f:
    f.write(courses_manage_html)

with open("app/templates/trainer/courses.html", "w", encoding="utf-8") as f:
    f.write(courses_list_html)

print("Trainer templates Part 1 created successfully")
