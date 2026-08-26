# Services Module
import re
import math
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app.database import get_db

# 1. Competency Mapping Engine
def calculate_trainer_competency(
    subject: str,
    domain: Optional[str] = None,
    required_skills: Optional[List[str]] = None,
    min_experience: int = 0
) -> List[Dict[str, Any]]:
    """
    Intelligent Competency Mapping Algorithm:
    Evaluates trainers across skill overlap, domain alignment, years of experience,
    and trainee feedback rating to rank the best-suited experts for MoES/IMD courses.
    """
    if required_skills is None:
        required_skills = []
    
    # Tokenize and normalize query
    query_tokens = set(re.findall(r'\w+', (subject + " " + (domain or "")).lower()))
    for s in required_skills:
        query_tokens.update(re.findall(r'\w+', s.lower()))

    results = []

    with get_db() as db:
        cursor = db.cursor()
        # Fetch active trainers
        cursor.execute("""
            SELECT u.id, u.full_name, u.email, u.designation, u.department,
                   u.qualifications, u.experience_years, u.skills, u.interests, u.bio,
                   COALESCE(AVG(f.rating_trainer), 4.8) as avg_rating,
                   COUNT(DISTINCT c.id) as courses_count,
                   COUNT(DISTINCT f.id) as feedback_count
            FROM users u
            LEFT JOIN courses c ON c.trainer_id = u.id
            LEFT JOIN course_feedback f ON f.trainer_id = u.id
            WHERE u.role = 'trainer' AND u.status = 'active'
            GROUP BY u.id
        """)
        trainers = [dict(row) for row in cursor.fetchall()]

        for t in trainers:
            t_skills_str = (t.get("skills") or "") + " " + (t.get("interests") or "") + " " + (t.get("qualifications") or "") + " " + (t.get("designation") or "")
            t_tokens = set(re.findall(r'\w+', t_skills_str.lower()))

            # 1. Keyword overlap score (max 50 points)
            matching_tokens = query_tokens.intersection(t_tokens)
            if query_tokens:
                overlap_ratio = len(matching_tokens) / len(query_tokens)
                skill_score = min(50.0, overlap_ratio * 75.0)  # scaled
            else:
                skill_score = 30.0

            # 2. Domain & Department relevance score (max 25 points)
            dept_str = (t.get("department") or "").lower()
            domain_score = 0.0
            if domain and domain.lower() in dept_str:
                domain_score += 15.0
            if any(term in dept_str for term in ["nwp", "radar", "satellite", "cyclone", "agromet", "seismol", "iitm", "ncs", "imd", "incois"]):
                domain_score += 10.0
            domain_score = min(25.0, domain_score)

            # 3. Experience score (max 15 points) - SAFE CAST TO FLOAT
            exp = float(t.get("experience_years") or 0)
            if exp >= min_experience:
                exp_score = min(15.0, (exp / 20.0) * 15.0)
            else:
                exp_score = max(0.0, (exp / max(1, min_experience)) * 8.0)

            # 4. Feedback & Track record score (max 10 points) - FIXED INDENT & FLOAT CAST
            avg_rating = float(t.get("avg_rating") or 4.5)
            rating_score = (avg_rating / 5.0) * 10.0

            total_score = round(min(100.0, skill_score + domain_score + exp_score + rating_score), 1)

            # Match tier
            if total_score >= 80:
                tier = "Top Match"
                tier_color = "emerald"
            elif total_score >= 60:
                tier = "Strong Match"
                tier_color = "blue"
            elif total_score >= 40:
                tier = "Good Match"
                tier_color = "amber"
            else:
                tier = "Potential Match"
                tier_color = "slate"

            # Extract matching keywords for badge display
            matching_skills = [s.strip() for s in (t.get("skills") or "").split(",") if any(qt in s.lower() for qt in query_tokens)]
            if not matching_skills and t.get("skills"):
                matching_skills = [s.strip() for s in t.get("skills").split(",")[:3]]

            results.append({
                "trainer_id": t["id"],
                "full_name": t["full_name"],
                "email": t["email"],
                "designation": t["designation"],
                "department": t["department"],
                "qualifications": t["qualifications"],
                "experience_years": t["experience_years"],
                "avg_rating": round(avg_rating, 1),
                "courses_count": t["courses_count"],
                "feedback_count": t["feedback_count"],
                "total_score": total_score,
                "skill_score": round(skill_score, 1),
                "domain_score": round(domain_score, 1),
                "exp_score": round(exp_score, 1),
                "rating_score": round(rating_score, 1),
                "tier": tier,
                "tier_color": tier_color,
                "matching_skills": matching_skills,
                "all_skills": [s.strip() for s in (t.get("skills") or "").split(",") if s.strip()]
            })

    # Sort descending by match score
    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results

