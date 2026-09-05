# CAPACITY CONNECT
### A Digital Capacity Building and Learning Management Portal
**Organization:** Ministry of Earth Sciences (MoES)  
**Department:** India Meteorological Department (IMD)  
**Category:** Software (Smart India Hackathon)

---

## 🌟 Executive Summary & Problem Overview

**CAPACITY CONNECT** is a centralized, digital capacity building and learning management platform engineered specifically for the **Ministry of Earth Sciences (MoES)** and the **India Meteorological Department (IMD)**. The portal addresses the critical national need for systematic competency development, real-time knowledge dissemination, observational training, and intelligent subject-matter expert allocation across atmospheric, oceanographic, and seismological institutions in India.

---

## 🚀 Key Modules & Functional Capabilities

### 1. 🛡️ Role-Based Authentication & Access Control
- **Three Distinct User Personas**:
  - **Trainee**: Operational meteorologists, observers, scientific assistants, and researchers.
- **Three Distinct User Personas & Registration**:
  - **Trainee**: Operational meteorologists, observers, scientific assistants, and researchers (instant activation).
  - **Trainer**: Senior scientists (Scientist-E/F/G), university professors, and domain experts (queued for administrative verification).
  - **Admin**: Director of Capacity Building, MoES/IMD administrative authorities (supports official security token `MOES-ADMIN-2026` for instant clearance, or queued for Director review).
- **Administrative Clearance & Approval Gate**: New trainers and unverified admins undergo administrative review before elevated permissions are granted.
- **1-Click Demo Persona Switcher**: Instant evaluation modal to switch between Admin, Trainer, and Trainee accounts.

### 2. 🎓 Trainee Learning & Certification Journey
- **Professional Profile Dossier**: Comprehensive record of qualifications, observatory assignments, years of experience, core competencies, and earned certificates.
- **Domain Curricula Discovery**: Filter and search across 12 specialized MoES disciplines:
  - Numerical Weather Prediction (NWP) & High-Resolution Modeling (`IMD-NWP-201`)
  - Doppler Weather Radar (DWR) Principles & Severe Storm Nowcasting (`IMD-RAD-101`)
  - Satellite Meteorology & INSAT-3DR Multi-Spectral Product Analysis (`IMD-SAT-102`)
  - Tropical Cyclogenesis, Track Forecasting & Early Warnings (`IMD-CYC-301`)
  - Operational Agrometeorological Advisory Services (AAS & GKMS) (`IMD-AGR-101`)
  - Seismological Network Monitoring & Tsunami Warning Systems (`IMD-SEIS-202`)
  - Applied AI/ML & Deep Learning for Extreme Weather & Nowcasting (`IMD-AI-401`)
  - Aviation Meteorology & ICAO Aerodrome Met Office Standards (`IMD-AVN-201`)
  - Operational Ocean State Forecasting & Storm Surge Inundation (`INCOIS-OCN-301`)
  - Climate Dynamics & Extended Range Monsoonal Teleconnections (`IMD-CLIM-302`)
  - High-Performance Computing (HPC) & GPU Earth System Modeling (`NCMRWF-HPC-501`)
  - Dual-Polarimetric Doppler Radar Urban Hydrometeorology (`IMD-RAD-302`)
- **Interactive Learning Room**: High-definition video lectures, presentation slide decks (PPT/PDF), and lesson completion checklists.
- **Real-Time Timed MCQ Assessment Engine**: Countdown clock, question navigator palette, instant auto-grading, and pedagogical answer reviews with scientific explanations.
- **Verifiable Digital Certificates**: Automatic issuance for scores \(\ge 70\%\), featuring authentic Government of India/MoES styling, unique Certificate IDs (e.g. `IMD-CB-2026-8921`), and scannable QR verification.
- **Course & Trainer Evaluation**: Multi-criteria 5-star feedback rating system.

### 3. 👨‍🏫 Trainer Authoring Suite
- **Questionnaire & MCQ Assessment Builder**: Create subject-specific quizzes with customizable timers, passing thresholds, deadlines, and dynamic question addition with answer explanations.
- **Trainer Resource Library**: Centralized repository for uploading recorded lectures, slide decks (PPTX/PDF), operational manuals, and raw meteorological observational datasets (NetCDF/GRIB2).
- **Trainee Roster & Progress Tracking**: Real-time visibility into enrolled officers, module completion percentages, quiz attempts, and pass/fail distributions.
- **Question Difficulty Index**: Detailed question-level analytics to identify topics requiring additional capacity building.

