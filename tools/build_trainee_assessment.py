import os

assessment_html = '''{% extends "base.html" %}

{% block title %}Timed Assessment: {{ quiz.title }} - CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto px-4 py-8 space-y-6">
    
    <!-- Assessment Banner with Timer -->
    <div class="bg-gradient-to-r from-moes-navy via-slate-900 to-sky-950 text-white p-6 rounded-3xl shadow-xl border border-sky-800/50 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 sticky top-20 z-30 backdrop-blur-md">
        <div>
            <span class="bg-emerald-500/20 text-emerald-300 text-[10px] font-bold px-2.5 py-0.5 rounded-full border border-emerald-500/30 uppercase">Live MCQ Assessment</span>
            <h1 class="text-xl font-bold text-white mt-1">{{ quiz.title }}</h1>
            <p class="text-xs text-slate-300">{{ quiz.course_title }} &bull; Passing mark: {{ quiz.pass_percentage }}%</p>
        </div>

        <!-- Live Countdown Timer -->
        <div class="flex items-center gap-3 bg-slate-900/90 border border-slate-700 px-4 py-2 rounded-2xl shadow-inner">
            <i data-lucide="timer" class="w-6 h-6 text-amber-400 animate-pulse"></i>
            <div>
                <div class="text-[10px] text-slate-400 font-bold uppercase">Time Remaining</div>
                <div id="timerClock" class="font-mono text-xl font-black text-amber-400">20:00</div>
            </div>
        </div>
    </div>

    <!-- Assessment Form -->
    <form id="quizForm" action="/trainee/assessment/{{ quiz.id }}/submit" method="post" class="space-y-6">
        
        {% for q in questions %}
            <div class="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4 question-card" id="q_card_{{ loop.index }}">
                <div class="flex justify-between items-start gap-4">
                    <span class="w-8 h-8 rounded-xl bg-sky-100 text-sky-800 font-black text-xs flex items-center justify-center shrink-0">
                        {{ loop.index }}
                    </span>
                    <p class="text-sm font-bold text-slate-900 leading-relaxed flex-1">
                        {{ q.question_text }}
                    </p>
                    <span class="text-[10px] text-slate-400 font-mono shrink-0">{{ q.marks }} Mark</span>
                </div>

                <!-- 4 Radio Options -->
                <div class="space-y-2.5 pt-2 pl-12">
                    <label class="flex items-center p-3 rounded-2xl border border-slate-200 hover:bg-sky-50/50 hover:border-sky-300 cursor-pointer transition has-[:checked]:border-sky-600 has-[:checked]:bg-sky-50">
                        <input type="radio" name="question_{{ q.id }}" value="A" class="w-4 h-4 text-sky-600 focus:ring-sky-500 mr-3">
                        <span class="text-xs font-semibold text-slate-800">A) {{ q.option_a }}</span>
                    </label>

                    <label class="flex items-center p-3 rounded-2xl border border-slate-200 hover:bg-sky-50/50 hover:border-sky-300 cursor-pointer transition has-[:checked]:border-sky-600 has-[:checked]:bg-sky-50">
                        <input type="radio" name="question_{{ q.id }}" value="B" class="w-4 h-4 text-sky-600 focus:ring-sky-500 mr-3">
                        <span class="text-xs font-semibold text-slate-800">B) {{ q.option_b }}</span>
                    </label>

                    {% if q.option_c %}
                        <label class="flex items-center p-3 rounded-2xl border border-slate-200 hover:bg-sky-50/50 hover:border-sky-300 cursor-pointer transition has-[:checked]:border-sky-600 has-[:checked]:bg-sky-50">
                            <input type="radio" name="question_{{ q.id }}" value="C" class="w-4 h-4 text-sky-600 focus:ring-sky-500 mr-3">
                            <span class="text-xs font-semibold text-slate-800">C) {{ q.option_c }}</span>
                        </label>
                    {% endif %}

                    {% if q.option_d %}
                        <label class="flex items-center p-3 rounded-2xl border border-slate-200 hover:bg-sky-50/50 hover:border-sky-300 cursor-pointer transition has-[:checked]:border-sky-600 has-[:checked]:bg-sky-50">
                            <input type="radio" name="question_{{ q.id }}" value="D" class="w-4 h-4 text-sky-600 focus:ring-sky-500 mr-3">
                            <span class="text-xs font-semibold text-slate-800">D) {{ q.option_d }}</span>
                        </label>
                    {% endif %}
                </div>
            </div>
        {% endfor %}

        <!-- Bottom Submit Strip -->
        <div class="bg-white p-6 rounded-3xl border border-slate-200 shadow-lg flex flex-col sm:flex-row justify-between items-center gap-4">
            <div class="text-xs text-slate-500">
                Please verify all answered questions before submitting. Passing threshold: <strong>{{ quiz.pass_percentage }}%</strong>.
            </div>
            <button type="submit" onclick="return confirm('Are you sure you want to submit your assessment answers now?')" class="px-8 py-3.5 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-white font-bold rounded-2xl shadow-lg shadow-emerald-600/30 transition text-sm flex items-center gap-2">
                <i data-lucide="send" class="w-4 h-4"></i> Submit Final Assessment
            </button>
        </div>
    </form>
</div>

<script>
// Timer Countdown
let durationMinutes = {{ quiz.duration_mins or 20 }};
let totalSeconds = durationMinutes * 60;
const timerEl = document.getElementById('timerClock');

const countdown = setInterval(() => {
    totalSeconds--;
    if (totalSeconds <= 0) {
        clearInterval(countdown);
        alert('Time has expired! Submitting your answers automatically.');
        document.getElementById('quizForm').submit();
        return;
    }
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    timerEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    
    if (totalSeconds < 120) {
        timerEl.classList.remove('text-amber-400');
        timerEl.classList.add('text-rose-400');
    }
}, 1000);
</script>
{% endblock %}
'''

