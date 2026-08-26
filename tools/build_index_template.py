import os

index_html = '''{% extends "base.html" %}

{% block title %}CAPACITY CONNECT - MoES & IMD Digital Capacity Building Portal{% endblock %}

{% block content %}
<!-- Hero Section -->
<section class="relative bg-gradient-to-br from-moes-navy via-slate-900 to-sky-950 text-white overflow-hidden py-16 lg:py-24 border-b border-sky-900/40">
    <div class="absolute inset-0 opacity-10 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:16px_16px]"></div>
    
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            <!-- Left Hero Content -->
            <div class="lg:col-span-7 space-y-6 text-center lg:text-left">
                <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-sky-500/20 border border-sky-400/30 text-sky-300 text-xs font-semibold">
                    <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                    Mission Mausam & MoES Digital Capacity Initiative
                </div>
                
                <h1 class="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-tight">
                    Empowering Earth Science & <span class="text-transparent bg-clip-text bg-gradient-to-r from-sky-400 via-teal-300 to-amber-400">Meteorological Excellence</span>
                </h1>
                
                <p class="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto lg:mx-0 leading-relaxed font-light">
                    A centralized portal for competency development, operational training, interactive assessments, and expert competency mapping across the <strong class="text-white">Ministry of Earth Sciences (MoES)</strong> and <strong class="text-white">India Meteorological Department (IMD)</strong>.
                </p>

                <!-- Action CTAs -->
                <div class="flex flex-wrap justify-center lg:justify-start gap-4 pt-2">
                    <a href="/trainee/courses" class="px-6 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-bold shadow-lg shadow-sky-500/30 hover:scale-105 transition flex items-center gap-2">
                        <i data-lucide="compass" class="w-5 h-5"></i> Explore Course Catalog
                    </a>
                    
                    {% if not user %}
                        <a href="/auth/login" class="px-6 py-3.5 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-white font-semibold border border-slate-700 shadow hover:scale-105 transition flex items-center gap-2">
                            <i data-lucide="log-in" class="w-5 h-5"></i> Officer Login
                        </a>
                    {% else %}
                        <a href="/trainee/dashboard" class="px-6 py-3.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold shadow hover:scale-105 transition flex items-center gap-2">
                            <i data-lucide="layout-dashboard" class="w-5 h-5"></i> Go to Dashboard
                        </a>
                    {% endif %}

                    <a href="/verify/certificate/IMD-CB-2026-8921" class="px-5 py-3.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/30 font-medium transition flex items-center gap-2 text-sm">
                        <i data-lucide="shield-check" class="w-4 h-4"></i> Verify Certificate
                    </a>
                </div>

                <!-- 1-Click Demo Notice -->
                <div class="pt-2">
                    <button onclick="document.getElementById('demoModal').classList.toggle('hidden')" class="inline-flex items-center gap-2 text-xs text-amber-300 hover:text-amber-200 underline font-medium">
                        <i data-lucide="sparkles" class="w-3.5 h-3.5"></i> Test Demo Personas (Admin / Trainer / Trainee)
                    </button>
                </div>
            </div>

            <!-- Right Hero Interactive Card -->
            <div class="lg:col-span-5">
                <div class="bg-slate-800/80 backdrop-blur-md rounded-2xl p-6 border border-slate-700 shadow-2xl space-y-6">
                    <div class="flex items-center justify-between border-b border-slate-700/80 pb-4">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-xl bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold">
                                <i data-lucide="activity" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <h3 class="text-sm font-bold text-white uppercase tracking-wider">MoES Capacity Matrix</h3>
                                <p class="text-xs text-slate-400">Real-time Portal Training Indicators</p>
                            </div>
                        </div>
                        <span class="bg-emerald-500/20 text-emerald-300 text-xs px-2.5 py-1 rounded-full font-bold border border-emerald-500/30">Active</span>
                    </div>

                    <!-- 4 Live Stats -->
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-700/60">
                            <div class="text-xs text-slate-400 font-medium mb-1">Trainees Enrolled</div>
                            <div class="text-2xl font-black text-white">{{ stats.trainees }}+</div>
                            <div class="text-[10px] text-emerald-400 mt-1 flex items-center gap-1">
                                <i data-lucide="trending-up" class="w-3 h-3"></i> Across 6 RMCs & NCS
                            </div>
                        </div>

                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-700/60">
                            <div class="text-xs text-slate-400 font-medium mb-1">Domain Courses</div>
                            <div class="text-2xl font-black text-sky-400">{{ stats.courses }}</div>
                            <div class="text-[10px] text-sky-300 mt-1">Radar, NWP, Satellite, Agro</div>
                        </div>

                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-700/60">
                            <div class="text-xs text-slate-400 font-medium mb-1">Certificates Issued</div>
                            <div class="text-2xl font-black text-amber-400">{{ stats.certificates }}+</div>
                            <div class="text-[10px] text-amber-300 mt-1">Verifiable QR Credentials</div>
                        </div>

                        <div class="bg-slate-900/60 p-4 rounded-xl border border-slate-700/60">
                            <div class="text-xs text-slate-400 font-medium mb-1">Expert Trainers</div>
                            <div class="text-2xl font-black text-purple-400">{{ stats.trainers }}+</div>
                            <div class="text-[10px] text-purple-300 mt-1">Scientist-E/F/G & Faculty</div>
                        </div>
                    </div>

                    <!-- Competency Mapping Feature Teaser -->
                    <div class="p-3.5 bg-gradient-to-r from-amber-500/10 to-orange-500/10 rounded-xl border border-amber-500/30 flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <i data-lucide="git-merge" class="w-5 h-5 text-amber-400"></i>
                            <div>
                                <div class="text-xs font-bold text-white">Smart Competency Mapping</div>
                                <div class="text-[11px] text-slate-300">Automated Trainer-to-Subject Matching</div>
                            </div>
                        </div>
                        <a href="/admin/competency-map" class="text-xs font-bold text-amber-400 hover:text-amber-300">Explore &rarr;</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Live Announcements & Circulars Banner -->
<section class="bg-amber-50 border-y border-amber-200 py-3">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center gap-3 overflow-hidden">
        <span class="bg-amber-600 text-white text-[11px] uppercase font-bold px-2.5 py-1 rounded flex items-center gap-1.5 shrink-0 shadow-sm">
            <i data-lucide="megaphone" class="w-3.5 h-3.5"></i> Notice Board
        </span>
        <div class="flex-1 overflow-x-auto whitespace-nowrap scrollbar-none flex items-center gap-8 text-xs text-slate-700 font-medium">
            {% for a in announcements %}
                <span class="inline-flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                    <strong class="text-slate-900">[{{ a.category }}]</strong> {{ a.title }}
                </span>
            {% endfor %}
        </div>
        <a href="/admin/announcements" class="text-xs text-amber-800 font-bold hover:underline shrink-0 hidden sm:block">View All</a>
    </div>
</section>

<!-- 3 Role Portals Breakdown -->
<section class="py-16 bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center max-w-3xl mx-auto mb-12">
            <h2 class="text-xs font-bold uppercase tracking-wider text-sky-600 mb-2">Integrated Three-Tier Framework</h2>
            <h3 class="text-3xl font-black text-slate-900 tracking-tight">Tailored Capacity Building for Every Role</h3>
            <p class="text-sm text-slate-600 mt-3">From field meteorology observers to senior climate research scientists and administrative directors, CAPACITY CONNECT bridges competency gaps seamlessly.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Trainee -->
            <div class="bg-slate-50 rounded-2xl p-8 border border-slate-200 hover:border-sky-300 hover:shadow-xl transition group">
                <div class="w-14 h-14 rounded-2xl bg-sky-100 text-sky-700 flex items-center justify-center mb-6 group-hover:scale-110 transition shadow-inner">
                    <i data-lucide="graduation-cap" class="w-7 h-7"></i>
                </div>
                <h4 class="text-xl font-bold text-slate-900 mb-2">Trainee Module</h4>
                <p class="text-xs text-slate-600 leading-relaxed mb-6">
                    Meteorologists, Scientific Assistants, and Observers create professional profiles, enroll in specialized courses, study interactive video/PPT modules, attempt timed MCQ assessments, and earn verifiable digital certificates.
                </p>
                <ul class="space-y-2.5 text-xs text-slate-700 mb-6">
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-sky-600"></i> Professional Profile & Skills Matrix</li>
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-sky-600"></i> Subject-wise Timed MCQ Assessments</li>
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-sky-600"></i> QR-Verified MoES Certifications</li>
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-sky-600"></i> Course & Trainer Feedback System</li>
                </ul>
                <a href="/trainee/courses" class="inline-flex items-center text-xs font-bold text-sky-600 hover:text-sky-700 group-hover:translate-x-1 transition">
                    Access Trainee Hub &rarr;
                </a>
            </div>

            <!-- Trainer -->
            <div class="bg-slate-50 rounded-2xl p-8 border border-slate-200 hover:border-emerald-300 hover:shadow-xl transition group">
                <div class="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center mb-6 group-hover:scale-110 transition shadow-inner">
                    <i data-lucide="presentation" class="w-7 h-7"></i>
                </div>
                <h4 class="text-xl font-bold text-slate-900 mb-2">Trainer Suite</h4>
                <p class="text-xs text-slate-600 leading-relaxed mb-6">
                    Subject matter experts, senior scientists, and professors author specialized curricula, build MCQ assessments with custom deadlines, upload recorded lectures and study materials into the Trainer Library, and monitor trainee participation.
                </p>
                <ul class="space-y-2.5 text-xs text-slate-700 mb-6">
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-600"></i> Interactive MCQ Questionnaire Builder</li>
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-600"></i> Recorded Lectures & Resource Library</li>
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-600"></i> Trainee Progress & Roster Tracking</li>
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-emerald-600"></i> Detailed Question Difficulty Analytics</li>
                </ul>
                <a href="/trainer/dashboard" class="inline-flex items-center text-xs font-bold text-emerald-600 hover:text-emerald-700 group-hover:translate-x-1 transition">
                    Enter Trainer Suite &rarr;
                </a>
            </div>

            <!-- Admin -->
            <div class="bg-slate-50 rounded-2xl p-8 border border-slate-200 hover:border-purple-300 hover:shadow-xl transition group">
                <div class="w-14 h-14 rounded-2xl bg-purple-100 text-purple-700 flex items-center justify-center mb-6 group-hover:scale-110 transition shadow-inner">
                    <i data-lucide="shield-check" class="w-7 h-7"></i>
                </div>
                <h4 class="text-xl font-bold text-slate-900 mb-2">Admin Command</h4>
                <p class="text-xs text-slate-600 leading-relaxed mb-6">
                    MoES Training Directors and Capacity Building Administrators oversee user approvals, manage role permissions, monitor national training dashboards, execute Competency Mapping algorithms, and publish official announcements.
                </p>
                <ul class="space-y-2.5 text-xs text-slate-700 mb-6">
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-purple-600"></i> User Approval & Role Switcher</li>
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-purple-600"></i> AI Trainer Competency Mapping Engine</li>
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-purple-600"></i> Regional Observatory Analytics</li>
                    <li class="flex items-center gap-2"><i data-lucide="check-circle-2" class="w-4 h-4 text-purple-600"></i> Homepage Bulletin & Circular Manager</li>
                </ul>
                <a href="/admin/dashboard" class="inline-flex items-center text-xs font-bold text-purple-600 hover:text-purple-700 group-hover:translate-x-1 transition">
                    Open Admin Center &rarr;
                </a>
            </div>
        </div>
    </div>
</section>

<!-- Featured Courses Grid -->
<section class="py-16 bg-slate-100 border-t border-slate-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-end mb-10 gap-4">
            <div>
                <h2 class="text-xs font-bold uppercase tracking-wider text-sky-600 mb-1">Operational Curricula</h2>
                <h3 class="text-2xl sm:text-3xl font-black text-slate-900">Featured Capacity Building Programs</h3>
            </div>
            <a href="/trainee/courses" class="text-xs font-bold text-sky-600 hover:text-sky-700 flex items-center gap-1">
                View All Courses <i data-lucide="arrow-right" class="w-4 h-4"></i>
            </a>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for c in featured_courses %}
                <div class="bg-white rounded-2xl overflow-hidden border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col">
                    <div class="p-6 flex-1 flex flex-col">
                        <div class="flex items-center justify-between gap-2 mb-3">
                            <span class="bg-sky-50 text-sky-700 text-[11px] font-bold px-2.5 py-1 rounded-full border border-sky-200">
                                {{ c.domain }}
                            </span>
                            <span class="text-slate-400 text-xs font-semibold flex items-center gap-1">
                                <i data-lucide="clock" class="w-3.5 h-3.5"></i> {{ c.duration_hours }} Hours
                            </span>
                        </div>

                        <h4 class="font-bold text-slate-900 text-base leading-snug mb-2 hover:text-sky-600 transition">
                            <a href="/trainee/courses/{{ c.id }}">{{ c.title }}</a>
                        </h4>

                        <p class="text-xs text-slate-500 line-clamp-2 leading-relaxed mb-4 flex-1">
                            {{ c.description }}
                        </p>

                        <div class="pt-4 border-t border-slate-100 flex items-center justify-between text-xs">
                            <div>
                                <span class="text-slate-400 block text-[10px]">Trainer</span>
                                <span class="font-semibold text-slate-800">{{ c.trainer_name or "MoES Faculty" }}</span>
                            </div>
                            <a href="/trainee/courses/{{ c.id }}" class="bg-sky-600 hover:bg-sky-500 text-white font-bold px-3 py-1.5 rounded-lg shadow-sm transition">
                                Start Learning
                            </a>
                        </div>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>
</section>

<!-- Competency Mapping Engine Highlight Banner -->
<section class="py-16 bg-moes-navy text-white relative overflow-hidden">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="bg-gradient-to-r from-sky-900/60 to-blue-900/60 p-8 sm:p-12 rounded-3xl border border-sky-700/50 backdrop-blur-sm grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div class="lg:col-span-8 space-y-4">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-400/20 text-amber-300 text-xs font-bold border border-amber-400/30">
                    <i data-lucide="cpu" class="w-3.5 h-3.5"></i> Intelligent Resource Allocation
                </div>
                <h3 class="text-2xl sm:text-4xl font-black tracking-tight leading-tight">
                    Automated Competency Mapping Engine
                </h3>
                <p class="text-sm text-slate-300 leading-relaxed font-light">
                    Identifying the best-suited meteorological trainer for new technical courses used to be a manual challenge. CAPACITY CONNECT uses an algorithmic competency matching score evaluating skill overlap, observational experience, research publications, and trainee feedback ratings to rank top trainers in real time.
                </p>
                <div class="pt-2">
                    <a href="/admin/competency-map" class="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold shadow transition">
                        <i data-lucide="git-merge" class="w-4 h-4"></i> Launch Competency Matcher
                    </a>
                </div>
            </div>
            <div class="lg:col-span-4 bg-slate-900/80 rounded-2xl p-5 border border-slate-700 space-y-3 text-xs">
                <div class="font-bold text-sky-400 uppercase tracking-wider text-[11px] mb-2">Live Match Simulation:</div>
                <div class="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700 flex justify-between items-center">
                    <div>
                        <div class="font-bold text-white">Dr. Madhavan Sharma</div>
                        <div class="text-[10px] text-slate-400">NWP & WRF Modeling</div>
                    </div>
                    <span class="text-xs font-black text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded">94.5% Fit</span>
                </div>
                <div class="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700 flex justify-between items-center">
                    <div>
                        <div class="font-bold text-white">Dr. Ananya Das</div>
                        <div class="text-[10px] text-slate-400">Radar & Severe Storms</div>
                    </div>
                    <span class="text-xs font-black text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded">91.0% Fit</span>
                </div>
                <div class="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700 flex justify-between items-center">
                    <div>
                        <div class="font-bold text-white">Dr. R. Venkatesh</div>
                        <div class="text-[10px] text-slate-400">INSAT-3DR & Cyclones</div>
                    </div>
                    <span class="text-xs font-black text-sky-400 bg-sky-500/20 px-2 py-0.5 rounded">88.5% Fit</span>
                </div>
            </div>
        </div>
    </div>
</section>
{% endblock %}
'''

