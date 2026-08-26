import os

admin_dashboard_html = '''{% extends "base.html" %}

{% block title %}Admin Command Center - CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
    
    <!-- Admin Header -->
    <div class="bg-gradient-to-r from-purple-950 via-slate-900 to-moes-navy rounded-3xl p-6 sm:p-8 text-white shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <div class="flex items-center gap-2 mb-2">
                <span class="bg-purple-500/20 text-purple-300 text-xs px-2.5 py-0.5 rounded-full font-bold border border-purple-500/30">MoES & IMD Governance Directorate</span>
                <span class="text-xs text-slate-400">National Capacity Monitoring</span>
            </div>
            <h1 class="text-2xl sm:text-3xl font-black tracking-tight">Executive Capacity Command</h1>
            <p class="text-xs sm:text-sm text-slate-300 mt-1">Logged in as: <strong>{{ user.full_name }}</strong> ({{ user.designation }})</p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
            <a href="/admin/users" class="px-4 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-xs font-bold shadow transition flex items-center gap-1.5">
                <i data-lucide="user-check" class="w-4 h-4"></i> User Approvals ({{ stats.pending_approvals }})
            </a>
            <a href="/admin/competency-map" class="px-4 py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-xl text-xs font-bold shadow transition flex items-center gap-1.5">
                <i data-lucide="git-merge" class="w-4 h-4"></i> Competency Matcher
            </a>
        </div>
    </div>

    <!-- KPI Metrics Cards (6 Grid) -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-[11px] text-slate-400 font-medium">Total Trainees</div>
            <div class="text-2xl font-black text-slate-900 mt-1">{{ stats.total_trainees }}</div>
            <div class="text-[10px] text-sky-600 font-semibold mt-1">Registered officers</div>
        </div>

        <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-[11px] text-slate-400 font-medium">Active Trainers</div>
            <div class="text-2xl font-black text-emerald-600 mt-1">{{ stats.total_trainers }}</div>
            <div class="text-[10px] text-emerald-700 font-semibold mt-1">Verified Scientists</div>
        </div>

        <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-[11px] text-slate-400 font-medium">Pending Approvals</div>
            <div class="text-2xl font-black text-amber-600 mt-1">{{ stats.pending_approvals }}</div>
            <div class="text-[10px] text-amber-700 font-semibold mt-1">Require Review</div>
        </div>

        <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-[11px] text-slate-400 font-medium">Domain Courses</div>
            <div class="text-2xl font-black text-purple-600 mt-1">{{ stats.total_courses }}</div>
            <div class="text-[10px] text-purple-700 font-semibold mt-1">Published Curricula</div>
        </div>

        <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-[11px] text-slate-400 font-medium">Certificates Issued</div>
            <div class="text-2xl font-black text-blue-600 mt-1">{{ stats.total_certificates }}</div>
            <div class="text-[10px] text-blue-700 font-semibold mt-1">Verifiable Credentials</div>
        </div>

        <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm">
            <div class="text-[11px] text-slate-400 font-medium">Pass Rate Average</div>
            <div class="text-2xl font-black text-emerald-600 mt-1">{{ stats.pass_rate }}%</div>
            <div class="text-[10px] text-emerald-700 font-semibold mt-1">Competency standard</div>
        </div>
    </div>

    <!-- Chart.js Analytical Visualizations -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- Left: Regional Observatory Participation Chart (7 cols) -->
        <div class="lg:col-span-7 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                <div>
                    <h3 class="font-bold text-slate-900 text-sm">Regional Meteorological Center (RMC) Participation</h3>
                    <p class="text-[11px] text-slate-400">Trainees enrolled vs. certifications completed by region</p>
                </div>
                <span class="text-xs bg-sky-50 text-sky-700 font-bold px-2 py-0.5 rounded">All 6 RMCs</span>
            </div>
            <div class="h-64">
                <canvas id="regionalChart"></canvas>
            </div>
        </div>

        <!-- Right: MoES Discipline Distribution Doughnut (5 cols) -->
        <div class="lg:col-span-5 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                <div>
                    <h3 class="font-bold text-slate-900 text-sm">Domain Curricula Distribution</h3>
                    <p class="text-[11px] text-slate-400">Breakdown by atmospheric & earth science disciplines</p>
                </div>
            </div>
            <div class="h-64 flex items-center justify-center">
                <canvas id="domainChart"></canvas>
            </div>
        </div>
    </div>

    <!-- Pending Approvals & Recent Activities -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- Pending Trainer Approvals Card (6 cols) -->
        <div class="lg:col-span-6 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                <h3 class="font-bold text-slate-900 text-sm flex items-center gap-2">
                    <i data-lucide="user-plus" class="w-4 h-4 text-amber-500"></i> Pending Trainer Approvals
                </h3>
                <a href="/admin/users" class="text-xs font-bold text-purple-700 hover:underline">View All &rarr;</a>
            </div>

            {% if stats.pending_trainers %}
                <div class="space-y-3">
                    {% for p in stats.pending_trainers %}
                        <div class="p-4 bg-amber-50/60 rounded-2xl border border-amber-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 text-xs">
                            <div>
                                <div class="font-bold text-slate-900 text-sm">{{ p.full_name }}</div>
                                <div class="text-slate-600">{{ p.designation }} &bull; {{ p.department }}</div>
                                <div class="text-[11px] text-slate-400 font-mono mt-0.5">{{ p.email }}</div>
                            </div>
                            <div class="flex gap-2 shrink-0">
                                <form action="/admin/users/{{ p.id }}/approve" method="post">
                                    <button type="submit" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold shadow-sm">
                                        Approve
                                    </button>
                                </form>
                                <form action="/admin/users/{{ p.id }}/reject" method="post">
                                    <button type="submit" class="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-bold">
                                        Reject
                                    </button>
                                </form>
                            </div>
                        </div>
                    {% endfor %}
                </div>
            {% else %}
                <p class="text-xs text-slate-400 text-center py-6">No trainer registrations currently awaiting administrative review.</p>
            {% endif %}
        </div>

        <!-- Recent Certificates Issued (6 cols) -->
        <div class="lg:col-span-6 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200 shadow-sm space-y-4">
            <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                <h3 class="font-bold text-slate-900 text-sm flex items-center gap-2">
                    <i data-lucide="award" class="w-4 h-4 text-emerald-600"></i> Latest Certifications Issued
                </h3>
            </div>

            <div class="space-y-3">
                {% for cert in recent_certs %}
                    <div class="p-3.5 bg-slate-50 rounded-2xl border border-slate-200 flex justify-between items-center text-xs">
                        <div>
                            <div class="font-bold text-slate-900">{{ cert.trainee_name }}</div>
                            <div class="text-slate-500 text-[11px]">{{ cert.course_title }}</div>
                            <div class="text-slate-400 font-mono text-[10px]">{{ cert.certificate_id }}</div>
                        </div>
                        <div class="text-right">
                            <span class="font-bold text-emerald-700 block">{{ cert.grade }}</span>
                            <a href="/verify/certificate/{{ cert.certificate_id }}" target="_blank" class="text-[10px] text-sky-600 font-bold hover:underline">Verify &rarr;</a>
                        </div>
                    </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>

<!-- Chart.js CDN & Loader -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const res = await fetch('/api/admin/chart-data');
        const data = await res.json();

        // 1. Regional Chart (Bar)
        const ctxReg = document.getElementById('regionalChart').getContext('2d');
        new Chart(ctxReg, {
            type: 'bar',
            data: {
                labels: data.regional_stats.map(r => r.region.replace(' (', '\\n(')),
                datasets: [
                    {
                        label: 'Enrolled Officers',
                        data: data.regional_stats.map(r => r.trainees),
                        backgroundColor: '#0284c7',
                        borderRadius: 8
                    },
                    {
                        label: 'Certifications Completed',
                        data: data.regional_stats.map(r => r.completed),
                        backgroundColor: '#059669',
                        borderRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } }
            }
        });

        // 2. Domain Chart (Doughnut)
        const ctxDom = document.getElementById('domainChart').getContext('2d');
        new Chart(ctxDom, {
            type: 'doughnut',
            data: {
                labels: data.domains.map(d => d.domain),
                datasets: [{
                    data: data.domains.map(d => d.count),
                    backgroundColor: ['#0284c7', '#059669', '#d97706', '#9333ea', '#ea580c', '#0d9488']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 10 } } } }
            }
        });
    } catch(e) {
        console.error(e);
    }
});
</script>
{% endblock %}
'''

