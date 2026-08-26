import os

create_quiz_html = '''{% extends "base.html" %}

{% block title %}Create MCQ Assessment - Trainer Suite{% endblock %}

{% block content %}
<div class="max-w-5xl mx-auto px-4 py-8 space-y-8">
    
    <div class="flex justify-between items-center">
        <div>
            <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full uppercase border border-emerald-200">Assessment Authoring</span>
            <h1 class="text-3xl font-black text-slate-900 mt-1">Create Subject-wise MCQ Questionnaire</h1>
            <p class="text-xs text-slate-500 mt-1">Design timed multiple-choice assessments with answer keys, scientific explanations, and auto-certification thresholds.</p>
        </div>
        <a href="/trainer/dashboard" class="text-xs font-bold text-slate-600 hover:text-slate-900">&larr; Back to Suite</a>
    </div>

    <form action="/trainer/quiz/create" method="post" id="createQuizForm" class="space-y-6">
        
        <!-- Quiz Meta Configuration Card -->
        <div class="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <h3 class="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <i data-lucide="settings-2" class="w-4 h-4 text-emerald-600"></i> Assessment Settings
            </h3>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Target Course *</label>
                    <select name="course_id" required class="w-full px-3 py-2.5 text-xs border border-slate-300 rounded-xl bg-white focus:ring-2 focus:ring-emerald-500">
                        {% for c in courses %}
                            <option value="{{ c.id }}" {% if selected_course_id == c.id %}selected{% endif %}>{{ c.code }} - {{ c.title }}</option>
                        {% endfor %}
                    </select>
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Assessment Title *</label>
                    <input type="text" name="title" required placeholder="e.g. Mid-Term Radar Interpretation & Nowcasting Assessment" class="w-full px-3 py-2.5 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500">
                </div>

                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Subject / Specialized Topic *</label>
                    <input type="text" name="subject" required placeholder="e.g. Doppler Velocity & Severe Storm Signatures" class="w-full px-3 py-2.5 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-emerald-500">
                </div>

                <div class="grid grid-cols-3 gap-2">
                    <div>
                        <label class="block text-[11px] font-bold text-slate-700 mb-1">Duration (Mins)</label>
                        <input type="number" name="duration_mins" value="20" min="5" max="180" class="w-full px-3 py-2.5 text-xs border border-slate-300 rounded-xl">
                    </div>
                    <div>
                        <label class="block text-[11px] font-bold text-slate-700 mb-1">Passing %</label>
                        <input type="number" name="pass_percentage" value="70" min="50" max="100" class="w-full px-3 py-2.5 text-xs border border-slate-300 rounded-xl">
                    </div>
                    <div>
                        <label class="block text-[11px] font-bold text-slate-700 mb-1">Deadline (Days)</label>
                        <input type="number" name="deadline_days" value="30" min="1" max="180" class="w-full px-3 py-2.5 text-xs border border-slate-300 rounded-xl">
                    </div>
                </div>
            </div>
        </div>

        <!-- Questions Dynamic Builder Container -->
        <div class="space-y-4">
            <div class="flex justify-between items-center">
                <h3 class="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <i data-lucide="help-circle" class="w-4 h-4 text-sky-600"></i> Multiple Choice Questions (<span id="questionCountDisplay">2</span>)
                </h3>
                <button type="button" onclick="addQuestionCard()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow flex items-center gap-1.5">
                    <i data-lucide="plus" class="w-4 h-4"></i> Add Another Question
                </button>
            </div>

            <div id="questionsContainer" class="space-y-4">
                
                <!-- Question 1 Default -->
                <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3 question-block" data-index="1">
                    <div class="flex justify-between items-center border-b border-slate-100 pb-2">
                        <span class="font-bold text-xs text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-lg border border-emerald-200">Question #1</span>
                        <div class="flex items-center gap-2 text-xs">
                            <span class="text-slate-500">Marks:</span>
                            <input type="number" name="marks_1" value="1" min="1" max="10" class="w-14 px-2 py-1 text-xs border border-slate-300 rounded-lg">
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Question Prompt *</label>
                        <textarea name="q_text_1" required rows="2" placeholder="e.g. Which Doppler radar parameter is most effective for distinguishing heavy rain from dry hail?" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl"></textarea>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[11px] font-bold text-slate-700 mb-1">Option A *</label>
                            <input type="text" name="op_a_1" required placeholder="Option A description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                        </div>
                        <div>
                            <label class="block text-[11px] font-bold text-slate-700 mb-1">Option B *</label>
                            <input type="text" name="op_b_1" required placeholder="Option B description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                        </div>
                        <div>
                            <label class="block text-[11px] font-bold text-slate-700 mb-1">Option C</label>
                            <input type="text" name="op_c_1" placeholder="Option C description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                        </div>
                        <div>
                            <label class="block text-[11px] font-bold text-slate-700 mb-1">Option D</label>
                            <input type="text" name="op_d_1" placeholder="Option D description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                        </div>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                        <div>
                            <label class="block text-xs font-bold text-emerald-800 mb-1">Correct Answer Key *</label>
                            <select name="correct_1" class="w-full px-3 py-2 text-xs border border-emerald-400 bg-emerald-50 rounded-xl font-bold text-emerald-900">
                                <option value="A">Option A</option>
                                <option value="B">Option B</option>
                                <option value="C">Option C</option>
                                <option value="D">Option D</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Scientific Pedagogical Explanation</label>
                            <input type="text" name="expl_1" placeholder="Why this option is physically correct (shown during post-test review)" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                        </div>
                    </div>
                </div>

                <!-- Question 2 Default -->
                <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3 question-block" data-index="2">
                    <div class="flex justify-between items-center border-b border-slate-100 pb-2">
                        <span class="font-bold text-xs text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-lg border border-emerald-200">Question #2</span>
                        <div class="flex items-center gap-2 text-xs">
                            <span class="text-slate-500">Marks:</span>
                            <input type="number" name="marks_2" value="1" min="1" max="10" class="w-14 px-2 py-1 text-xs border border-slate-300 rounded-lg">
                        </div>
                    </div>

                    <div>
                        <label class="block text-xs font-bold text-slate-700 mb-1">Question Prompt *</label>
                        <textarea name="q_text_2" required rows="2" placeholder="e.g. What is the fundamental physical relationship governed by the Doppler Dilemma in weather radars?" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl"></textarea>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div>
                            <label class="block text-[11px] font-bold text-slate-700 mb-1">Option A *</label>
                            <input type="text" name="op_a_2" required placeholder="Option A description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                        </div>
                        <div>
                            <label class="block text-[11px] font-bold text-slate-700 mb-1">Option B *</label>
                            <input type="text" name="op_b_2" required placeholder="Option B description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                        </div>
                        <div>
                            <label class="block text-[11px] font-bold text-slate-700 mb-1">Option C</label>
                            <input type="text" name="op_c_2" placeholder="Option C description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                        </div>
                        <div>
                            <label class="block text-[11px] font-bold text-slate-700 mb-1">Option D</label>
                            <input type="text" name="op_d_2" placeholder="Option D description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                        </div>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                        <div>
                            <label class="block text-xs font-bold text-emerald-800 mb-1">Correct Answer Key *</label>
                            <select name="correct_2" class="w-full px-3 py-2 text-xs border border-emerald-400 bg-emerald-50 rounded-xl font-bold text-emerald-900">
                                <option value="A">Option A</option>
                                <option value="B">Option B</option>
                                <option value="C">Option C</option>
                                <option value="D">Option D</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-700 mb-1">Scientific Pedagogical Explanation</label>
                            <input type="text" name="expl_2" placeholder="Pedagogical explanation for trainees" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <!-- Submit Strip -->
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-lg flex justify-between items-center">
            <span class="text-xs text-slate-500">Upon publishing, enrolled trainees will be able to take the timed assessment.</span>
            <button type="submit" class="px-8 py-3.5 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-white font-bold rounded-2xl shadow-lg transition text-sm flex items-center gap-2">
                <i data-lucide="check-circle" class="w-4 h-4"></i> Publish MCQ Assessment
            </button>
        </div>
    </form>
</div>

<script>
let questionCounter = 2;

function addQuestionCard() {
    questionCounter++;
    const idx = questionCounter;
    const container = document.getElementById('questionsContainer');
    
    const div = document.createElement('div');
    div.className = 'bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-3 question-block animate-fade-in';
    div.setAttribute('data-index', idx);
    div.innerHTML = `
        <div class="flex justify-between items-center border-b border-slate-100 pb-2">
            <span class="font-bold text-xs text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-lg border border-emerald-200">Question #${idx}</span>
            <div class="flex items-center gap-2 text-xs">
                <span class="text-slate-500">Marks:</span>
                <input type="number" name="marks_${idx}" value="1" min="1" max="10" class="w-14 px-2 py-1 text-xs border border-slate-300 rounded-lg">
                <button type="button" onclick="this.closest('.question-block').remove(); updateCount();" class="text-rose-500 hover:text-rose-700 ml-2">
                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
            </div>
        </div>
        <div>
            <label class="block text-xs font-bold text-slate-700 mb-1">Question Prompt *</label>
            <textarea name="q_text_${idx}" required rows="2" placeholder="Enter question description..." class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl"></textarea>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
                <label class="block text-[11px] font-bold text-slate-700 mb-1">Option A *</label>
                <input type="text" name="op_a_${idx}" required placeholder="Option A description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
            <div>
                <label class="block text-[11px] font-bold text-slate-700 mb-1">Option B *</label>
                <input type="text" name="op_b_${idx}" required placeholder="Option B description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
            <div>
                <label class="block text-[11px] font-bold text-slate-700 mb-1">Option C</label>
                <input type="text" name="op_c_${idx}" placeholder="Option C description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
            <div>
                <label class="block text-[11px] font-bold text-slate-700 mb-1">Option D</label>
                <input type="text" name="op_d_${idx}" placeholder="Option D description" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <div>
                <label class="block text-xs font-bold text-emerald-800 mb-1">Correct Answer Key *</label>
                <select name="correct_${idx}" class="w-full px-3 py-2 text-xs border border-emerald-400 bg-emerald-50 rounded-xl font-bold text-emerald-900">
                    <option value="A">Option A</option>
                    <option value="B">Option B</option>
                    <option value="C">Option C</option>
                    <option value="D">Option D</option>
                </select>
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Scientific Pedagogical Explanation</label>
                <input type="text" name="expl_${idx}" placeholder="Pedagogical explanation for trainees" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
        </div>
    `;
    container.appendChild(div);
    lucide.createIcons();
    updateCount();
}

function updateCount() {
    const blocks = document.querySelectorAll('.question-block');
    document.getElementById('questionCountDisplay').textContent = blocks.length;
}
</script>
{% endblock %}
'''