verify_html = '''{% extends "base.html" %}

{% block title %}Verify Certificate - MoES / IMD CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto px-4 py-12">
    <div class="text-center mb-8">
        <span class="bg-sky-100 text-sky-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
            Official Credential Verification
        </span>
        <h1 class="text-3xl font-black text-slate-900 mt-2">Ministry of Earth Sciences / IMD Certificate Validator</h1>
        <p class="text-sm text-slate-500 mt-1">Verify authenticity of digital capacity building certificates issued by the MoES Training Directorate</p>
    </div>

    <!-- Search Form -->
    <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm mb-8">
        <form action="" method="get" class="flex flex-col sm:flex-row gap-3">
            <div class="relative flex-1">
                <i data-lucide="search" class="w-5 h-5 text-slate-400 absolute left-3 top-3.5"></i>
                <input type="text" id="certInput" placeholder="Enter Certificate ID (e.g. IMD-CB-2026-8921)" value="{{ cert_id }}" class="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-sky-500 focus:outline-none font-mono text-sm uppercase">
            </div>
            <button type="button" onclick="searchCert()" class="px-6 py-3 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-xl shadow transition flex items-center justify-center gap-2">
                <i data-lucide="shield-check" class="w-5 h-5"></i> Verify Certificate
            </button>
        </form>
    </div>

    {% if is_valid and certificate %}
        <!-- Verified Certificate Card -->
        <div class="bg-white rounded-3xl border-2 border-emerald-500/40 p-8 shadow-xl relative overflow-hidden animate-fade-in">
            <div class="absolute top-0 right-0 bg-emerald-500 text-white text-xs font-bold px-6 py-1.5 rounded-bl-2xl shadow-md flex items-center gap-1.5">
                <i data-lucide="check-check" class="w-4 h-4"></i> VERIFIED AUTHENTIC
            </div>

            <div class="flex items-start gap-5 mb-6">
                <div class="w-16 h-16 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                    <i data-lucide="award" class="w-8 h-8"></i>
                </div>
                <div>
                    <h2 class="text-2xl font-black text-slate-900">{{ certificate.trainee_name }}</h2>
                    <p class="text-sm text-slate-600">{{ certificate.trainee_designation }} &bull; {{ certificate.trainee_department }}</p>
                    <p class="text-xs font-mono text-emerald-700 font-bold mt-1">Certificate ID: {{ certificate.certificate_id }}</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-50 p-5 rounded-2xl border border-slate-200 text-xs mb-6">
                <div>
                    <span class="text-slate-400 block font-medium">Program Title</span>
                    <strong class="text-slate-900 text-sm">{{ certificate.course_title }}</strong>
                </div>
                <div>
                    <span class="text-slate-400 block font-medium">Course Code & Domain</span>
                    <strong class="text-slate-900 text-sm">{{ certificate.course_code }} ({{ certificate.course_domain }})</strong>
                </div>
                <div>
                    <span class="text-slate-400 block font-medium">Issue Date</span>
                    <strong class="text-slate-900">{{ certificate.issue_date }}</strong>
                </div>
                <div>
                    <span class="text-slate-400 block font-medium">Grade & Assessment Score</span>
                    <strong class="text-emerald-700 font-bold">{{ certificate.grade }} ({{ certificate.score_percentage }}%)</strong>
                </div>
                <div>
                    <span class="text-slate-400 block font-medium">Lead Instructor</span>
                    <strong class="text-slate-900">{{ certificate.trainer_name or "MoES Certified Trainer" }}</strong>
                </div>
                <div>
                    <span class="text-slate-400 block font-medium">Issuing Authority</span>
                    <strong class="text-slate-900">MoES / IMD Capacity Building Directorate</strong>
                </div>
            </div>

            <div class="flex flex-wrap justify-between items-center gap-4 pt-4 border-t border-slate-100">
                <div class="text-[11px] text-slate-400">
                    Cryptographic Signature Validated &bull; Timestamped on Government Record
                </div>
                <a href="/trainee/certificate/{{ certificate.certificate_id }}" class="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl shadow transition flex items-center gap-2">
                    <i data-lucide="eye" class="w-4 h-4"></i> View Official Certificate Document
                </a>
            </div>
        </div>
    {% elif cert_id %}
        <!-- Invalid Record -->
        <div class="bg-rose-50 border border-rose-200 rounded-2xl p-8 text-center text-rose-800">
            <i data-lucide="alert-circle" class="w-12 h-12 text-rose-500 mx-auto mb-3"></i>
            <h3 class="text-lg font-bold">Certificate Record Not Found</h3>
            <p class="text-xs text-rose-600 mt-1 max-w-md mx-auto">
                No verified capacity building certificate was found matching the identifier <strong class="font-mono">{{ cert_id }}</strong>. Please check the spelling or contact the MoES Capacity Building Directorate.
            </p>
        </div>
    {% endif %}
</div>

<script>
function searchCert() {
    const val = document.getElementById('certInput').value.trim();
    if (val) {
        window.location.href = '/verify/certificate/' + encodeURIComponent(val);
    }
}
</script>
{% endblock %}
'''

with open("app/templates/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)

with open("app/templates/verify_certificate.html", "w", encoding="utf-8") as f:
    f.write(verify_html)

print("app/templates/index.html & verify_certificate.html created successfully")