assessment_result_html = '''{% extends "base.html" %}

{% block title %}Assessment Result - CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto px-4 py-10 space-y-8">
    
    <!-- Scorecard Header -->
    <div class="bg-white rounded-3xl p-8 border border-slate-200 shadow-xl text-center space-y-4 relative overflow-hidden">
        
        {% if attempt.is_passed %}
            <div class="w-20 h-20 rounded-3xl bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto shadow-inner">
                <i data-lucide="award" class="w-10 h-10"></i>
            </div>
            <span class="bg-emerald-100 text-emerald-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                Assessment Passed Successfully
            </span>
            <h1 class="text-3xl font-black text-slate-900">Congratulations, {{ user.full_name }}!</h1>
            <p class="text-xs text-slate-500 max-w-md mx-auto">You have demonstrated high proficiency in <strong>{{ attempt.course_title }}</strong>.</p>
            
            <div class="flex justify-center items-center gap-6 py-4">
                <div class="text-center">
                    <div class="text-xs text-slate-400 font-medium">Your Score</div>
                    <div class="text-4xl font-black text-emerald-600">{{ attempt.score }} / {{ attempt.total_marks }}</div>
                </div>
                <div class="h-10 w-px bg-slate-200"></div>
                <div class="text-center">
                    <div class="text-xs text-slate-400 font-medium">Percentage</div>
                    <div class="text-4xl font-black text-slate-900">{{ attempt.percentage }}%</div>
                </div>
                <div class="h-10 w-px bg-slate-200"></div>
                <div class="text-center">
                    <div class="text-xs text-slate-400 font-medium">Passing Required</div>
                    <div class="text-4xl font-black text-slate-400">{{ attempt.pass_percentage }}%</div>
                </div>
            </div>

            {% if certificate %}
                <div class="pt-2">
                    <a href="/trainee/certificate/{{ certificate.certificate_id }}" class="inline-flex items-center gap-2 px-8 py-3.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-bold rounded-2xl shadow-xl shadow-amber-500/30 transition text-sm">
                        <i data-lucide="award" class="w-5 h-5"></i> View & Download MoES Digital Certificate
                    </a>
                </div>
            {% endif %}

        {% else %}
            <div class="w-20 h-20 rounded-3xl bg-amber-100 text-amber-700 flex items-center justify-center mx-auto shadow-inner">
                <i data-lucide="alert-circle" class="w-10 h-10"></i>
            </div>
            <span class="bg-amber-100 text-amber-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                Threshold Not Met
            </span>
            <h1 class="text-3xl font-black text-slate-900">Score: {{ attempt.percentage }}%</h1>
            <p class="text-xs text-slate-500 max-w-md mx-auto">Passing threshold for certification is {{ attempt.pass_percentage }}%. Review the detailed question explanations below and retake the assessment when ready.</p>
            
            <div class="pt-4 flex justify-center gap-3">
                <a href="/trainee/assessment/{{ attempt.quiz_id }}" class="px-6 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-xl text-xs shadow">
                    Retake Assessment
                </a>
                <a href="/trainee/courses/{{ attempt.course_id }}" class="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-xl text-xs">
                    Return to Course Material
                </a>
            </div>
        {% endif %}
    </div>

    <!-- Question-by-Question Review with Scientific Explanations -->
    <div class="space-y-4">
        <h2 class="text-lg font-black text-slate-900 flex items-center gap-2">
            <i data-lucide="check-square" class="w-5 h-5 text-sky-600"></i> Pedagogical Answer Review & Explanations
        </h2>

        {% for q in questions %}
            <div class="bg-white p-6 rounded-3xl border {% if q.is_correct %}border-emerald-300 bg-emerald-50/10{% else %}border-rose-300 bg-rose-50/10{% endif %} shadow-sm space-y-3">
                <div class="flex justify-between items-start gap-3">
                    <span class="w-7 h-7 rounded-lg {% if q.is_correct %}bg-emerald-100 text-emerald-800{% else %}bg-rose-100 text-rose-800{% endif %} font-bold text-xs flex items-center justify-center shrink-0">
                        {{ loop.index }}
                    </span>
                    <p class="text-xs font-bold text-slate-900 flex-1 leading-relaxed">
                        {{ q.question_text }}
                    </p>
                    {% if q.is_correct %}
                        <span class="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                            <i data-lucide="check" class="w-3 h-3"></i> Correct
                        </span>
                    {% else %}
                        <span class="bg-rose-100 text-rose-800 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                            <i data-lucide="x" class="w-3 h-3"></i> Incorrect
                        </span>
                    {% endif %}
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs pl-10">
                    <div class="p-2.5 rounded-xl border border-slate-200 {% if q.user_selected == 'A' and q.is_correct %}bg-emerald-100/70 border-emerald-400{% elif q.user_selected == 'A' and not q.is_correct %}bg-rose-100/70 border-rose-400{% elif q.correct_option == 'A' %}bg-emerald-50 border-emerald-300 font-bold{% endif %}">
                        A) {{ q.option_a }}
                    </div>
                    <div class="p-2.5 rounded-xl border border-slate-200 {% if q.user_selected == 'B' and q.is_correct %}bg-emerald-100/70 border-emerald-400{% elif q.user_selected == 'B' and not q.is_correct %}bg-rose-100/70 border-rose-400{% elif q.correct_option == 'B' %}bg-emerald-50 border-emerald-300 font-bold{% endif %}">
                        B) {{ q.option_b }}
                    </div>
                    {% if q.option_c %}
                        <div class="p-2.5 rounded-xl border border-slate-200 {% if q.user_selected == 'C' and q.is_correct %}bg-emerald-100/70 border-emerald-400{% elif q.user_selected == 'C' and not q.is_correct %}bg-rose-100/70 border-rose-400{% elif q.correct_option == 'C' %}bg-emerald-50 border-emerald-300 font-bold{% endif %}">
                            C) {{ q.option_c }}
                        </div>
                    {% endif %}
                    {% if q.option_d %}
                        <div class="p-2.5 rounded-xl border border-slate-200 {% if q.user_selected == 'D' and q.is_correct %}bg-emerald-100/70 border-emerald-400{% elif q.user_selected == 'D' and not q.is_correct %}bg-rose-100/70 border-rose-400{% elif q.correct_option == 'D' %}bg-emerald-50 border-emerald-300 font-bold{% endif %}">
                            D) {{ q.option_d }}
                        </div>
                    {% endif %}
                </div>

                <!-- Explanation -->
                {% if q.explanation %}
                    <div class="mt-2 ml-10 p-3 bg-sky-50 rounded-2xl border border-sky-200 text-xs text-sky-950">
                        <strong class="text-sky-800">Scientific Explanation:</strong> {{ q.explanation }}
                    </div>
                {% endif %}
            </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
'''