library_html = '''{% extends "base.html" %}

{% block title %}Trainer Resource Library - CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 py-8 space-y-8">
    
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full uppercase border border-emerald-200">Knowledge Repository</span>
            <h1 class="text-3xl font-black text-slate-900 mt-1">Trainer Resource Library</h1>
            <p class="text-xs text-slate-500 mt-1">Upload and manage recorded lectures, presentation decks (PPTX/PDF), and meteorological observational datasets.</p>
        </div>
        <button onclick="document.getElementById('uploadModal').classList.toggle('hidden')" class="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded-xl shadow flex items-center gap-1.5">
            <i data-lucide="upload-cloud" class="w-4 h-4"></i> Upload New Resource
        </button>
    </div>

    <!-- Resources Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for r in resources %}
            <div class="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm flex flex-col justify-between space-y-4">
                <div>
                    <div class="flex justify-between items-center mb-2">
                        <span class="bg-sky-50 text-sky-800 text-[10px] font-bold px-2 py-0.5 rounded uppercase">{{ r.category }}</span>
                        <span class="text-xs text-slate-400 font-mono">{{ r.file_size }}</span>
                    </div>

                    <h3 class="text-base font-bold text-slate-900 leading-snug">{{ r.title }}</h3>
                    <p class="text-xs text-slate-500 line-clamp-3 mt-1">{{ r.description }}</p>
                </div>

                <div class="pt-3 border-t border-slate-100 flex justify-between items-center text-xs">
                    <span class="text-slate-400 font-medium capitalize">{{ r.resource_type|replace('_', ' ') }}</span>
                    <a href="{{ r.file_url }}" target="_blank" class="px-4 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-lg text-xs flex items-center gap-1">
                        <i data-lucide="download" class="w-3.5 h-3.5"></i> Access File
                    </a>
                </div>
            </div>
        {% endfor %}
    </div>
</div>

<!-- Modal Upload -->
<div id="uploadModal" class="hidden fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-3xl p-6 sm:p-8 max-w-lg w-full border border-slate-200 shadow-2xl space-y-4">
        <div class="flex justify-between items-center">
            <h3 class="font-bold text-slate-900 text-base">Upload Training Resource</h3>
            <button onclick="document.getElementById('uploadModal').classList.add('hidden')" class="p-1 text-slate-400 hover:text-slate-600"><i data-lucide="x" class="w-5 h-5"></i></button>
        </div>
        <form action="/trainer/library/upload" method="post" class="space-y-3">
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Resource Title</label>
                <input type="text" name="title" required placeholder="e.g. INSAT-3DR Rapid Scan Radiance Processing Guide" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
            <div class="grid grid-cols-2 gap-3">
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Resource Type</label>
                    <select name="resource_type" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white">
                        <option value="presentation_ppt">Presentation Slide Deck (PPTX/PDF)</option>
                        <option value="lecture_video">Recorded Video Lecture</option>
                        <option value="study_guide_pdf">Study Guide / Manual (PDF)</option>
                        <option value="meteorological_dataset">NetCDF / GRIB2 Dataset</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 mb-1">Category / Domain</label>
                    <select name="category" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white">
                        <option value="Numerical Weather Prediction">Numerical Weather Prediction</option>
                        <option value="Radar Meteorology">Radar Meteorology</option>
                        <option value="Satellite Meteorology">Satellite Meteorology</option>
                        <option value="Cyclone Forecasting">Cyclone Forecasting</option>
                        <option value="Agrometeorology">Agrometeorology</option>
                        <option value="Seismology & Tsunami">Seismology & Tsunami</option>
                    </select>
                </div>
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">File URL / Storage Link</label>
                <input type="text" name="file_url" placeholder="/static/docs/... or Cloud Drive URL" class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl">
            </div>
            <div>
                <label class="block text-xs font-bold text-slate-700 mb-1">Description & Scientific Significance</label>
                <textarea name="description" rows="3" required placeholder="Describe what trainees will learn or test with this dataset..." class="w-full px-3 py-2 text-xs border border-slate-300 rounded-xl"></textarea>
            </div>
            <button type="submit" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-xs shadow">Save to Library</button>
        </form>
    </div>
</div>
{% endblock %}
'''

