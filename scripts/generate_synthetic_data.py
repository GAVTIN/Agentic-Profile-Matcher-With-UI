"""
Generates the synthetic dataset used by the demo:
  - 100 candidate resumes (data/resumes/CAND-xxx.txt)  -> unstructured text,
    what a real Milestone-1 file-system tool would read off disk / what
    Milestone-2 RAG indexes.
  - data/resumes/_metadata.json -> structured ground truth used only for
    (a) generating readable resume text below and (b) powering MOCK MODE's
    rule-based scorer when no Groq API key is configured. LIVE mode never
    reads this file - it extracts everything itself from the .txt resumes
    via the LLM, exactly like a real system would.
  - 3 sample job descriptions (data/job_descriptions/*.txt)

This is a one-time, build-time script. Its output is committed to the repo,
so cloning the project already gives you a working dataset - you do not
need to re-run this to try the agent. Re-run it only if you want a fresh
(re-seeded) dataset.

Usage:
    python scripts/generate_synthetic_data.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

ROOT = Path(__file__).resolve().parent.parent
RESUME_DIR = ROOT / "data" / "resumes"
JD_DIR = ROOT / "data" / "job_descriptions"
RESUME_DIR.mkdir(parents=True, exist_ok=True)
JD_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Skill pools per track
# --------------------------------------------------------------------------
TRACKS = {
    "frontend": {
        "titles": ["Frontend Engineer", "UI Engineer", "Frontend Developer", "React Developer"],
        "core": ["React", "TypeScript", "JavaScript (ES6+)", "HTML5", "CSS3"],
        "extra": ["Redux", "Next.js", "Vue.js", "Angular", "Webpack", "Vite", "Jest", "Cypress",
                  "Tailwind CSS", "GraphQL", "Storybook", "Web Accessibility (WCAG 2.1)",
                  "Responsive Design", "Micro-frontends", "Framer Motion", "Zustand", "Redux Toolkit",
                  "Figma-to-code workflows", "Performance profiling (Lighthouse)"],
    },
    "backend": {
        "titles": ["Backend Engineer", "Backend Developer", "API Engineer", "Platform Engineer"],
        "core": ["Node.js", "REST API design", "SQL", "Git"],
        "extra": ["Python", "Java", "Go", "Express.js", "Django", "FastAPI", "Spring Boot",
                  "PostgreSQL", "MongoDB", "Redis", "GraphQL", "Microservices", "Docker",
                  "Kubernetes", "RabbitMQ", "Kafka", "JWT/OAuth2", "Unit testing (Jest/PyTest)"],
    },
    "fullstack": {
        "titles": ["Fullstack Engineer", "Fullstack Developer", "Software Engineer (Fullstack)"],
        "core": ["React", "Node.js", "TypeScript", "SQL", "REST API design"],
        "extra": ["Next.js", "Express.js", "MongoDB", "PostgreSQL", "Redux", "Docker", "GraphQL",
                  "AWS", "CI/CD pipelines", "Jest", "Cypress", "Microservices"],
    },
    "data": {
        "titles": ["Data Engineer", "Data Scientist", "Analytics Engineer", "ML Engineer"],
        "core": ["Python", "SQL", "Pandas"],
        "extra": ["NumPy", "Apache Spark", "Airflow", "ETL pipeline design", "Machine Learning",
                  "TensorFlow", "PyTorch", "Tableau", "Power BI", "Snowflake", "dbt",
                  "Statistical modeling", "A/B testing"],
    },
    "devops": {
        "titles": ["DevOps Engineer", "Site Reliability Engineer", "Cloud Infrastructure Engineer"],
        "core": ["Docker", "Kubernetes", "AWS", "CI/CD"],
        "extra": ["Terraform", "Azure", "GCP", "Jenkins", "GitHub Actions", "Ansible",
                  "Prometheus", "Grafana", "Linux administration", "Bash scripting",
                  "Helm", "Service mesh (Istio)"],
    },
    "mobile": {
        "titles": ["Mobile Engineer", "iOS Developer", "Android Developer", "React Native Developer"],
        "core": ["React Native", "JavaScript (ES6+)", "Mobile UI patterns"],
        "extra": ["Swift", "Kotlin", "Flutter", "Xcode", "Android Studio", "Redux",
                  "App Store / Play Store release process", "Push notifications", "TypeScript"],
    },
    "qa": {
        "titles": ["QA Engineer", "SDET", "Test Automation Engineer"],
        "core": ["Test automation", "Manual testing", "JIRA"],
        "extra": ["Selenium", "Cypress", "Playwright", "Postman", "Performance testing (JMeter)",
                  "CI/CD integration", "API testing", "Python", "JavaScript"],
    },
}

DOMAINS = ["Fintech / BFSI", "E-commerce", "Healthcare tech", "EdTech", "SaaS / B2B",
           "Logistics", "Media & streaming", "Gaming", "Travel tech", "Enterprise IT"]

SCHOOLS = ["State University", "Institute of Technology", "National College of Engineering",
           "University of Technology", "Polytechnic Institute", "College of Engineering"]

DEGREES = ["B.S. Computer Science", "B.E. Information Technology", "B.Tech Computer Science",
           "M.S. Computer Science", "B.S. Software Engineering", "B.A. Computer Science"]

CERTS_POOL = ["AWS Certified Solutions Architect – Associate", "AWS Certified Developer – Associate",
              "Certified Kubernetes Administrator (CKA)", "Google Cloud Professional Developer",
              "Meta Front-End Developer Professional Certificate", "PMI Agile Certified Practitioner",
              "MongoDB Certified Developer"]

SENIORITY_BANDS = [(0, 2, "Junior"), (2, 4, "Mid-level"), (4, 7, "Senior"),
                    (7, 11, "Staff/Lead"), (11, 18, "Principal")]


def seniority_for(years: int) -> str:
    for lo, hi, label in SENIORITY_BANDS:
        if lo <= years < hi:
            return label
    return "Principal"


def _clean_name(raw: str) -> str:
    """Faker's name() occasionally adds a prefix ('Dr.', 'Mr.') or suffix
    ('MD', 'Jr.'), which reads oddly on a software-engineering resume. Strip both."""
    for prefix in ("Dr. ", "Mr. ", "Mrs. ", "Ms. ", "Miss "):
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
    for suffix in (" MD", " PhD", " DDS", " DVM", " Jr.", " Sr.", " II", " III", " IV"):
        if raw.endswith(suffix):
            raw = raw[: -len(suffix)]
    return raw


def _dedupe_domains(primary_domain: str, n_prev: int) -> list[str]:
    domains = [primary_domain]
    if n_prev > 1 and random.random() < 0.4:
        others = [d for d in DOMAINS if d != primary_domain]
        domains.append(random.choice(others))
    return domains


def make_candidate(cid: str, track: str, years: int, name: str | None = None,
                    forced_skills: list[str] | None = None, missing_skills: list[str] | None = None,
                    domain: str | None = None) -> dict:
    pool = TRACKS[track]
    name = name or _clean_name(fake.name())
    title = f"{seniority_for(years)} {random.choice(pool['titles'])}" if years >= 2 else random.choice(pool["titles"])

    core = list(pool["core"])
    if missing_skills:
        core = [s for s in core if s not in missing_skills]
    extra_pool = [s for s in pool["extra"] if not missing_skills or s not in missing_skills]
    n_extra = random.randint(3, min(8, len(extra_pool)))
    skills = core + random.sample(extra_pool, n_extra)
    if forced_skills:
        for s in forced_skills:
            if s not in skills:
                skills.append(s)
    # light cross-track sprinkle for realism
    if random.random() < 0.35:
        other_track = random.choice([t for t in TRACKS if t != track])
        skills.append(random.choice(TRACKS[other_track]["core"]))
    random.shuffle(skills)

    domain = domain or random.choice(DOMAINS)
    n_prev = 1 if years < 3 else random.choice([1, 2, 2, 3])
    certs = random.sample(CERTS_POOL, k=random.choice([0, 0, 1, 1, 2]))

    return {
        "candidate_id": cid,
        "name": name,
        "track": track,
        "current_title": title,
        "years_experience": years,
        "seniority": seniority_for(years),
        "location": f"{fake.city()}, {fake.state_abbr()}",
        "skills": sorted(set(skills)),
        "education": {"degree": random.choice(DEGREES), "school": f"{fake.city()} {random.choice(SCHOOLS)}"},
        "certifications": certs,
        "domain_experience": _dedupe_domains(domain, n_prev),
        "num_previous_companies": n_prev,
        "notice_period_weeks": random.choice([0, 2, 4, 4, 8, 12]),
    }


def render_resume_text(c: dict) -> str:
    lines = []
    lines.append(c["name"])
    lines.append(f"{c['current_title']}  |  {c['location']}  |  {c['years_experience']} years experience")
    lines.append(f"email: {c['name'].lower().replace(' ', '.')}@example.com")
    lines.append("")
    lines.append("SUMMARY")
    domains = " and ".join(c["domain_experience"])
    lines.append(
        f"{c['seniority']} {c['track']} engineer with {c['years_experience']} years of experience "
        f"building production software, primarily in {domains}. "
        f"Comfortable owning features end-to-end and collaborating closely with product and design."
    )
    lines.append("")
    lines.append("SKILLS")
    lines.append(", ".join(c["skills"]))
    lines.append("")
    lines.append("EXPERIENCE")
    yrs_left = c["years_experience"]
    n = c["num_previous_companies"]
    for i in range(n):
        span = max(1, yrs_left // (n - i)) if (n - i) else yrs_left
        yrs_left -= span
        role_title = c["current_title"] if i == 0 else random.choice(TRACKS[c["track"]]["titles"])
        lines.append(f"- {role_title}, {fake.company()} ({span} yr{'s' if span != 1 else ''})")
        bullet_skills = random.sample(c["skills"], k=min(3, len(c["skills"])))
        lines.append(
            f"    Built and maintained systems using {', '.join(bullet_skills)}; "
            f"partnered cross-functionally to ship features in {random.choice(c['domain_experience'])}."
        )
    lines.append("")
    lines.append("EDUCATION")
    lines.append(f"{c['education']['degree']}, {c['education']['school']}")
    if c["certifications"]:
        lines.append("")
        lines.append("CERTIFICATIONS")
        lines.append(", ".join(c["certifications"]))
    return "\n".join(lines)


def main():
    candidates: list[dict] = []
    counter = 1

    def next_id():
        nonlocal counter
        cid = f"CAND-{counter:03d}"
        counter += 1
        return cid

    # ---- Hand-placed "signature" candidates used in demo scripts/tests ----
    # John: strong senior React match for the primary demo JD - covers every
    # must-have (React, TypeScript, a state-mgmt library, HTML5/CSS3, a test
    # framework) plus several nice-to-haves (Next.js, GraphQL, fintech domain,
    # accessibility).
    john = make_candidate(
        next_id(), "frontend", years=5, name="John Whitfield",
        forced_skills=["React", "TypeScript", "Redux", "Jest", "Next.js", "GraphQL",
                       "Web Accessibility (WCAG 2.1)"],
        domain="Fintech / BFSI",
    )
    candidates.append(john)

    # Jane: also frontend/React with Redux and Jest, but junior on years and
    # missing TypeScript - gives a clean, explainable reason she ranks below
    # John on a JD that requires TypeScript + 3+ years.
    jane = make_candidate(
        next_id(), "frontend", years=2, name="Jane Okafor",
        forced_skills=["React", "Redux", "Jest"], missing_skills=["TypeScript"],
        domain="E-commerce",
    )
    candidates.append(jane)

    # A close #3 for "compare top 3" scenarios: strong but no fintech domain,
    # slightly less senior than John.
    priya = make_candidate(
        next_id(), "frontend", years=4, name="Priya Nataraj",
        forced_skills=["React", "TypeScript", "Redux", "Jest"],
        domain="SaaS / B2B",
    )
    candidates.append(priya)

    # A borderline candidate: covers the must-haves but misses several
    # nice-to-haves - good for the "improvement suggestions for borderline
    # candidates" feature.
    marcus = make_candidate(
        next_id(), "frontend", years=3, name="Marcus Webb",
        forced_skills=["React", "TypeScript", "Redux", "Jest"],
        missing_skills=["Next.js", "GraphQL", "Web Accessibility (WCAG 2.1)"],
        domain="Logistics",
    )
    candidates.append(marcus)

    # A clearly unqualified candidate for contrast (wrong track, junior).
    devops_junior = make_candidate(next_id(), "devops", years=1, name="Alex Torres")
    candidates.append(devops_junior)

    # ---- Bulk procedurally-generated candidates ----
    # Weighted toward frontend/fullstack since the primary demo JD is React,
    # but with a healthy spread across all tracks for realistic RAG recall.
    track_weights = {"frontend": 28, "fullstack": 20, "backend": 22, "data": 12,
                      "devops": 10, "mobile": 5, "qa": 3}
    remaining = 100 - len(candidates)
    track_list = []
    for t, w in track_weights.items():
        track_list += [t] * w
    random.shuffle(track_list)

    for i in range(remaining):
        track = track_list[i % len(track_list)]
        years = max(0, int(random.gauss(5, 3.2)))
        years = min(years, 17)
        candidates.append(make_candidate(next_id(), track, years))

    # ---- Write files ----
    metadata = {}
    for c in candidates:
        text = render_resume_text(c)
        (RESUME_DIR / f"{c['candidate_id']}.txt").write_text(text, encoding="utf-8")
        metadata[c["candidate_id"]] = c

    (RESUME_DIR / "_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Generated {len(candidates)} resumes -> {RESUME_DIR}")
    track_counts = {}
    for c in candidates:
        track_counts[c["track"]] = track_counts.get(c["track"], 0) + 1
    print("Track distribution:", track_counts)


if __name__ == "__main__":
    main()