certificate_html = '''{% extends "base.html" %}

{% block title %}Official Certificate - {{ certificate.certificate_id }} - MoES / IMD{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto px-4 py-8 space-y-6">
    
    <!-- Action Bar (Non-Printable) -->
    <div class="flex justify-between items-center bg-white p-4 rounded-2xl border border-slate-200 shadow-sm print:hidden">
        <a href="/trainee/dashboard" class="text-xs font-bold text-slate-600 hover:text-slate-900 flex items-center gap-1.5">
            <i data-lucide="arrow-left" class="w-4 h-4"></i> Back to Dashboard
        </a>
        <div class="flex items-center gap-2">
            <button onclick="window.print()" class="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold rounded-xl shadow transition flex items-center gap-2">
                <i data-lucide="printer" class="w-4 h-4"></i> Print Certificate
            </button>
        </div>
    </div>

    <!-- Official Government Certificate Document -->
    <div class="bg-white p-8 sm:p-14 rounded-3xl border-8 border-double border-amber-600/80 shadow-2xl relative overflow-hidden certificate-printable" id="certificateNode">
        
        <!-- Watermark Background -->
        <div class="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none">
            <i data-lucide="satellite" class="w-96 h-96 text-slate-900"></i>
        </div>

        <div class="relative z-10 text-center space-y-6">
            
            <!-- Government Header Insignia -->
            <div class="space-y-1">
                <p class="text-xs uppercase font-bold tracking-widest text-slate-500">Government of India &bull; भारत सरकार</p>
                <h2 class="text-base sm:text-lg font-black tracking-wider text-slate-900 uppercase">Ministry of Earth Sciences</h2>
                <h3 class="text-sm font-bold text-sky-800 uppercase tracking-wide">India Meteorological Department (IMD)</h3>
                <p class="text-[11px] text-amber-700 italic font-serif">"आदित्यात् जायते वृष्टिः" &bull; Training & Capacity Building Directorate</p>
            </div>

            <div class="w-24 h-1 bg-gradient-to-r from-orange-500 via-amber-500 to-green-600 mx-auto rounded-full"></div>

            <!-- Certificate Title -->
            <div class="py-2">
                <h1 class="text-2xl sm:text-4xl font-serif font-black text-slate-900 tracking-wide uppercase">
                    Certificate of Competency
                </h1>
                <p class="text-xs text-slate-500 mt-1 uppercase tracking-widest font-sans">This is to certify that</p>
            </div>

            <!-- Recipient Name -->
            <div class="py-2">
                <div class="text-2xl sm:text-3xl font-serif font-black text-sky-950 underline decoration-amber-500 decoration-2 underline-offset-8">
                    {{ certificate.trainee_name }}
                </div>
                <p class="text-xs text-slate-600 mt-3 font-medium">
                    {{ certificate.trainee_designation or "Meteorological Officer" }}, {{ certificate.trainee_department or "India Meteorological Department" }}
                </p>
            </div>

            <p class="text-xs sm:text-sm text-slate-700 max-w-2xl mx-auto leading-relaxed font-serif">
                has successfully completed the comprehensive operational training program and demonstrated distinguished proficiency in the specialized capacity-building curriculum titled:
            </p>

            <!-- Course Title Highlight -->
            <div class="bg-gradient-to-r from-sky-50 via-amber-50 to-sky-50 py-3 px-6 rounded-2xl border border-amber-200/80 max-w-2xl mx-auto">
                <h4 class="text-base sm:text-lg font-bold text-slate-900">
                    {{ certificate.course_title }}
                </h4>
                <p class="text-xs font-mono text-slate-500 mt-0.5">
                    Course Code: {{ certificate.course_code }} &bull; Domain: {{ certificate.course_domain }} ({{ certificate.duration_hours }} Hours)
                </p>
            </div>

            <!-- Performance Metrics -->
            <div class="flex justify-center items-center gap-8 text-xs py-2">
                <div>
                    <span class="text-slate-400 block text-[10px] uppercase">Grade Awarded</span>
                    <strong class="text-emerald-700 text-sm font-bold">{{ certificate.grade }}</strong>
                </div>
                <div class="h-6 w-px bg-slate-200"></div>
                <div>
                    <span class="text-slate-400 block text-[10px] uppercase">Assessment Score</span>
                    <strong class="text-slate-900 text-sm font-bold">{{ certificate.score_percentage }}%</strong>
                </div>
                <div class="h-6 w-px bg-slate-200"></div>
                <div>
                    <span class="text-slate-400 block text-[10px] uppercase">Date of Issue</span>
                    <strong class="text-slate-900 text-sm font-bold">{{ certificate.issue_date }}</strong>
                </div>
            </div>

            <!-- Signatures & QR Code Section -->
            <div class="pt-8 border-t border-slate-200 grid grid-cols-3 gap-4 items-end text-center">
                
                <!-- Left Signature -->
                <div class="space-y-1">
                    <div class="font-serif italic text-slate-700 text-xs">Dr. Madhavan Sharma</div>
                    <div class="w-32 h-px bg-slate-400 mx-auto"></div>
                    <div class="text-[10px] font-bold text-slate-800 uppercase">Lead Course Instructor</div>
                    <div class="text-[9px] text-slate-500">Scientist-G, IMD</div>
                </div>

                <!-- Center QR Code -->
                <div class="flex flex-col items-center justify-center space-y-1">
                    <!-- SVG Dynamic QR Representation -->
                    <div class="p-2 bg-white border border-slate-300 rounded-xl shadow-sm">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=90x90&data={{ certificate.qr_data|urlencode }}" alt="Verification QR" class="w-16 h-16 sm:w-20 sm:h-20">
                    </div>
                    <span class="text-[9px] font-mono text-slate-600 font-bold uppercase tracking-wider">{{ certificate.certificate_id }}</span>
                    <a href="/verify/certificate/{{ certificate.certificate_id }}" target="_blank" class="text-[9px] text-sky-700 hover:underline">Scan to Verify Authenticity</a>
                </div>

                <!-- Right Signature -->
                <div class="space-y-1">
                    <div class="font-serif italic text-slate-700 text-xs">Dr. Rajeshwar Rao</div>
                    <div class="w-32 h-px bg-slate-400 mx-auto"></div>
                    <div class="text-[10px] font-bold text-slate-800 uppercase">Director of Capacity Building</div>
                    <div class="text-[9px] text-slate-500">Ministry of Earth Sciences</div>
                </div>
            </div>

        </div>
    </div>
</div>
{% endblock %}
'''

with open("app/templates/trainee/assessment.html", "w", encoding="utf-8") as f:
    f.write(assessment_html)

with open("app/templates/trainee/assessment_result.html", "w", encoding="utf-8") as f:
    f.write(assessment_result_html)

with open("app/templates/trainee/certificate.html", "w", encoding="utf-8") as f:
    f.write(certificate_html)

print("Trainee templates Part 2 (assessment, result, certificate) created successfully")
