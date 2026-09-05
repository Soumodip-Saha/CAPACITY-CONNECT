import os
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, date, timedelta
from app.config import DATABASE_PATH, DATABASE_URL
from app.auth import generate_salt, hash_password

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

def is_postgres() -> bool:
    return bool(DATABASE_URL and ("postgres" in DATABASE_URL or "postgresql" in DATABASE_URL))

class UniversalRow:
    """
    Universal row wrapper providing identical behavior to sqlite3.Row in PostgreSQL:
    - Numeric index access: row[0], row[1]
    - Case-insensitive column name access: row['column_name']
    - Dictionary conversion: dict(row) or dict(row.items())
    - Safe .get('column_name', default)
    - Membership checks: 'col' in row
    """
    def __init__(self, values_list, columns_map):
        self._values = list(values_list)
        self._columns = list(columns_map)
        self._map = {str(col).lower(): i for i, col in enumerate(columns_map)}

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return self._values[key]
        if isinstance(key, str):
            idx = self._map.get(key.lower())
            if idx is not None:
                return self._values[idx]
            raise KeyError(key)
        raise TypeError(f"Row indices must be integers or strings, not {type(key)}")

    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError, IndexError):
            return default

    def keys(self):
        return self._columns

    def values(self):
        return self._values

    def items(self):
        return zip(self._columns, self._values)

    def __iter__(self):
        return iter(self._columns)

    def __len__(self):
        return len(self._values)

    def __contains__(self, key):
        if isinstance(key, str):
            return key.lower() in self._map
        return key in self._values

    def __repr__(self):
        return f"<Row {dict(self.items())}>"

class PostgresCursorWrapper:
    def __init__(self, raw_cursor):
        self.cursor = raw_cursor
        self.lastrowid = None

    def _convert_query(self, query: str) -> str:
        return query.replace("?", "%s")

    def _wrap_row(self, raw_row):
        if raw_row is None:
            return None
        if self.cursor.description:
            col_names = [col[0] for col in self.cursor.description]
            return UniversalRow(raw_row, col_names)
        return raw_row

    def execute(self, query, params=None):
        pg_query = self._convert_query(query)
        is_insert = pg_query.strip().upper().startswith("INSERT INTO")
        has_returning = "RETURNING" in pg_query.upper()

        if is_insert and not has_returning:
            pg_query_with_ret = pg_query.rstrip(";") + " RETURNING id;"
            try:
                if params:
                    self.cursor.execute(pg_query_with_ret, params)
                else:
                    self.cursor.execute(pg_query_with_ret)
                res = self.cursor.fetchone()
                if res is not None:
                    self.lastrowid = res[0]
            except Exception:
                if params:
                    self.cursor.execute(pg_query, params)
                else:
                    self.cursor.execute(pg_query)
            return self
        else:
            if params:
                self.cursor.execute(pg_query, params)
            else:
                self.cursor.execute(pg_query)
            return self

    def executemany(self, query, seq_of_params):
        pg_query = self._convert_query(query)
        return self.cursor.executemany(pg_query, seq_of_params)

    def fetchone(self):
        raw = self.cursor.fetchone()
        return self._wrap_row(raw)

    def fetchall(self):
        raw_rows = self.cursor.fetchall()
        if not raw_rows:
            return []
        col_names = [col[0] for col in self.cursor.description] if self.cursor.description else []
        return [UniversalRow(r, col_names) for r in raw_rows]

    def fetchmany(self, size=None):
        raw_rows = self.cursor.fetchmany(size) if size else self.cursor.fetchmany()
        if not raw_rows:
            return []
        col_names = [col[0] for col in self.cursor.description] if self.cursor.description else []
        return [UniversalRow(r, col_names) for r in raw_rows]

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def close(self):
        return self.cursor.close()

    def __iter__(self):
        while True:
            row = self.fetchone()
            if row is None:
                break
            yield row

class PostgresConnectionWrapper:
    def __init__(self, raw_conn):
        self.conn = raw_conn

    def cursor(self):
        return PostgresCursorWrapper(self.conn.cursor())

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def close(self):
        return self.conn.close()

@contextmanager
def get_db():
    if is_postgres():
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("psycopg2-binary is required for PostgreSQL. Install with: pip install psycopg2-binary")
        conn = psycopg2.connect(DATABASE_URL)
        wrapper = PostgresConnectionWrapper(conn)
        try:
            yield wrapper
            wrapper.commit()
        except Exception:
            wrapper.rollback()
            raise
        finally:
            wrapper.close()
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