# 2. Certificate Service
def generate_certificate_id() -> str:
    year = datetime.now().year
    rand_num = random.randint(1000, 9999)
    return f"IMD-CB-{year}-{rand_num}"

def calculate_grade(percentage: float) -> str:
    if percentage >= 90.0:
        return "Outstanding"
    elif percentage >= 80.0:
        return "Distinction"
    elif percentage >= 70.0:
        return "First Class"
    else:
        return "Pass"

def verify_certificate_by_id(cert_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("""
            SELECT c.id, c.certificate_id, c.issue_date, c.grade, c.score_percentage,
                   c.qr_data, c.verification_url,
                   u.full_name as trainee_name, u.email as trainee_email, u.designation as trainee_designation,
                   u.department as trainee_department,
                   crs.title as course_title, crs.code as course_code, crs.domain as course_domain,
                   crs.duration_hours,
                   tr.full_name as trainer_name, tr.designation as trainer_designation
            FROM certificates c
            JOIN users u ON u.id = c.user_id
            JOIN courses crs ON crs.id = c.course_id
            LEFT JOIN users tr ON tr.id = crs.trainer_id
            WHERE c.certificate_id = ?
        """, (cert_id.strip(),))
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)

# 3. Analytics Service
def get_admin_dashboard_stats() -> Dict[str, Any]:
    with get_db() as db:
        cursor = db.cursor()

        # FIXED: Safe fetch helper for PostgreSQL dictionary rows
        def safe_fetch_count(query: str, params=()) -> int:
            cursor.execute(query, params)
            res = cursor.fetchone()
            if not res:
                return 0
            if isinstance(res, dict):
                vals = list(res.values())
                return vals[0] if vals and vals[0] is not None else 0
            try:
                return res[0] if res[0] is not None else 0
            except (KeyError, IndexError, TypeError):
                return 0

        # Counts
        total_trainees = safe_fetch_count("SELECT COUNT(*) FROM users WHERE role = 'trainee'")
        total_trainers = safe_fetch_count("SELECT COUNT(*) FROM users WHERE role = 'trainer' AND status = 'active'")
        pending_approvals = safe_fetch_count("SELECT COUNT(*) FROM users WHERE status = 'pending_approval'")
        total_courses = safe_fetch_count("SELECT COUNT(*) FROM courses WHERE status = 'published'")
        total_enrollments = safe_fetch_count("SELECT COUNT(*) FROM enrollments")
        total_certificates = safe_fetch_count("SELECT COUNT(*) FROM certificates")
        total_attempts = safe_fetch_count("SELECT COUNT(*) FROM quiz_attempts")
        passed_attempts = safe_fetch_count("SELECT COUNT(*) FROM quiz_attempts WHERE is_passed = 1")
        
        pass_rate = round((passed_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0.0

        # Domain distribution
        cursor.execute("""
            SELECT domain, COUNT(*) as count
            FROM courses
            GROUP BY domain
        """)
        domain_dist = [dict(row) for row in cursor.fetchall()]

        # Recent activities / enrollments
        cursor.execute("""
            SELECT e.enrolled_at, u.full_name as trainee_name, c.title as course_title, e.progress_percent, e.status
            FROM enrollments e
            JOIN users u ON u.id = e.user_id
            JOIN courses c ON c.id = e.course_id
            ORDER BY e.enrolled_at DESC
            LIMIT 6
        """)
        recent_enrollments = [dict(row) for row in cursor.fetchall()]

        # Pending Trainer Approvals
        cursor.execute("""
            SELECT id, full_name, email, designation, department, qualifications, experience_years, skills, created_at
            FROM users
            WHERE status = 'pending_approval'
            ORDER BY created_at DESC
        """)
        pending_trainers = [dict(row) for row in cursor.fetchall()]

        return {
            "total_trainees": total_trainees,
            "total_trainers": total_trainers,
            "pending_approvals": pending_approvals,
            "total_courses": total_courses,
            "total_enrollments": total_enrollments,
            "total_certificates": total_certificates,
            "total_attempts": total_attempts,
            "pass_rate": pass_rate,
            "domain_dist": domain_dist,
            "recent_enrollments": recent_enrollments,
            "pending_trainers": pending_trainers
        }

def get_trainer_dashboard_stats(trainer_id: int) -> Dict[str, Any]:
    with get_db() as db:
        cursor = db.cursor()

        # Courses by this trainer
        cursor.execute("SELECT id, title, code, domain, level, duration_hours FROM courses WHERE trainer_id = ?", (trainer_id,))
        courses = [dict(row) for row in cursor.fetchall()]
        course_ids = [c["id"] for c in courses]

        if not course_ids:
            return {
                "courses": [],
                "total_courses": 0,
                "total_students": 0,
                "total_quizzes": 0,
                "avg_rating": 5.0,
                "recent_attempts": []
            }

        placeholders = ",".join("?" * len(course_ids))

        # Trainees enrolled - FIXED FOR POSTGRES
        cursor.execute(f"SELECT COUNT(DISTINCT user_id) FROM enrollments WHERE course_id IN ({placeholders})", course_ids)
        res_students = cursor.fetchone()
        if res_students:
            total_students = next(iter(res_students.values())) if isinstance(res_students, dict) else (res_students[0] if res_students[0] is not None else 0)
        else:
            total_students = 0

        # Quizzes - FIXED FOR POSTGRES
        cursor.execute("SELECT COUNT(*) FROM quizzes WHERE trainer_id = ?", (trainer_id,))
        res_quizzes = cursor.fetchone()
        if res_quizzes:
            total_quizzes = next(iter(res_quizzes.values())) if isinstance(res_quizzes, dict) else (res_quizzes[0] if res_quizzes[0] is not None else 0)
        else:
            total_quizzes = 0

        # Avg Rating - FIXED FOR POSTGRES AND DECIMAL
        cursor.execute("SELECT COALESCE(AVG(rating_trainer), 5.0) FROM course_feedback WHERE trainer_id = ?", (trainer_id,))
        res_rating = cursor.fetchone()
        if res_rating:
            val = next(iter(res_rating.values())) if isinstance(res_rating, dict) else res_rating[0]
            avg_rating = round(float(val), 1) if val is not None else 5.0
        else:
            avg_rating = 5.0

        # Recent attempts
        cursor.execute(f"""
            SELECT qa.attempted_at, u.full_name as trainee_name, q.title as quiz_title,
                   qa.score, qa.total_marks, qa.percentage, qa.is_passed
            FROM quiz_attempts qa
            JOIN users u ON u.id = qa.user_id
            JOIN quizzes q ON q.id = qa.quiz_id
            WHERE q.trainer_id = ?
            ORDER BY qa.attempted_at DESC
            LIMIT 6
        """, (trainer_id,))
        recent_attempts = [dict(row) for row in cursor.fetchall()]

        return {
            "courses": courses,
            "total_courses": len(courses),
            "total_students": total_students,
            "total_quizzes": total_quizzes,
            "avg_rating": avg_rating,
            "recent_attempts": recent_attempts
        }