analytics_html = '''{% extends "base.html" %}

{% block title %}Trainee Analytics & Performance - Trainer Suite{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 py-8 space-y-8">
    
    <div>
        <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full uppercase border border-emerald-200">Assessment Analytics</span>
        <h1 class="text-3xl font-black text-slate-900 mt-1">Trainee Participation & Performance Metrics</h1>
        <p class="text-xs text-slate-500 mt-1">Real-time score distributions, pass rates, and question difficulty index for your course assessments.</p>
    </div>

    <!-- 3 Metrics Top Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
            <div class="text-xs text-slate-500 font-medium">Total Assessment Attempts</div>
            <div class="text-3xl font-black text-slate-900 mt-1">{{ attempts|length }}</div>
            <div class="text-xs text-emerald-600 mt-2 font-semibold">Across all active batches</div>
        </div>

        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
            <div class="text-xs text-slate-500 font-medium">Trainer Evaluation Average</div>
            <div class="text-3xl font-black text-amber-600 mt-1">{{ stats.avg_rating }} / 5.0 ★</div>
            <div class="text-xs text-amber-700 mt-2 font-semibold">Consistently high feedback</div>
        </div>

        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
            <div class="text-xs text-slate-500 font-medium">Authoring Status</div>
            <div class="text-3xl font-black text-purple-600 mt-1">{{ stats.total_courses }} Courses</div>
            <div class="text-xs text-purple-700 mt-2 font-semibold">{{ stats.total_quizzes }} Questionnaires Published</div>
        </div>
    </div>

    <!-- Attempts Table -->
    <div class="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200 shadow-sm space-y-4">
        <h3 class="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
            <i data-lucide="list-ordered" class="w-4 h-4 text-sky-600"></i> Trainee Attempt Roster
        </h3>

        <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
                <thead>
                    <tr class="border-b border-slate-200 text-slate-400 uppercase text-[10px]">
                        <th class="py-3 px-4">Trainee Name</th>
                        <th class="py-3 px-4">Department / Observatory</th>
                        <th class="py-3 px-4">Assessment Title</th>
                        <th class="py-3 px-4">Score</th>
                        <th class="py-3 px-4">Percentage</th>
                        <th class="py-3 px-4">Status</th>
                        <th class="py-3 px-4">Attempt Date</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    {% for a in attempts %}
                        <tr class="hover:bg-slate-50 transition">
                            <td class="py-3 px-4 font-bold text-slate-900">{{ a.trainee_name }}</td>
                            <td class="py-3 px-4 text-slate-500">{{ a.trainee_department }}</td>
                            <td class="py-3 px-4 text-slate-700 font-medium">{{ a.quiz_title }}</td>
                            <td class="py-3 px-4 font-bold">{{ a.score }} / {{ a.total_marks }}</td>
                            <td class="py-3 px-4 font-bold text-slate-900">{{ a.percentage }}%</td>
                            <td class="py-3 px-4">
                                {% if a.is_passed %}
                                    <span class="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full">Passed</span>
                                {% else %}
                                    <span class="bg-rose-100 text-rose-800 text-[10px] font-bold px-2 py-0.5 rounded-full">Needs Retake</span>
                                {% endif %}
                            </td>
                            <td class="py-3 px-4 text-slate-400 font-mono">{{ a.attempted_at[:10] }}</td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
'''

with open("app/templates/trainer/create_quiz.html", "w", encoding="utf-8") as f:
    f.write(create_quiz_html)

with open("app/templates/trainer/library.html", "w", encoding="utf-8") as f:
    f.write(library_html)

with open("app/templates/trainer/analytics.html", "w", encoding="utf-8") as f:
    f.write(analytics_html)

print("Trainer templates Part 2 created successfully")