admin_users_html = '''{% extends "base.html" %}

{% block title %}User Management & Approvals - CAPACITY CONNECT{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 py-8 space-y-8">
    
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <span class="text-xs font-bold text-purple-700 bg-purple-50 px-2.5 py-0.5 rounded-full uppercase border border-purple-200">Access Control & Governance</span>
            <h1 class="text-3xl font-black text-slate-900 mt-1">User Directory & Role Approvals</h1>
            <p class="text-xs text-slate-500 mt-1">Review pending trainer registrations, adjust role privileges, and manage officer account statuses.</p>
        </div>

        <!-- Pending Badge -->
        {% if pending_count > 0 %}
            <div class="bg-amber-100 border border-amber-300 text-amber-900 px-4 py-2 rounded-2xl text-xs font-bold flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-500 animate-ping"></span>
                <span>{{ pending_count }} Trainer Registration(s) Awaiting Review</span>
            </div>
        {% endif %}
    </div>

    <!-- Filters & Search Form -->
    <div class="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-3 items-center justify-between">
        <form action="/admin/users" method="get" class="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <input type="text" name="search" value="{{ search }}" placeholder="Search name, email, department..." class="px-3 py-2 text-xs border border-slate-300 rounded-xl w-60 focus:outline-none">
            
            <select name="role" onchange="this.form.submit()" class="px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white">
                <option value="">All Roles</option>
                <option value="trainee" {% if selected_role == 'trainee' %}selected{% endif %}>Trainees</option>
                <option value="trainer" {% if selected_role == 'trainer' %}selected{% endif %}>Trainers</option>
                <option value="admin" {% if selected_role == 'admin' %}selected{% endif %}>Admins</option>
            </select>

            <select name="status_filter" onchange="this.form.submit()" class="px-3 py-2 text-xs border border-slate-300 rounded-xl bg-white">
                <option value="">All Statuses</option>
                <option value="pending_approval" {% if selected_status == 'pending_approval' %}selected{% endif %}>Pending Approval</option>
                <option value="active" {% if selected_status == 'active' %}selected{% endif %}>Active</option>
                <option value="suspended" {% if selected_status == 'suspended' %}selected{% endif %}>Suspended</option>
            </select>

            <button type="submit" class="px-4 py-2 bg-purple-600 text-white font-bold text-xs rounded-xl shadow">Filter</button>
        </form>
        <span class="text-xs text-slate-400 font-medium">{{ users_list|length }} Officers Listed</span>
    </div>

    <!-- Users Table -->
    <div class="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm">
        <div class="overflow-x-auto">
            <table class="w-full text-left text-xs border-collapse">
                <thead>
                    <tr class="bg-slate-50 border-b border-slate-200 text-slate-400 uppercase text-[10px]">
                        <th class="py-4 px-6">Officer & Department</th>
                        <th class="py-4 px-4">Role</th>
                        <th class="py-4 px-4">Account Status</th>
                        <th class="py-4 px-4">Experience & Skills</th>
                        <th class="py-4 px-4">Activity</th>
                        <th class="py-4 px-6 text-right">Actions</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    {% for u in users_list %}
                        <tr class="hover:bg-slate-50/80 transition {% if u.status == 'pending_approval' %}bg-amber-50/40{% endif %}">
                            <td class="py-4 px-6">
                                <div class="font-bold text-slate-900 text-sm">{{ u.full_name }}</div>
                                <div class="text-slate-500 text-[11px]">{{ u.designation }} &bull; {{ u.department }}</div>
                                <div class="text-slate-400 font-mono text-[10px]">{{ u.email }}</div>
                            </td>

                            <td class="py-4 px-4">
                                <span class="uppercase font-bold text-[10px] px-2.5 py-1 rounded-full {% if u.role == 'admin' %}bg-purple-100 text-purple-800 border border-purple-200{% elif u.role == 'trainer' %}bg-emerald-100 text-emerald-800 border border-emerald-200{% else %}bg-sky-100 text-sky-800 border border-sky-200{% endif %}">
                                    {{ u.role }}
                                </span>
                            </td>

                            <td class="py-4 px-4">
                                {% if u.status == 'pending_approval' %}
                                    <span class="bg-amber-100 text-amber-900 text-[10px] font-bold px-2 py-0.5 rounded border border-amber-300 flex items-center gap-1 w-max">
                                        <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span> Pending Review
                                    </span>
                                {% elif u.status == 'active' %}
                                    <span class="text-emerald-700 font-bold text-[11px] flex items-center gap-1">
                                        <i data-lucide="check" class="w-3.5 h-3.5"></i> Active
                                    </span>
                                {% else %}
                                    <span class="text-slate-400 font-bold text-[11px]">{{ u.status }}</span>
                                {% endif %}
                            </td>

                            <td class="py-4 px-4 max-w-xs">
                                <div class="text-slate-700 font-medium">{{ u.experience_years }} Yrs Exp</div>
                                <div class="text-[10px] text-slate-500 truncate">{{ u.skills or "No skills logged" }}</div>
                            </td>

                            <td class="py-4 px-4 text-[11px] text-slate-500">
                                {% if u.role == 'trainer' %}
                                    {{ u.courses_taught }} Courses Authored
                                {% else %}
                                    {{ u.enrollments_count }} Enrolled &bull; {{ u.certs_count }} Certs
                                {% endif %}
                            </td>

                            <td class="py-4 px-6 text-right space-x-1 whitespace-nowrap">
                                {% if u.status == 'pending_approval' %}
                                    <form action="/admin/users/{{ u.id }}/approve" method="post" class="inline">
                                        <button type="submit" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold text-xs shadow-sm">
                                            Approve
                                        </button>
                                    </form>
                                    <form action="/admin/users/{{ u.id }}/reject" method="post" class="inline">
                                        <button type="submit" class="px-3 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-bold text-xs">
                                            Reject
                                        </button>
                                    </form>
                                {% else %}
                                    <!-- Role Switcher Form -->
                                    <form action="/admin/users/{{ u.id }}/role" method="post" class="inline">
                                        <select name="new_role" onchange="this.form.submit()" class="text-[10px] font-bold border border-slate-300 rounded px-1.5 py-1 bg-white">
                                            <option value="trainee" {% if u.role == 'trainee' %}selected{% endif %}>Trainee</option>
                                            <option value="trainer" {% if u.role == 'trainer' %}selected{% endif %}>Trainer</option>
                                            <option value="admin" {% if u.role == 'admin' %}selected{% endif %}>Admin</option>
                                        </select>
                                    </form>
                                {% endif %}
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
'''

with open("app/templates/admin/dashboard.html", "w", encoding="utf-8") as f:
    f.write(admin_dashboard_html)

with open("app/templates/admin/users.html", "w", encoding="utf-8") as f:
    f.write(admin_users_html)

print("Admin templates Part 1 created successfully")
