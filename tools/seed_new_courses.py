import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath("."))

from app.database import get_db

new_courses = [
    (
        "Applied AI/ML & Deep Learning for Extreme Weather & Nowcasting",
        "IMD-AI-401", "Artificial Intelligence in Meteorology", "Advanced", 30,
        "Advanced capacity building on Physics-Informed Neural Networks (PINNs), ConvLSTM for radar echo extrapolation, Transformer models for precipitation nowcasting, and machine learning post-processing of numerical ensemble forecasts.",
        "dr.m.sharma@imd.gov.in"
    ),
    (
        "Aviation Meteorology & ICAO Aerodrome Met Office (AMO) Standards",
        "IMD-AVN-201", "Aviation Meteorology", "Intermediate", 20,
        "Operational training on METAR, SPECI, TAF formulation, terminal aerodrome weather radar, low-level wind shear detection systems (LLWAS), runway visual range (RVR) instrumentation, and SIGMET issuance for clear-air turbulence and convective storms.",
        "dr.ananya.das@imd.gov.in"
    ),
    (
        "Operational Ocean State Forecasting, Storm Surges & Coastal Hazard Warning",
        "INCOIS-OCN-301", "Oceanographic Sciences", "Advanced", 24,
        "Collaborative MoES/INCOIS curriculum covering coastal sea-state prediction, wave-rider buoy telemetry, High-Frequency (HF) radar surface currents, hydrodynamic storm surge modeling (ADCIRC/IITD model), and coastal inundation warning dissemination.",
        "dr.r.venkatesh@imd.gov.in"
    ),
    (
        "Climate Dynamics, Monsoonal Teleconnections & Extended Range Forecasting",
        "IMD-CLIM-302", "Climatology & Climate Change", "Intermediate", 22,
        "Systematic training on coupled climate models, El Niño Southern Oscillation (ENSO), Indian Ocean Dipole (IOD), Madden-Julian Oscillation (MJO), drought monitoring indicators, and sub-seasonal to seasonal (S2S) monsoon predictions.",
        "dr.priya.nair@imd.gov.in"
    ),
    (
        "High-Performance Computing (HPC), GPU Acceleration & Earth System Modeling",
        "NCMRWF-HPC-501", "HPC & Scientific Computing", "Advanced", 25,
        "Practical training on MoES supercomputing clusters (Pratyush & Mihir), MPI/OpenMP parallelization of atmospheric dynamical cores, GPU-accelerated microphysics schemes, and Petascale data I/O management with NetCDF-4/Zarr.",
        "dr.m.sharma@imd.gov.in"
    ),
    (
        "Dual-Polarimetric Doppler Radar Urban Hydrometeorology & Flash Flood Nowcasting",
        "IMD-RAD-302", "Radar Meteorology", "Advanced", 20,
        "Urban nowcasting techniques using high-resolution X-band dual-polarimetric radars, Quantitative Precipitation Estimation (QPE) algorithms, Specific Differential Phase (Kdp) rain rate derivation, and integration with city drainage hydrodynamic models.",
        "dr.ananya.das@imd.gov.in"
    )
]

def add_courses():
    with get_db() as db:
        cursor = db.cursor()
        
        # Get trainer ids
        cursor.execute("SELECT email, id FROM users WHERE role = 'trainer'")
        trainer_map = {row[0]: row[1] for row in cursor.fetchall()}
        
        added_count = 0
        for title, code, domain, level, duration, desc, t_email in new_courses:
            cursor.execute("SELECT id FROM courses WHERE code = ?", (code,))
            if cursor.fetchone():
                print(f"Course {code} already exists.")
                continue
            
            t_id = trainer_map.get(t_email)
            cursor.execute("""
                INSERT INTO courses (title, code, domain, level, duration_hours, description, trainer_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'published')
            """, (title, code, domain, level, duration, desc, t_id))
            course_id = cursor.lastrowid
            added_count += 1
            print(f"Added Course {code} (ID: {course_id})")

            # Add sample module & lessons
            cursor.execute("""
                INSERT INTO course_modules (course_id, title, order_num, summary)
                VALUES (?, ?, 1, ?)
            """, (course_id, f"Module 1: Advanced Operational Framework for {code}", f"Comprehensive theoretical foundations and operational implementation protocols for {title}."))
            module_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO course_lessons (module_id, course_id, title, lesson_type, content_url, duration_mins, notes, order_num)
                VALUES (?, ?, ?, 'video', 'https://www.youtube.com/embed/dQw4w9WgXcQ', 30, 'Key theoretical principles and standard operating guidelines.', 1)
            """, (module_id, course_id, f"1.1 Foundations & Mathematical Physics of {code}"))

            cursor.execute("""
                INSERT INTO course_lessons (module_id, course_id, title, lesson_type, content_url, duration_mins, notes, order_num)
                VALUES (?, ?, ?, 'presentation', '/static/docs/Manual_Guidelines.pdf', 35, 'Case studies from recent extreme weather episodes over Indian subcontinent.', 2)
            """, (module_id, course_id, f"1.2 Case Analysis & Operational Diagnostics ({code})"))

            # Add sample quiz
            deadline = (datetime.now() + timedelta(days=35)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                INSERT INTO quizzes (course_id, trainer_id, title, subject, duration_mins, pass_percentage, deadline)
                VALUES (?, ?, ?, ?, 20, 70, ?)
            """, (course_id, t_id, f"{code} Master Competency Assessment", domain, deadline))
            quiz_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO quiz_questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation)
                VALUES (?, ?, ?, ?, ?, ?, 'A', ?)
            """, (
                quiz_id,
                f"What is the primary operational objective of {title} in the MoES/IMD early warning network?",
                "Enhancing lead time and spatial accuracy of warnings for disaster risk mitigation",
                "Replacing ground observational networks entirely with satellite data",
                "Decreasing model computational resolution to save electrical power",
                "Restricting weather advisory access to private sector entities only",
                "MoES Mission Mausam mandate emphasizes maximizing early warning lead times with high spatiotemporal precision to protect life and property."
            ))

            cursor.execute("""
                INSERT INTO quiz_questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation)
                VALUES (?, ?, ?, ?, ?, ?, 'B', ?)
            """, (
                quiz_id,
                f"Which physical or numerical diagnostic metric is most critical when evaluating {domain} products?",
                "Only qualitative visual inspection without statistics",
                "Root Mean Square Error (RMSE), Threat Score (TS), and Equitable Threat Score (ETS)",
                "Alphabetical sorting of observatory stations",
                "Ignoring observational error covariance matrices",
                "Objective skill metrics like ETS and RMSE provide standardized quantitative verification against ground truth observations."
            ))

    print(f"\nSuccessfully added {added_count} new target courses with modules, lessons, and certification quizzes!")

if __name__ == "__main__":
    add_courses()