def init_db():
    use_pg = is_postgres()
    pk_type = "SERIAL PRIMARY KEY" if use_pg else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    with get_db() as db:
        cursor = db.cursor()
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id {pk_type},
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('trainee', 'trainer', 'admin')),
                status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('pending_approval', 'active', 'rejected', 'suspended')),
                designation TEXT,
                department TEXT,
                qualifications TEXT,
                experience_years INTEGER DEFAULT 0,
                skills TEXT,
                interests TEXT,
                bio TEXT,
                avatar_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS courses (
                id {pk_type},
                title TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                domain TEXT NOT NULL,
                level TEXT NOT NULL DEFAULT 'Intermediate',
                duration_hours INTEGER DEFAULT 20,
                description TEXT,
                trainer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                thumbnail_url TEXT,
                status TEXT DEFAULT 'published',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS course_modules (
                id {pk_type},
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                order_num INTEGER DEFAULT 1,
                summary TEXT
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS course_lessons (
                id {pk_type},
                module_id INTEGER REFERENCES course_modules(id) ON DELETE CASCADE,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                lesson_type TEXT NOT NULL DEFAULT 'video',
                content_url TEXT,
                duration_mins INTEGER DEFAULT 15,
                notes TEXT,
                order_num INTEGER DEFAULT 1
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS enrollments (
                id {pk_type},
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                progress_percent INTEGER DEFAULT 0,
                completed_lessons TEXT DEFAULT '[]',
                status TEXT DEFAULT 'in_progress',
                completed_at TIMESTAMP,
                UNIQUE(user_id, course_id)
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS quizzes (
                id {pk_type},
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                trainer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                duration_mins INTEGER DEFAULT 20,
                pass_percentage INTEGER DEFAULT 70,
                deadline TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id {pk_type},
                quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_option TEXT NOT NULL CHECK(correct_option IN ('A', 'B', 'C', 'D')),
                explanation TEXT,
                marks INTEGER DEFAULT 1
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id {pk_type},
                quiz_id INTEGER REFERENCES quizzes(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                score INTEGER NOT NULL,
                total_marks INTEGER NOT NULL,
                percentage REAL NOT NULL,
                is_passed INTEGER NOT NULL,
                user_answers TEXT,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS certificates (
                id {pk_type},
                certificate_id TEXT UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                issue_date DATE NOT NULL,
                grade TEXT NOT NULL DEFAULT 'Distinction',
                score_percentage REAL NOT NULL,
                qr_data TEXT NOT NULL,
                verification_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS course_feedback (
                id {pk_type},
                course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                trainer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                rating_content INTEGER NOT NULL,
                rating_trainer INTEGER NOT NULL,
                rating_overall INTEGER NOT NULL,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS trainer_library (
                id {pk_type},
                trainer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                category TEXT NOT NULL,
                file_url TEXT,
                file_size TEXT,
                description TEXT,
                downloads_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS announcements (
                id {pk_type},
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Announcement',
                priority TEXT NOT NULL DEFAULT 'Normal',
                published_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

def seed_db():
    with get_db() as db:
        cursor = db.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM users")
        res = cursor.fetchone()
        count = res[0] if isinstance(res, (tuple, list)) else (res["count"] if hasattr(res, "__getitem__") else 0)
        if count > 0:
            return

        db_type = "PostgreSQL" if is_postgres() else "SQLite"
        print(f"Seeding CAPACITY CONNECT {db_type} database with MoES/IMD realistic data...")

        # 1. Admin
        s_adm = generate_salt()
        p_adm = hash_password("Admin@123", s_adm)
        cursor.execute("""
            INSERT INTO users (email, password_hash, salt, full_name, role, status, designation, department, qualifications, experience_years, skills, interests, bio)
            VALUES (?, ?, ?, ?, 'admin', 'active', ?, ?, ?, ?, ?, ?, ?)
        """, (
            "admin@imd.gov.in", p_adm, s_adm,
            "Dr. Rajeshwar Rao",
            "Director of Training & Capacity Building",
            "Ministry of Earth Sciences (MoES) / IMD HQ New Delhi",
            "Ph.D. in Atmospheric Sciences, IIT Delhi",
            22,
            "Atmospheric Dynamics, Policy Planning, Meteorological Training Governance",
            "Capacity Building, Scientific Human Resource Development, High Performance Computing",
            "Leading national training programs and digital competency frameworks across all MoES and IMD institutions."
        ))
        admin_id = cursor.lastrowid

        # 2. Trainers
        trainers = [
            (
                "dr.m.sharma@imd.gov.in", "Trainer@123", "Dr. Madhavan Sharma",
                "Scientist-G & Head, NWP Division", "IMD New Delhi - Mausam Bhawan",
                "Ph.D. in Numerical Modeling, IISc Bangalore", 18,
                "Numerical Weather Prediction, WRF Modeling, Data Assimilation, Ensemble Forecasting, High-Performance Computing",
                "Monsoon Predictability, Mesoscale Modeling, Severe Weather Dynamics",
                "Pioneer in high-resolution global and regional numerical weather models operationalized at IMD.",
                "active"
            ),
            (
                "dr.ananya.das@imd.gov.in", "Trainer@123", "Dr. Ananya Das",
                "Scientist-F, Radar Meteorology Division", "Regional Meteorological Center, Kolkata",
                "Ph.D. in Radar Remote Sensing, Calcutta University", 14,
                "Doppler Weather Radar, Dual-Polarization Radar, Severe Storm Nowcasting, Hydrometeor Classification",
                "Thunderstorm Dynamics, Microburst Detection, Flash Flood Warnings",
                "Overseeing Doppler Radar network operations and nowcasting protocols in eastern and north-eastern India.",
                "active"
            ),
            (
                "dr.r.venkatesh@imd.gov.in", "Trainer@123", "Dr. R. Venkatesh",
                "Scientist-F, Satellite Meteorology Division", "Space Applications Division, IMD Pune / Ahmedabad",
                "Ph.D. in Satellite Meteorology, Andhra University", 16,
                "INSAT-3DR, INSAT-3DS, Scatterometry, Tropical Cyclone Track Prediction, IR Remote Sensing, Cloud Physics",
                "Satellite Geostationary Imagers, Atmospheric Sounders, Ocean Color Sensors",
                "Expert in processing and operational utilization of Indian geostationary meteorological satellites.",
                "active"
            ),
            (
                "dr.priya.nair@imd.gov.in", "Trainer@123", "Dr. Priya Nair",
                "Scientist-E, Agricultural Meteorology", "IMD Agrometeorological Advisory Services, Pune",
                "Ph.D. in Agrometeorology, PAU Ludhiana", 11,
                "Agrometeorological Advisories, Crop Weather Modeling, Soil Moisture Monitoring, Extended Range Forecasting",
                "Climate Resilient Agriculture, Gramin Krishi Mausam Sewa (GKMS)",
                "Designing district and block-level agromet advisory bulletins for millions of Indian farmers.",
                "active"
            ),
            (
                "dr.k.murthy@imd.gov.in", "Trainer@123", "Dr. K. S. Murthy",
                "Scientist-F, Seismological Network Operations", "National Center for Seismology (NCS) / MoES New Delhi",
                "Ph.D. in Geophysics, Osmania University", 15,
                "Seismological Inversion, Tsunami Early Warning, Ocean Bottom Pressure Modeling, Seismic Microzonation",
                "Plate Tectonics, Himalayan Seismic Hazard, Deep Earth Geodynamics",
                "Senior researcher in real-time earthquake monitoring and Indian Ocean Tsunami Warning System operations.",
                "active"
            ),
            (
                "prof.tarun.verma@iitm.ac.in", "Trainer@123", "Prof. Tarun Verma",
                "Visiting Climate Scientist & Professor", "Indian Institute of Tropical Meteorology (IITM), Pune",
                "Ph.D. in Atmospheric Physics, Oxford University", 19,
                "Climate Modeling, AI/ML in Weather, Monsoon Teleconnections, Extreme Rainfall Prediction",
                "Coupled Ocean-Atmosphere Models, Climate Change Projections",
                "Submitted application for conducting specialized advanced AI/ML Capacity Building workshops for MoES officers.",
                "pending_approval"
            )
        ]

        trainer_ids = {}
        for email, pwd, name, desig, dept, qual, exp, skills, interests, bio, status in trainers:
            s = generate_salt()
            p = hash_password(pwd, s)
            cursor.execute("""
                INSERT INTO users (email, password_hash, salt, full_name, role, status, designation, department, qualifications, experience_years, skills, interests, bio)
                VALUES (?, ?, ?, ?, 'trainer', ?, ?, ?, ?, ?, ?, ?, ?)
            """, (email, p, s, name, status, desig, dept, qual, exp, skills, interests, bio))
            trainer_ids[email] = cursor.lastrowid

        # 3. Trainees
        trainees = [
            (
                "trainee.verma@imd.gov.in", "Trainee@123", "Rahul Verma",
                "Meteorologist Grade-I", "IMD Cyclone Warning Division, New Delhi",
                "M.Sc. Atmospheric Sciences, Delhi University", 3,
                "Synoptic Meteorology, Cyclone Tracking, Weather Chart Analysis, Python MetPy",
                "Tropical Meteorology, Severe Weather Warnings, Disaster Risk Mitigation",
                "Operational meteorologist monitoring Bay of Bengal and Arabian Sea cyclonic systems."
            ),
            (
                "sneha.patel@imd.gov.in", "Trainee@123", "Sneha Patel",
                "Scientific Assistant", "Doppler Weather Radar Station, Bhuj, Gujarat",
                "B.Tech Electronics & Met Instrumentation", 2,
                "Radar Maintenance, DWR Data Acquisition, Signal Processing, Weather Radar Tools",
                "Nowcasting, Extreme Wind Warnings, Dual-Pol Radar Calibration",
                "Handling 24x7 Doppler radar operations and data feeds for Gujarat western coast."
            ),
            (
                "amit.sen@imd.gov.in", "Trainee@123", "Amit Sen",
                "Agromet Observer", "IMD Pune Observational Network, Maharashtra",
                "B.Sc. Agriculture & Agro-meteorology", 1,
                "Soil Moisture Analysis, Agro Forecast Dissemination, Weather Data Logging",
                "Farmer Outreach, Crop Weather Calenders, Rainfall Deficit Monitoring",
                "Field meteorology observer engaged with district agromet units."
            )
        ]

        trainee_ids = {}
        for email, pwd, name, desig, dept, qual, exp, skills, interests, bio in trainees:
            s = generate_salt()
            p = hash_password(pwd, s)
            cursor.execute("""
                INSERT INTO users (email, password_hash, salt, full_name, role, status, designation, department, qualifications, experience_years, skills, interests, bio)
                VALUES (?, ?, ?, ?, 'trainee', 'active', ?, ?, ?, ?, ?, ?, ?)
            """, (email, p, s, name, desig, dept, qual, exp, skills, interests, bio))
            trainee_ids[email] = cursor.lastrowid

        # 4. Courses
        courses = [
            (
                "Advanced Numerical Weather Prediction (NWP) & High-Resolution Modeling",
                "IMD-NWP-201", "Numerical Weather Prediction", "Advanced", 25,
                "Comprehensive capacity building course covering atmospheric governing equations, finite-difference & spectral discretizations, high-performance computing, data assimilation techniques (3D-Var, 4D-Var), WRF model configuration, and ensemble forecasting systems operational at IMD.",
                trainer_ids["dr.m.sharma@imd.gov.in"]
            ),
            (
                "Doppler Weather Radar (DWR) Principles, Data Interpretation & Nowcasting",
                "IMD-RAD-101", "Radar Meteorology", "Intermediate", 20,
                "Hands-on training module on S-Band, C-Band, and X-Band Doppler Weather Radars. Learn Plan Position Indicator (PPI), Range Height Indicator (RHI), Velocity Azimuth Display (VAD), hydrometeor classification, mesocyclone detection, and severe storm nowcasting algorithms.",
                trainer_ids["dr.ananya.das@imd.gov.in"]
            ),
            (
                "Satellite Meteorology & INSAT-3DR Multi-Spectral Product Analysis",
                "IMD-SAT-102", "Satellite Meteorology", "Intermediate", 18,
                "In-depth operational training on Indian geostationary meteorological satellites (INSAT-3D, INSAT-3DR, INSAT-3DS). Topics include Visible, Infrared, Water Vapor imagery interpretation, Atmospheric Motion Vectors (AMVs), Outgoing Longwave Radiation (OLR), and quantitative precipitation estimates.",
                trainer_ids["dr.r.venkatesh@imd.gov.in"]
            ),
            (
                "Tropical Cyclogenesis, Track Forecasting & Early Warning Dissemination",
                "IMD-CYC-301", "Cyclone Forecasting", "Advanced", 22,
                "Specialized masterclass on North Indian Ocean tropical cyclone dynamics, Dvorak technique for intensity estimation, multi-model ensemble consensus tracking, storm surge modeling, cone of uncertainty generation, and bulletined warning protocols.",
                trainer_ids["dr.r.venkatesh@imd.gov.in"]
            ),
            (
                "Operational Agrometeorological Advisory Services (AAS) & Crop Weather Dynamics",
                "IMD-AGR-101", "Agrometeorology", "Beginner", 15,
                "Essential training on Gramin Krishi Mausam Sewa (GKMS), district-level weather forecast interpretation, crop phenological stages, weather-pest-disease correlations, preparation of dynamic agro-advisories, and multi-channel dissemination.",
                trainer_ids["dr.priya.nair@imd.gov.in"]
            ),
            (
                "Seismological Network Monitoring, Earthquake Location & Tsunami Warning Systems",
                "IMD-SEIS-202", "Seismology & Tsunami", "Intermediate", 20,
                "Comprehensive curriculum on broadband seismometer instrumentation, real-time seismic phase picking (P and S waves), hypocenter and magnitude determination (Mw, Mb), focal mechanism solutions, and early tsunami warning modeling for coastal regions.",
                trainer_ids["dr.k.murthy@imd.gov.in"]
            ),
            (
                "Applied AI/ML & Deep Learning for Extreme Weather & Nowcasting",
                "IMD-AI-401", "Artificial Intelligence in Meteorology", "Advanced", 30,
                "Advanced capacity building on Physics-Informed Neural Networks (PINNs), ConvLSTM for radar echo extrapolation, Transformer models for precipitation nowcasting, and machine learning post-processing of numerical ensemble forecasts.",
                trainer_ids["dr.m.sharma@imd.gov.in"]
            ),
            (
                "Aviation Meteorology & ICAO Aerodrome Met Office (AMO) Standards",
                "IMD-AVN-201", "Aviation Meteorology", "Intermediate", 20,
                "Operational training on METAR, SPECI, TAF formulation, terminal aerodrome weather radar, low-level wind shear detection systems (LLWAS), runway visual range (RVR) instrumentation, and SIGMET issuance for clear-air turbulence and convective storms.",
                trainer_ids["dr.ananya.das@imd.gov.in"]
            ),
            (
                "Operational Ocean State Forecasting, Storm Surges & Coastal Hazard Warning",
                "INCOIS-OCN-301", "Oceanographic Sciences", "Advanced", 24,
                "Collaborative MoES/INCOIS curriculum covering coastal sea-state prediction, wave-rider buoy telemetry, High-Frequency (HF) radar surface currents, hydrodynamic storm surge modeling (ADCIRC/IITD model), and coastal inundation warning dissemination.",
                trainer_ids["dr.r.venkatesh@imd.gov.in"]
            ),
            (
                "Climate Dynamics, Monsoonal Teleconnections & Extended Range Forecasting",
                "IMD-CLIM-302", "Climatology & Climate Change", "Intermediate", 22,
                "Systematic training on coupled climate models, El Niño Southern Oscillation (ENSO), Indian Ocean Dipole (IOD), Madden-Julian Oscillation (MJO), drought monitoring indicators, and sub-seasonal to seasonal (S2S) monsoon predictions.",
                trainer_ids["dr.priya.nair@imd.gov.in"]
            ),
            (
                "High-Performance Computing (HPC), GPU Acceleration & Earth System Modeling",
                "NCMRWF-HPC-501", "HPC & Scientific Computing", "Advanced", 25,
                "Practical training on MoES supercomputing clusters (Pratyush & Mihir), MPI/OpenMP parallelization of atmospheric dynamical cores, GPU-accelerated microphysics schemes, and Petascale data I/O management with NetCDF-4/Zarr.",
                trainer_ids["dr.m.sharma@imd.gov.in"]
            ),
            (
                "Dual-Polarimetric Doppler Radar Urban Hydrometeorology & Flash Flood Nowcasting",
                "IMD-RAD-302", "Radar Meteorology", "Advanced", 20,
                "Urban nowcasting techniques using high-resolution X-band dual-polarimetric radars, Quantitative Precipitation Estimation (QPE) algorithms, Specific Differential Phase (Kdp) rain rate derivation, and integration with city drainage hydrodynamic models.",
                trainer_ids["dr.ananya.das@imd.gov.in"]
            )
        ]

        course_ids = []
        for title, code, domain, level, duration, desc, t_id in courses:
            cursor.execute("""
                INSERT INTO courses (title, code, domain, level, duration_hours, description, trainer_id, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'published')
            """, (title, code, domain, level, duration, desc, t_id))
            course_ids.append(cursor.lastrowid)

        # 5. Course Modules & Lessons for NWP
        nwp_id = course_ids[0]
        cursor.execute("INSERT INTO course_modules (course_id, title, order_num, summary) VALUES (?, 'Module 1: Atmospheric Dynamics & Governing Equations', 1, 'Navier-Stokes equations, hydrostatic approximation, and thermodynamic principles')", (nwp_id,))
        m1_id = cursor.lastrowid
        cursor.execute("INSERT INTO course_lessons (module_id, course_id, title, lesson_type, content_url, duration_mins, notes, order_num) VALUES (?, ?, '1.1 Primitive Equations and Coordinate Systems in NWP', 'video', 'https://www.youtube.com/embed/dQw4w9WgXcQ', 25, 'Understanding sigma, isobaric, and hybrid coordinate systems.', 1)", (m1_id, nwp_id))
        cursor.execute("INSERT INTO course_lessons (module_id, course_id, title, lesson_type, content_url, duration_mins, notes, order_num) VALUES (?, ?, '1.2 Numerical Discretization and Grid Staggering (Arakawa Grids)', 'presentation', '/static/docs/NWP_Arakawa_Grids.pdf', 30, 'Error dispersion analysis on Arakawa C-grid.', 2)", (m1_id, nwp_id))

        cursor.execute("INSERT INTO course_modules (course_id, title, order_num, summary) VALUES (?, 'Module 2: Data Assimilation & Observational Integration', 2, 'Methods for synthesizing satellite, radar, and radiosonde observations into initial conditions')", (nwp_id,))
        m2_id = cursor.lastrowid
        cursor.execute("INSERT INTO course_lessons (module_id, course_id, title, lesson_type, content_url, duration_mins, notes, order_num) VALUES (?, ?, '2.1 Principles of 3D-Var and 4D-Var Data Assimilation', 'video', 'https://www.youtube.com/embed/dQw4w9WgXcQ', 35, 'Cost function minimization and Background Error Covariance (B-Matrix).', 1)", (m2_id, nwp_id))
        cursor.execute("INSERT INTO course_lessons (module_id, course_id, title, lesson_type, content_url, duration_mins, notes, order_num) VALUES (?, ?, '2.2 WRFDA System Operational Implementation', 'document', '/static/docs/WRFDA_Operational_Guide.pdf', 40, 'Configuring WRFDA namelist for Indian region domain.', 2)", (m2_id, nwp_id))

        # Modules for Radar
        rad_id = course_ids[1]
        cursor.execute("INSERT INTO course_modules (course_id, title, order_num, summary) VALUES (?, 'Module 1: Radar Hardware & Electromagnetic Principles', 1, 'Radar equation, antenna beamwidth, PRF, and Doppler dilemma')", (rad_id,))
        rm1_id = cursor.lastrowid
        cursor.execute("INSERT INTO course_lessons (module_id, course_id, title, lesson_type, content_url, duration_mins, notes, order_num) VALUES (?, ?, '1.1 Dual-Polarization Parameters: Zdr, Kdp, and RhoHV', 'video', 'https://www.youtube.com/embed/dQw4w9WgXcQ', 30, 'Physical interpretation of differential reflectivity and specific differential phase.', 1)", (rm1_id, rad_id))
        cursor.execute("INSERT INTO course_lessons (module_id, course_id, title, lesson_type, content_url, duration_mins, notes, order_num) VALUES (?, ?, '1.2 Severe Thunderstorm Signatures: Hook Echo & Velocity Couplets', 'presentation', '/static/docs/DWR_Severe_Signatures.pdf', 35, 'Analyzing Doppler velocity dipoles for tornado and microburst nowcasting.', 2)", (rm1_id, rad_id))

        # Modules for Satellite
        sat_id = course_ids[2]
        cursor.execute("INSERT INTO course_modules (course_id, title, order_num, summary) VALUES (?, 'Module 1: INSAT-3DR Payloads & Imagery Interpretation', 1, 'Multi-spectral imager and sounder payload channels')", (sat_id,))
        sm1_id = cursor.lastrowid
        cursor.execute("INSERT INTO course_lessons (module_id, course_id, title, lesson_type, content_url, duration_mins, notes, order_num) VALUES (?, ?, '1.1 INSAT-3DR Thermal IR & Water Vapor Band Analysis', 'video', 'https://www.youtube.com/embed/dQw4w9WgXcQ', 25, 'Identifying upper-tropospheric jet streams and moisture convergence.', 1)", (sm1_id, sat_id))

        # 6. Quizzes
        cursor.execute("""
            INSERT INTO quizzes (course_id, trainer_id, title, subject, duration_mins, pass_percentage, deadline)
            VALUES (?, ?, 'NWP Modeling & Data Assimilation Assessment', 'Numerical Weather Prediction', 25, 70, ?)
        """, (nwp_id, trainer_ids["dr.m.sharma@imd.gov.in"], (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')))
        quiz1_id = cursor.lastrowid

        nwp_q = [
            (
                "Which Arakawa grid staggering is most widely used in the Weather Research and Forecasting (WRF) dynamical core for conserving mass and kinetic energy?",
                "Arakawa A-grid (Unstaggered)", "Arakawa B-grid", "Arakawa C-grid", "Arakawa E-grid", "C",
                "WRF ARW uses the Arakawa C-grid where velocity components u and v are staggered half a grid point from thermodynamic variables."
            ),
            (
                "In 3D-Var Data Assimilation, what is the primary role of the Background Error Covariance Matrix (B-Matrix)?",
                "To eliminate observational errors completely",
                "To spread observational information spatially and balance variables dynamically",
                "To speed up computer execution by reducing grid resolution",
                "To replace satellite soundings with ground observations",
                "B",
                "The B-matrix distributes observational increments spatially and provides cross-variable physical coupling."
            ),
            (
                "Which Courant-Friedrichs-Lewy (CFL) stability criterion condition must be satisfied in explicit time-stepping schemes?",
                "C = u * (dt / dx) <= 1", "C = u * (dx / dt) >= 1", "C = dt * dx / u == 0", "C = u^2 / (dx * dt) <= 0.5", "A",
                "The CFL condition requires that numerical information propagation speed does not exceed grid resolution over time step."
            ),
            (
                "What is the primary physical process represented by convective parameterization schemes in NWP models?",
                "Radiative cooling of cloud tops",
                "Sub-grid scale vertical transport of heat, moisture, and momentum by cumulus clouds",
                "Soil moisture percolation to deep aquifers",
                "Surface frictional drag over mountainous topography",
                "B",
                "Convective parameterization accounts for unresolved subgrid-scale deep and shallow convection that transports heat and moisture vertically."
            ),
            (
                "In an Ensemble Prediction System (EPS), how is forecast uncertainty typically quantified?",
                "By taking only the single most extreme outlier forecast",
                "By calculating the ensemble spread (standard deviation) and ensemble probability distributions",
                "By averaging past historical climate data with the forecast",
                "By ignoring initial condition perturbations",
                "B",
                "Ensemble spread provides an objective measure of atmospheric flow predictability and forecast confidence."
            )
        ]

        for q_text, oa, ob, oc, od, corr, expl in nwp_q:
            cursor.execute("""
                INSERT INTO quiz_questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (quiz1_id, q_text, oa, ob, oc, od, corr, expl))

        # Quiz 2 for Radar Course
        cursor.execute("""
            INSERT INTO quizzes (course_id, trainer_id, title, subject, duration_mins, pass_percentage, deadline)
            VALUES (?, ?, 'Doppler Weather Radar Interpretation & Nowcasting Quiz', 'Radar Meteorology', 20, 70, ?)
        """, (rad_id, trainer_ids["dr.ananya.das@imd.gov.in"], (datetime.now() + timedelta(days=25)).strftime('%Y-%m-%d %H:%M:%S')))
        quiz2_id = cursor.lastrowid

        rad_q = [
            (
                "What Doppler radar signature is characterized by strong inbound and outbound velocities adjacent to each other?",
                "Uniform Stratiform Flow", "Velocity Couplet (Mesocyclone Signature)", "Ground Clutter Echo", "Bright Band Melting Layer", "B",
                "A velocity couplet depicts rotation in severe thunderstorm supercells."
            ),
            (
                "What does a high Differential Reflectivity (Zdr > 3.0 dB) combined with high Horizontal Reflectivity (Zh > 50 dBZ) typically indicate?",
                "Small isotropic cloud droplets", "Large, horizontally flattened oblate raindrops", "Tumbling spherical dry hailstones", "Insect clutter", "B",
                "Large raindrops flatten horizontally as they fall due to aerodynamic drag, causing positive Zdr."
            ),
            (
                "The Doppler Dilemma describes the trade-off between which two radar operational parameters?",
                "Maximum unambiguous range (Rmax) and maximum unambiguous velocity (Vmax)",
                "Transmitter power and antenna diameter",
                "Radar wavelength and pulse duration",
                "Beam elevation angle and scan rotation speed",
                "A",
                "Rmax * Vmax = c * wavelength / 8. Increasing unambiguous range decreases maximum measurable velocity without aliasing."
            ),
            (
                "In Radar Meteorology, what causes the 'Bright Band' observed in vertical profiles of reflectivity?",
                "Direct solar reflection into the antenna",
                "Melting of snow aggregates into raindrops near the freezing 0°C isotherm",
                "Smoke plumes from fires",
                "Anomalous propagation through temperature inversions",
                "B",
                "Melting ice particles acquire a water coating, drastically increasing dielectric constant and reflectivity."
            )
        ]

        for q_text, oa, ob, oc, od, corr, expl in rad_q:
            cursor.execute("""
                INSERT INTO quiz_questions (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (quiz2_id, q_text, oa, ob, oc, od, corr, expl))

        # 7. Seed Rahul Verma Enrollment & Earned Certificate
        r_id = trainee_ids["trainee.verma@imd.gov.in"]
        cursor.execute("""
            INSERT INTO enrollments (user_id, course_id, enrolled_at, progress_percent, completed_lessons, status, completed_at)
            VALUES (?, ?, ?, 100, '[1,2,3,4]', 'completed', ?)
        """, (r_id, nwp_id, (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'), (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')))
        
        cursor.execute("""
            INSERT INTO enrollments (user_id, course_id, enrolled_at, progress_percent, completed_lessons, status)
            VALUES (?, ?, ?, 50, '[5]', 'in_progress')
        """, (r_id, rad_id, (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')))

        user_ans = json.dumps({"1": "C", "2": "B", "3": "A", "4": "B", "5": "B"})
        cursor.execute("""
            INSERT INTO quiz_attempts (quiz_id, user_id, course_id, score, total_marks, percentage, is_passed, user_answers, attempted_at)
            VALUES (?, ?, ?, 5, 5, 100.0, 1, ?, ?)
        """, (quiz1_id, r_id, nwp_id, user_ans, (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')))

        cert_id = "IMD-CB-2026-8921"
        v_url = f"/verify/certificate/{cert_id}"
        qr_data = f"MoES/IMD CAPACITY CONNECT | Certificate ID: {cert_id} | Recipient: Rahul Verma | Course: Advanced Numerical Weather Prediction (NWP) | Score: 100% | Grade: Outstanding | Verified by MoES Training Directorate"
        cursor.execute("""
            INSERT INTO certificates (certificate_id, user_id, course_id, issue_date, grade, score_percentage, qr_data, verification_url)
            VALUES (?, ?, ?, ?, 'Outstanding', 100.0, ?, ?)
        """, (cert_id, r_id, nwp_id, (date.today() - timedelta(days=2)).strftime('%Y-%m-%d'), qr_data, v_url))

        cursor.execute("""
            INSERT INTO course_feedback (course_id, user_id, trainer_id, rating_content, rating_trainer, rating_overall, comments)
            VALUES (?, ?, ?, 5, 5, 5, 'Exceptional training by Dr. Madhavan Sharma. The hands-on WRFDA workflows and Arakawa grid formulations directly helped our operational cyclone forecasting team at IMD.')
        """, (nwp_id, r_id, trainer_ids["dr.m.sharma@imd.gov.in"]))

        # 8. Seed Trainer Library
        lib_items = [
            (
                trainer_ids["dr.m.sharma@imd.gov.in"],
                "WRF Model Operational Architecture & Parallel HPC Scaling Compendium",
                "presentation_ppt", "Numerical Weather Prediction",
                "/static/docs/WRF_Parallel_Architecture.pdf", "14.8 MB",
                "Detailed presentation slide deck detailing MPI/OpenMP domain decomposition and I/O optimization for high-resolution 3km runs on MoES Pratyush & Mihir supercomputers."
            ),
            (
                trainer_ids["dr.ananya.das@imd.gov.in"],
                "Dual-Polarization Doppler Weather Radar Calibration Dataset",
                "meteorological_dataset", "Radar Meteorology",
                "/static/docs/DWR_Kolkata_SevereStorm_Case.nc", "45.2 MB",
                "Standard NetCDF/HDF5 radar dataset from Kolkata DWR capturing Severe Nor'wester squall line passage with dual-pol moments."
            ),
            (
                trainer_ids["dr.r.venkatesh@imd.gov.in"],
                "INSAT-3DR Geostationary Radiance Processing & Rapid Scan Guide",
                "study_guide_pdf", "Satellite Meteorology",
                "/static/docs/INSAT3DR_Radiance_Guide.pdf", "8.5 MB",
                "Comprehensive manual detailing calibration coefficients and cloud mask generation algorithms."
            ),
            (
                trainer_ids["dr.priya.nair@imd.gov.in"],
                "Agromet Advisory Service Bulletin Standard Operating Procedures (SOP 2026)",
                "study_guide_pdf", "Agrometeorology",
                "/static/docs/Agromet_SOP_IMD_2026.pdf", "5.1 MB",
                "Official guidelines for State and District Agromet Units (DAMUs) for issuing block-level agro-meteorological advisories."
            )
        ]

        for t_id, title, r_type, cat, f_url, f_size, desc in lib_items:
            cursor.execute("""
                INSERT INTO trainer_library (trainer_id, title, resource_type, category, file_url, file_size, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (t_id, title, r_type, cat, f_url, f_size, desc))

        # 9. Seed Announcements
        announcements = [
            (
                "National Capacity Building Workshop on AI/ML in Monsoon Prediction 2026",
                "The Ministry of Earth Sciences (MoES) and India Meteorological Department (IMD) announce a 5-day specialized capacity building program on applying Deep Learning to medium-range monsoon rainfall forecasting. Nominations open for IMD, NCMRWF, and IITM scientists.",
                "Workshop", "Urgent", admin_id
            ),
            (
                "Operational Commissioning of 10 New X-Band Doppler Radars in Western Ghats",
                "Under the Mission Mausam initiative, IMD has commissioned 10 high-resolution X-band Doppler Weather Radars along the Western Ghats. Trainees are encouraged to enroll in 'IMD-RAD-101' for operational interpretation certification.",
                "Achievement", "Important", admin_id
            ),
            (
                "Launch of New Specialized Course: Tropical Cyclogenesis & Track Forecasting (IMD-CYC-301)",
                "A new advanced training module designed by Dr. R. Venkatesh is now live on CAPACITY CONNECT. Staff from Regional Cyclone Warning Centers are mandated to complete certification by Q3 2026.",
                "New Course", "Normal", admin_id
            ),
            (
                "MoES Circular: Mandatory Competency Mapping for Senior Meteorological Trainers",
                "All Scientist-D and above personnel across MoES institutions are requested to review and update their domain skills and research publications on the portal to facilitate automated Trainer Competency Mapping for upcoming national programs.",
                "Circular", "Important", admin_id
            )
        ]

        for title, content, cat, prio, pub_by in announcements:
            cursor.execute("""
                INSERT INTO announcements (title, content, category, priority, published_by)
                VALUES (?, ?, ?, ?, ?)
            """, (title, content, cat, prio, pub_by))

        print(f"CAPACITY CONNECT {db_type} database successfully initialized and seeded!")
