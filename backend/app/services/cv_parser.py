# app/services/cv_parser.py

import io
import re
from typing import Dict, List, Optional

import pdfplumber
from fastapi import UploadFile, HTTPException, status


def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extract raw text from an uploaded PDF file.

    We don't store the file here; we just read content from the UploadFile.
    """
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF CV files are supported at the moment.",
        )

    try:
        content = file.file.read()
        file.file.seek(0)
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            texts = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(texts)
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from PDF.",
            )
        return text
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read CV PDF file.",
        )


def parse_cv_text(text: str) -> Dict[str, Optional[object]]:
    """
    Very simple, rule-based CV parser.

    This is intentionally modular so you can later replace it with
    a more advanced NLP-based parser without changing the API.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # --- full name: naive heuristic = first non-empty line
    full_name: Optional[str] = lines[0] if lines else None

    # --- degree
    degree_pattern = (
        r"(BSc|B\.Sc|Bachelors?|Bachelor of|BBA|MBA|MSc|M\.Sc|MCA|BCA)[^,\n]*"
    )
    degree_match = re.search(degree_pattern, text, flags=re.IGNORECASE)
    degree = degree_match.group(0).strip() if degree_match else None

    # --- university
    university: Optional[str] = None
    for ln in lines:
        lower = ln.lower()
        if "university" in lower or "campus" in lower or "college" in lower:
            university = ln.strip()
            break

    # --- CGPA
    cgpa: Optional[float] = None
    cgpa_match = re.search(r"cgpa[:\s]+(\d\.\d+)", text, flags=re.IGNORECASE)
    if cgpa_match:
        try:
            cgpa = float(cgpa_match.group(1))
        except ValueError:
            cgpa = None

    # --- skills
    skills: List[str] = []
    skills_section = ""

    for i, ln in enumerate(lines):
        if "skill" in ln.lower():
            # take the next few lines as skill lines
            for j in range(i + 1, min(i + 6, len(lines))):
                skills_section += " " + lines[j]
            break

    if skills_section:
        raw_tokens = re.split(r"[,\u2022;\-\|/]+", skills_section)
        for token in raw_tokens:
            t = token.strip().lower()
            if len(t) >= 2:
                skills.append(t)

    # de-duplicate
    skills = sorted(set(skills))

    return {
        "full_name": full_name,
        "degree": degree,
        "university": university,
        "cgpa": cgpa,
        "skills": skills,
    }
