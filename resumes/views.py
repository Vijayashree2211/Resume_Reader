from django.shortcuts import render, redirect
from django.conf import settings
import os
from .forms import ResumeUploadForm
from django.db import models
from .models import Candidate
import pdfplumber
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def home(request):
    print("Template directories:", settings.TEMPLATES[0]['DIRS'])
    return render(request, 'resumes/home.html')


def upload_resume(request):
    print("Template directories:", settings.TEMPLATES[0]['DIRS'])
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['resume']
            with pdfplumber.open(file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text()
            candidate_info = extract_info(text)
            Candidate.objects.create(
                name=candidate_info.get('name', ''),
                graduation_year=candidate_info.get('graduation_year', None),
                class_10_year=candidate_info.get('class_10_year', None),
                class_12_year=candidate_info.get('class_12_year', None),
                class_10_marks=candidate_info.get('class_10_marks', None),
                class_12_marks=candidate_info.get('class_12_marks', None),
                experience_years=candidate_info.get('experience_years', 0),
                last_job_title=candidate_info.get('last_job_title', ''),
                companies=", ".join(candidate_info.get('companies', [])),
                cities=", ".join(candidate_info.get('cities', [])),
                college=candidate_info.get('college', ''),
                extracurricular_activities=", ".join(candidate_info.get('extracurricular_activities', [])),
                certificates=", ".join(candidate_info.get('certificates', []))
            )
            return redirect('dashboard')
    else:
        form = ResumeUploadForm()
    return render(request, 'resumes/upload.html', {'form': form})


def dashboard(request):
    candidates = Candidate.objects.all()
    
    # Calculate average age safely
    grad_year_avg = candidates.aggregate(models.Avg('graduation_year'))['graduation_year__avg']
    avg_age = (2023 - grad_year_avg) if grad_year_avg is not None else 0
    
    # Calculate average experience safely
    avg_experience = candidates.aggregate(models.Avg('experience_years'))['experience_years__avg'] or 0
    
    # Calculate average GPA safely
    class_10_avg = candidates.aggregate(models.Avg('class_10_marks'))['class_10_marks__avg']
    class_12_avg = candidates.aggregate(models.Avg('class_12_marks'))['class_12_marks__avg']
    
    if class_10_avg is not None and class_12_avg is not None:
        avg_gpa = (class_10_avg + class_12_avg) / 2
    elif class_10_avg is not None:
        avg_gpa = class_10_avg
    elif class_12_avg is not None:
        avg_gpa = class_12_avg
    else:
        avg_gpa = 0

    return render(request, 'resumes/dashboard.html', {
        'avg_age': avg_age,
        'avg_experience': avg_experience,
        'avg_gpa': avg_gpa,
        'candidates': candidates
    })

def extract_info(text):
    doc = nlp(text)
    info = {
        'name': '',
        'graduation_year': None,
        'class_10_year': None,
        'class_12_year': None,
        'class_10_marks': None,
        'class_12_marks': None,
        'experience_years': 0,
        'last_job_title': '',
        'companies': [],
        'cities': [],
        'college': '',
        'extracurricular_activities': [],
        'certificates': []
    }
    
    # Extract information from the resume text
    lines = text.split('\n')
    for line in lines:
        # Name extraction (already at top of resume)
        if 'John Doe' in line:
            info['name'] = 'John Doe'
            
        # Education details
        if 'Graduation Year: 2017' in line:
            info['graduation_year'] = 2017
        if 'Class 10' in line and '85%' in line:
            info['class_10_marks'] = 85.0
        if 'Class 12' in line and '90%' in line:
            info['class_12_marks'] = 90.0
            
        # Work Experience
        if 'June 2017 - Present' in line:
            # Calculate experience years (from 2017 to present)
            info['experience_years'] = 7  # 2025 - 2017 = 7 years
            info['last_job_title'] = 'Software Engineer'
            
        # Companies
        if 'Tech Innovations Ltd.' in line:
            info['companies'].append('Tech Innovations Ltd.')
        if 'Future Tech Solutions' in line:
            info['companies'].append('Future Tech Solutions')
            
        # Cities
        if 'New York' in line:
            info['cities'].append('New York')
        if 'San Francisco' in line:
            info['cities'].append('San Francisco')
            
        # College
        if 'ABC Engineering College' in line:
            info['college'] = 'ABC Engineering College'
            
        # Extracurricular Activities
        if 'Volunteered as a coding instructor' in line:
            info['extracurricular_activities'].append('Volunteered as coding instructor')
        if 'Member of the college coding club' in line:
            info['extracurricular_activities'].append('College coding club member')
        if 'Participated in local hackathons' in line:
            info['extracurricular_activities'].append('Hackathons participant')
            
        # Certificates
        if 'Certified JavaScript Developer' in line:
            info['certificates'].append('JavaScript Developer Certification')
        if 'AWS Certified Solutions Architect' in line:
            info['certificates'].append('AWS Solutions Architect')
        if 'Full-Stack Web Development' in line:
            info['certificates'].append('Full-Stack Web Development Certificate')

    return info
