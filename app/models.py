from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "trainee"
    designation: Optional[str] = ""
    department: Optional[str] = ""
    qualifications: Optional[str] = ""
    experience_years: Optional[int] = 0
    skills: Optional[str] = ""
    interests: Optional[str] = ""
    bio: Optional[str] = ""

class UserLoginRequest(BaseModel):
    email: str
    password: str

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    qualifications: Optional[str] = None
    experience_years: Optional[int] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    bio: Optional[str] = None

class CourseCreateRequest(BaseModel):
    title: str
    code: str
    domain: str
    level: str = "Intermediate"
    duration_hours: int = 20
    description: str
    thumbnail_url: Optional[str] = None

class QuizCreateRequest(BaseModel):
    course_id: int
    title: str
    subject: str
    duration_mins: int = 20
    pass_percentage: int = 70
    deadline: Optional[str] = None
    questions: List[Dict[str, Any]]

class QuizSubmitRequest(BaseModel):
    quiz_id: int
    answers: Dict[str, str]

class FeedbackSubmitRequest(BaseModel):
    course_id: int
    rating_content: int = Field(..., ge=1, le=5)
    rating_trainer: int = Field(..., ge=1, le=5)
    rating_overall: int = Field(..., ge=1, le=5)
    comments: Optional[str] = ""

class AnnouncementCreateRequest(BaseModel):
    title: str
    content: str
    category: str = "Announcement"
    priority: str = "Normal"

class CompetencyQueryRequest(BaseModel):
    subject: str
    domain: Optional[str] = None
    required_skills: Optional[List[str]] = []
    min_experience: Optional[int] = 0