### 4. ⚙️ Admin Command Center & Governance
- **Executive Analytics Dashboard**: High-level KPIs and interactive Chart.js visualizations:
  - Regional Meteorological Center (RMC) Participation (North, South, East, West, North-East, NCS).
  - Discipline Distribution Doughnut Chart.
  - Monthly certification and pass rate trends.
- **User Directory & Approval Queue**: 1-click Approve/Reject for pending trainer applications, role reassignment, and status management.
- **Intelligent Competency Mapping Engine**: Smart matching algorithm calculating composite fit scores based on Skill Overlap (50%), Domain Relevance (25%), Seniority (15%), and Trainee Feedback (10%) to recommend top trainers for any atmospheric science subject.
- **Portal Communications & Bulletin Board**: Publish, update, and manage official circulars, workshop notices, achievements, and course spotlights on the homepage.

---

## 🔑 Demo Access & Pre-Seeded Accounts

The database comes pre-populated with realistic MoES/IMD data and accounts for immediate evaluation:

| Role | Name & Designation | Email Address | Password |
| :--- | :--- | :--- | :--- |
| **Admin** | Dr. Rajeshwar Rao (Director of Training, MoES) | `admin@imd.gov.in` | `Admin@123` |
| **Trainer** | Dr. Madhavan Sharma (Scientist-G, NWP Division) | `dr.m.sharma@imd.gov.in` | `Trainer@123` |
| **Trainer** | Dr. Ananya Das (Scientist-F, Radar Division) | `dr.ananya.das@imd.gov.in` | `Trainer@123` |
| **Trainee** | Rahul Verma (Meteorologist Grade-I, Cyclone Warning) | `trainee.verma@imd.gov.in` | `Trainee@123` |
| **Trainee** | Sneha Patel (Scientific Assistant, DWR Bhuj) | `sneha.patel@imd.gov.in` | `Trainee@123` |
| **Pending Trainer** | Prof. Tarun Verma (Visiting Climate Scientist, IITM Pune) | `prof.tarun.verma@iitm.ac.in` | `Trainer@123` |

> *Tip: Click the gold **"1-Click Demo Login"** button in the top navigation bar to test any persona without typing credentials.*

---

## 🛠️ Technology Stack & Architecture

- **Backend Framework**: FastAPI (Python 3.14) with async handlers and Pydantic validation.
- **Database**: SQLite with relational schema, foreign key enforcement, and automated migrations.
- **Frontend & UI**: Tailwind CSS, Lucide Icons, Chart.js for data visualization, and responsive HTML5/Jinja2 templates.
- **Security**: PBKDF2-HMAC-SHA256 salted password hashing, HTTP-only signed session tokens, and role-based middleware guards.
- **Certification Engine**: Real-time cryptographic certificate ID generator with QR validation endpoint (`/verify/certificate/{id}`).

---

## 🏁 Quickstart & How to Run

### 1. Start the Server
```bash
python run.py
```

### 2. Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🧪 Verification & Demonstration Guide

1. **Test Trainee Flow**:
   - Log in as Trainee (`trainee.verma@imd.gov.in` or 1-Click Trainee Login).
   - Navigate to **Course Catalog** and open "Doppler Weather Radar (DWR) Principles" (`IMD-RAD-101`).
   - Launch the **Certification Assessment**, select your answers, and submit.
   - Review your scorecard, answer explanations, and view your auto-generated **Certificate of Competency** with QR code.

2. **Test Trainer Flow**:
   - Log in as Trainer (`dr.m.sharma@imd.gov.in` or 1-Click Trainer Login).
   - Go to **Create Quiz**, configure a timer and passing mark, and add custom MCQ questions.
   - Go to **Trainer Library** and upload presentation slides or NetCDF datasets.
   - Check **Trainee Analytics** for roster scores.

3. **Test Admin Flow**:
   - Log in as Admin (`admin@imd.gov.in` or 1-Click Admin Login).
   - Review **Executive Analytics** (RMC participation charts, domain distribution).
   - Go to **User Approvals** and approve the pending registration of `Prof. Tarun Verma`.
   - Open **Competency Map**, search for *"Doppler Weather Radar Nowcasting"*, and view AI-ranked trainers with score breakdowns.
   - Publish a new circular in **Bulletins** and verify its appearance on the homepage notice ticker.

---
*Developed for Ministry of Earth Sciences (MoES) & India Meteorological Department (IMD) - Smart India Hackathon.*
