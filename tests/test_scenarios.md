# Test Scenarios

Six real, captured conversation flows exercising every required capability - initial screening, comparison, explainability, iterative refinement, interview questions, and hire/no-hire recommendations. These are not hand-written examples: they were captured by running the actual agent (`mock` mode, no API key) through `tests/scenario_runner.py`, which drives the compiled graph exactly the way the CLI does. Re-run `python tests/scenario_runner.py --help` to regenerate any of them yourself, or add `--mode live` once you've set `GROQ_API_KEY` to see the same flows with full LLM reasoning instead of the rule-based fallback.

> **A note on mode:** every transcript below ran in mock mode, so the reasoning you'll see (skill matching, comparisons, questions, hire calls) is the rule-based engine described in [ARCHITECTURE.md](../docs/ARCHITECTURE.md), not an LLM. That's deliberate - it's what makes these transcripts exactly reproducible and reviewable without an API key. Live mode produces the same conversational shape with materially better reasoning quality.

## Scenario 1: Full walkthrough — screen, compare, explain, refine, interview, hire

**Job description:** Senior Frontend Engineer (React)  
**Demonstrates:** The most complete flow: initial screen, a 3-way comparison, an explainability question about two *specific* candidates, a live requirement refinement with re-ranking, interview-question generation, and a round-3 hire call.

<details>
<summary>Full transcript</summary>


**Agent:**

Got the job description (250 words). Parsing requirements...


**Agent:**

**Senior Frontend Engineer** — Staff/Lead, 3+ yrs

**Must-have:** React, TypeScript, Redux, HTML5, CSS3, Jest
**Nice-to-have:** Next.js, GraphQL, WCAG


**Agent:**

Searched all 100 resumes in the pool. Scoring and ranking now...


**Agent:**

**Round 1 shortlist — top 10 of 100:**
1. John Whitfield (CAND-001) — 88.5/100
2. Priya Nataraj (CAND-003) — 80.5/100
3. Olivia Harris (CAND-083) — 74.2/100
4. Nicole Hamilton (CAND-093) — 73.4/100
5. Anthony Rodriguez (CAND-012) — 72.2/100
6. Marcus Webb (CAND-004) — 66.6/100
7. George Hobbs (CAND-056) — 66.4/100
8. Matthew Fernandez (CAND-023) — 65.8/100
9. Paul Larsen (CAND-050) — 65.5/100
10. Daniel Floyd (CAND-044) — 65.5/100


**Agent:**

# Candidate Match Report — Senior Frontend Engineer

**Seniority:** Staff/Lead  
**Minimum experience:** 3+ years  
**Must-have:** React, TypeScript, Redux, HTML5, CSS3, Jest  
**Nice-to-have:** Next.js, GraphQL, WCAG  

## Round 1 — Initial screen: top 10 of 100 resumes

| Rank | Candidate | Score /100 | Must-have coverage | Why |
|---|---|---|---|---|
| 1 | John Whitfield (CAND-001) | 88.5 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 3 nice-to-have(s): Next.js, GraphQL, WCAG; 5 yrs experience meets the 3+ yr bar |
| 2 | Priya Nataraj (CAND-003) | 80.5 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 2 nice-to-have(s): Next.js, GraphQL; 4 yrs experience meets the 3+ yr bar |
| 3 | Olivia Harris (CAND-083) | 74.2 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 1 nice-to-have(s): Next.js; 6 yrs experience meets the 3+ yr bar |
| 4 | Nicole Hamilton (CAND-093) | 73.4 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 1 nice-to-have(s): Next.js; 9 yrs experience meets the 3+ yr bar |
| 5 | Anthony Rodriguez (CAND-012) | 72.2 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 2 nice-to-have(s): Next.js, WCAG; 6 yrs experience meets the 3+ yr bar |
| 6 | Marcus Webb (CAND-004) | 66.6 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); 3 yrs experience meets the 3+ yr bar |
| 7 | George Hobbs (CAND-056) | 66.4 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 2 nice-to-have(s): Next.js, WCAG; 2 yrs experience is below the 3+ yr bar |
| 8 | Matthew Fernandez (CAND-023) | 65.8 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 1 nice-to-have(s): GraphQL; 4 yrs experience meets the 3+ yr bar |
| 9 | Paul Larsen (CAND-050) | 65.5 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 1 nice-to-have(s): WCAG; 5 yrs experience meets the 3+ yr bar |
| 10 | Daniel Floyd (CAND-044) | 65.5 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, HTML5, CSS3); missing Redux; also brings 1 nice-to-have(s): Next.js; 8 yrs experience meets the 3+ yr bar |

## Round 2 — Deep analysis of the shortlist

### John Whitfield (CAND-001) — Strong match

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js
- GraphQL
- WCAG

**Gaps**
- None identified against current requirements.

### Priya Nataraj (CAND-003) — Strong match

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js
- GraphQL

**Gaps**
- None identified against current requirements.

### Olivia Harris (CAND-083) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- None identified against current requirements.

### Nicole Hamilton (CAND-093) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- None identified against current requirements.

### Anthony Rodriguez (CAND-012) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Marcus Webb (CAND-004) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest

**Gaps**
- None identified against current requirements.

### George Hobbs (CAND-056) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Matthew Fernandez (CAND-023) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- GraphQL

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Paul Larsen (CAND-050) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- WCAG

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Daniel Floyd (CAND-044) — Borderline

**Strengths**
- React
- TypeScript
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- Redux

**Improvement suggestions** _(borderline candidate)_
- Hands-on Redux experience would meaningfully strengthen this application.

---
_Ask for a head-to-head comparison, interview questions, or a hire/no-hire recommendation for any candidate above - or refine the requirements and I'll re-rank._

_(saved to `/home/claude/resume-matching-agent/data/reports/Senior_Frontend_Engineer-20260813-225952.md`)_


**You:**

Compare the top 3 matches side by side


**Agent:**

**Comparison**

- **John Whitfield (CAND-001)** — matches 6 must-have(s), 3 nice-to-have(s); strengths: Meta Front-End Developer Professional Certificate, 5 yrs in Fintech / BFSI
- **Priya Nataraj (CAND-003)** — matches 6 must-have(s), 2 nice-to-have(s); strengths: Google Cloud Professional Developer, 4 yrs in SaaS / B2B
- **Olivia Harris (CAND-083)** — matches 6 must-have(s), 1 nice-to-have(s); strengths: 6 yrs in Travel tech

John Whitfield leads this comparison, covering 6/6 must-have requirement(s) versus Priya Nataraj's 6/6. John Whitfield also has more relevant nice-to-have coverage.


**You:**

Why did John rank higher than Jane?


**Agent:**

**Comparison**

- **John Whitfield (CAND-001)** — matches 6 must-have(s), 3 nice-to-have(s); strengths: Meta Front-End Developer Professional Certificate, 5 yrs in Fintech / BFSI
- **Jane Okafor (CAND-002)** — matches 5 must-have(s), 1 nice-to-have(s); strengths: Certified Kubernetes Administrator (CKA), 2 yrs in E-commerce

John Whitfield leads this comparison, covering 6/6 must-have requirement(s) versus Jane Okafor's 5/6. The gap comes down to TypeScript.


**You:**

We also need AWS experience


**Agent:**

Got it — updating the requirements and re-ranking against all 100 resumes...


**Agent:**

**Round 1 shortlist — top 10 of 100:**
1. John Whitfield (CAND-001) — 81.4/100
2. Priya Nataraj (CAND-003) — 73.3/100
3. Olivia Harris (CAND-083) — 67.1/100
4. Matthew Fernandez (CAND-023) — 67.0/100
5. Marcus Webb (CAND-004) — 66.6/100
6. Anthony Rodriguez (CAND-012) — 66.2/100
7. Nicole Hamilton (CAND-093) — 66.2/100
8. April Booth (CAND-082) — 66.1/100
9. William Warren (CAND-069) — 65.9/100
10. George Hobbs (CAND-056) — 60.5/100


**Agent:**

## What changed since the last ranking

- Newly in the top 10: April Booth, William Warren
- Dropped out of the top 10: Paul Larsen, Daniel Floyd
- Matthew Fernandez moved up: #8 → #4
- Marcus Webb moved up: #6 → #5
- Anthony Rodriguez moved down: #5 → #6
- Nicole Hamilton moved down: #4 → #7
- George Hobbs moved down: #7 → #10

# Candidate Match Report — Senior Frontend Engineer

**Seniority:** Staff/Lead  
**Minimum experience:** 3+ years  
**Must-have:** React, TypeScript, Redux, HTML5, CSS3, Jest, AWS  
**Nice-to-have:** Next.js, GraphQL, WCAG  

## Round 1 — Initial screen: top 10 of 100 resumes

| Rank | Candidate | Score /100 | Must-have coverage | Why |
|---|---|---|---|---|
| 1 | John Whitfield (CAND-001) | 81.4 | 6/7 | matches 6/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing AWS; also brings 3 nice-to-have(s): Next.js, GraphQL, WCAG; 5 yrs experience meets the 3+ yr bar |
| 2 | Priya Nataraj (CAND-003) | 73.3 | 6/7 | matches 6/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing AWS; also brings 2 nice-to-have(s): Next.js, GraphQL; 4 yrs experience meets the 3+ yr bar |
| 3 | Olivia Harris (CAND-083) | 67.1 | 6/7 | matches 6/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing AWS; also brings 1 nice-to-have(s): Next.js; 6 yrs experience meets the 3+ yr bar |
| 4 | Matthew Fernandez (CAND-023) | 67.0 | 6/7 | matches 6/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 1 nice-to-have(s): GraphQL; 4 yrs experience meets the 3+ yr bar |
| 5 | Marcus Webb (CAND-004) | 66.6 | 7/7 | matches 7/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); 3 yrs experience meets the 3+ yr bar |
| 6 | Anthony Rodriguez (CAND-012) | 66.2 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest, AWS; also brings 2 nice-to-have(s): Next.js, WCAG; 6 yrs experience meets the 3+ yr bar |
| 7 | Nicole Hamilton (CAND-093) | 66.2 | 6/7 | matches 6/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing AWS; also brings 1 nice-to-have(s): Next.js; 9 yrs experience meets the 3+ yr bar |
| 8 | April Booth (CAND-082) | 66.1 | 6/7 | matches 6/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 1 nice-to-have(s): Next.js; 4 yrs experience meets the 3+ yr bar |
| 9 | William Warren (CAND-069) | 65.9 | 6/7 | matches 6/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 1 nice-to-have(s): WCAG; 9 yrs experience meets the 3+ yr bar |
| 10 | George Hobbs (CAND-056) | 60.5 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest, AWS; also brings 2 nice-to-have(s): Next.js, WCAG; 2 yrs experience is below the 3+ yr bar |

## Round 2 — Deep analysis of the shortlist

### John Whitfield (CAND-001) — Strong match

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js
- GraphQL
- WCAG

**Gaps**
- AWS

### Priya Nataraj (CAND-003) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js
- GraphQL

**Gaps**
- AWS

**Improvement suggestions** _(borderline candidate)_
- Hands-on AWS experience would meaningfully strengthen this application.

### Olivia Harris (CAND-083) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- AWS

**Improvement suggestions** _(borderline candidate)_
- Hands-on AWS experience would meaningfully strengthen this application.

### Matthew Fernandez (CAND-023) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- AWS
- GraphQL

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Marcus Webb (CAND-004) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- AWS

**Gaps**
- None identified against current requirements.

### Anthony Rodriguez (CAND-012) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest
- AWS

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.
- Hands-on AWS experience would meaningfully strengthen this application.

### Nicole Hamilton (CAND-093) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- AWS

**Improvement suggestions** _(borderline candidate)_
- Hands-on AWS experience would meaningfully strengthen this application.

### April Booth (CAND-082) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- AWS
- Next.js

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### William Warren (CAND-069) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- AWS
- WCAG

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### George Hobbs (CAND-056) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest
- AWS

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.
- Hands-on AWS experience would meaningfully strengthen this application.

---
_Ask for a head-to-head comparison, interview questions, or a hire/no-hire recommendation for any candidate above - or refine the requirements and I'll re-rank._

_(saved to `/home/claude/resume-matching-agent/data/reports/Senior_Frontend_Engineer-20260813-225952.md`)_


**You:**

Give me interview questions for John


**Agent:**

**Screening questions for John Whitfield (CAND-001)**

1. Walk me through a production project where you used Jest - what was your specific role, and what would you do differently now?
2. You've worked across 2 company(ies) in 5 years - what's driven those moves?
3. This role expects AWS, which isn't explicit on your resume - how would you ramp up on that, and have you touched anything adjacent to it?
4. You've worked in Fintech / BFSI - what's one domain-specific constraint from that industry that shaped how you built software?
5. Tell me about a time you disagreed with a technical decision on your team. What did you do?


**You:**

Give me a hire recommendation for John


**Agent:**

**Round 3 recommendation — John Whitfield (CAND-001)**

**Decision: Hire with reservations**

Score of 81/100 - solid overall fit, but AWS should be probed in the next round.


**You:**

That's all, thanks


**Agent:**

Sounds good — wrapping up here. The full report is saved to disk if you want to revisit it (`/home/claude/resume-matching-agent/data/reports/Senior_Frontend_Engineer-20260813-225952.md`). Good luck with the search!


</details>

## Scenario 2: Default-candidate shorthand + explicit quit

**Job description:** Backend Engineer (Node.js)  
**Demonstrates:** Shows the shorthand path: asking for interview questions or a comparison without naming anyone defaults to the current top candidate(s). Ends via the word "quit" instead of a natural-language goodbye.

<details>
<summary>Full transcript</summary>


**Agent:**

Got the job description (133 words). Parsing requirements...


**Agent:**

**Backend Engineer** — Mid-level, 3+ yrs

**Must-have:** Node.js, REST API, SQL, PostgreSQL, Git
**Nice-to-have:** Microservices, Kafka, Docker, Kubernetes, JWT, OAuth2


**Agent:**

Searched all 100 resumes in the pool. Scoring and ranking now...


**Agent:**

**Round 1 shortlist — top 10 of 100:**
1. Jeffrey Wood (CAND-061) — 76.6/100
2. Laura Barnett (CAND-064) — 74.4/100
3. Julie Roberts (CAND-096) — 72.9/100
4. Evelyn Galvan (CAND-037) — 72.5/100
5. Tracey Higgins (CAND-059) — 70.0/100
6. Carmen Rose (CAND-017) — 67.8/100
7. Taylor Harris (CAND-028) — 65.2/100
8. Trevor Walker (CAND-057) — 65.2/100
9. Alicia Hubbard (CAND-079) — 64.1/100
10. Katherine Miller (CAND-078) — 62.4/100


**Agent:**

# Candidate Match Report — Backend Engineer

**Seniority:** Mid-level  
**Minimum experience:** 3+ years  
**Must-have:** Node.js, REST API, SQL, PostgreSQL, Git  
**Nice-to-have:** Microservices, Kafka, Docker, Kubernetes, JWT, OAuth2  

## Round 1 — Initial screen: top 10 of 100 resumes

| Rank | Candidate | Score /100 | Must-have coverage | Why |
|---|---|---|---|---|
| 1 | Jeffrey Wood (CAND-061) | 76.6 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 5 nice-to-have(s): Kafka, Docker, Kubernetes; 3 yrs experience meets the 3+ yr bar |
| 2 | Laura Barnett (CAND-064) | 74.4 | 5/5 | matches 5/5 must-have requirement(s) (Node.js, REST API, SQL, PostgreSQL); also brings 2 nice-to-have(s): Microservices, Kubernetes; 3 yrs experience meets the 3+ yr bar |
| 3 | Julie Roberts (CAND-096) | 72.9 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 4 nice-to-have(s): Kafka, Kubernetes, JWT; 5 yrs experience meets the 3+ yr bar |
| 4 | Evelyn Galvan (CAND-037) | 72.5 | 5/5 | matches 5/5 must-have requirement(s) (Node.js, REST API, SQL, PostgreSQL); also brings 3 nice-to-have(s): Microservices, Docker, Kubernetes; 2 yrs experience is below the 3+ yr bar |
| 5 | Tracey Higgins (CAND-059) | 70.0 | 5/5 | matches 5/5 must-have requirement(s) (Node.js, REST API, SQL, PostgreSQL); also brings 2 nice-to-have(s): JWT, OAuth2; 2 yrs experience is below the 3+ yr bar |
| 6 | Carmen Rose (CAND-017) | 67.8 | 5/5 | matches 5/5 must-have requirement(s) (Node.js, REST API, SQL, PostgreSQL); 8 yrs experience meets the 3+ yr bar |
| 7 | Taylor Harris (CAND-028) | 65.2 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 2 nice-to-have(s): Kafka, Docker; 4 yrs experience meets the 3+ yr bar |
| 8 | Trevor Walker (CAND-057) | 65.2 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 2 nice-to-have(s): JWT, OAuth2; 5 yrs experience meets the 3+ yr bar |
| 9 | Alicia Hubbard (CAND-079) | 64.1 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 2 nice-to-have(s): Microservices, Kafka; 8 yrs experience meets the 3+ yr bar |
| 10 | Katherine Miller (CAND-078) | 62.4 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 3 nice-to-have(s): Microservices, Kafka, Kubernetes; 2 yrs experience is below the 3+ yr bar |

## Round 2 — Deep analysis of the shortlist

### Jeffrey Wood (CAND-061) — Strong match

**Strengths**
- Node.js
- REST API
- SQL
- Git
- Kafka
- Docker
- Kubernetes
- JWT
- OAuth2

**Gaps**
- PostgreSQL

### Laura Barnett (CAND-064) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- PostgreSQL
- Git
- Microservices
- Kubernetes

**Gaps**
- None identified against current requirements.

### Julie Roberts (CAND-096) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- Git
- Kafka
- Kubernetes
- JWT
- OAuth2

**Gaps**
- PostgreSQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on PostgreSQL experience would meaningfully strengthen this application.

### Evelyn Galvan (CAND-037) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- PostgreSQL
- Git
- Microservices
- Docker
- Kubernetes

**Gaps**
- None identified against current requirements.

**Improvement suggestions** _(borderline candidate)_
- Currently under the 3+ year bar - worth probing depth in the interview.

### Tracey Higgins (CAND-059) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- PostgreSQL
- Git
- JWT
- OAuth2

**Gaps**
- None identified against current requirements.

**Improvement suggestions** _(borderline candidate)_
- Currently under the 3+ year bar - worth probing depth in the interview.

### Carmen Rose (CAND-017) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- PostgreSQL
- Git

**Gaps**
- None identified against current requirements.

### Taylor Harris (CAND-028) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- Git
- Kafka
- Docker

**Gaps**
- PostgreSQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on PostgreSQL experience would meaningfully strengthen this application.

### Trevor Walker (CAND-057) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- Git
- JWT
- OAuth2

**Gaps**
- PostgreSQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on PostgreSQL experience would meaningfully strengthen this application.

### Alicia Hubbard (CAND-079) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- Git
- Microservices
- Kafka

**Gaps**
- PostgreSQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on PostgreSQL experience would meaningfully strengthen this application.

### Katherine Miller (CAND-078) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- Git
- Microservices
- Kafka
- Kubernetes

**Gaps**
- PostgreSQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on PostgreSQL experience would meaningfully strengthen this application.

---
_Ask for a head-to-head comparison, interview questions, or a hire/no-hire recommendation for any candidate above - or refine the requirements and I'll re-rank._

_(saved to `/home/claude/resume-matching-agent/data/reports/Backend_Engineer-20260813-225952.md`)_


**You:**

Give me interview questions for the top candidate


**Agent:**

**Screening questions for Jeffrey Wood (CAND-061)**

1. Walk me through a production project where you used Kubernetes - what was your specific role, and what would you do differently now?
2. You've worked across 1 company(ies) in 3 years - what's driven those moves?
3. This role expects PostgreSQL, which isn't explicit on your resume - how would you ramp up on that, and have you touched anything adjacent to it?
4. This role expects Microservices, which isn't explicit on your resume - how would you ramp up on that, and have you touched anything adjacent to it?
5. You've worked in SaaS / B2B - what's one domain-specific constraint from that industry that shaped how you built software?
6. Tell me about a time you disagreed with a technical decision on your team. What did you do?


**You:**

Now compare the top 3 side by side


**Agent:**

**Comparison**

- **Jeffrey Wood (CAND-061)** — matches 4 must-have(s), 5 nice-to-have(s); strengths: 3 yrs in SaaS / B2B
- **Laura Barnett (CAND-064)** — matches 5 must-have(s), 2 nice-to-have(s); strengths: Certified Kubernetes Administrator (CKA), 3 yrs in Fintech / BFSI
- **Julie Roberts (CAND-096)** — matches 4 must-have(s), 4 nice-to-have(s); strengths: Meta Front-End Developer Professional Certificate, 5 yrs in EdTech

Laura Barnett leads this comparison, covering 5/5 must-have requirement(s) versus Jeffrey Wood's 4/5. The gap comes down to PostgreSQL.


**You:**

quit


**Agent:**

Sounds good — wrapping up here. The full report is saved to disk if you want to revisit it (`/home/claude/resume-matching-agent/data/reports/Backend_Engineer-20260813-225952.md`). Good luck with the search!


</details>

## Scenario 3: Deep analysis and a Round-3 hire call

**Job description:** Fullstack Engineer  
**Demonstrates:** Round 2's deep-dive (strengths/gaps/verdict) and Round 3's hire/no-hire recommendation, both invoked directly on the top candidate.

<details>
<summary>Full transcript</summary>


**Agent:**

Got the job description (126 words). Parsing requirements...


**Agent:**

**Fullstack Engineer** — Mid-level, 2+ yrs

**Must-have:** React, TypeScript, SQL
**Nice-to-have:** Next.js, CI/CD, Startup or fast-moving product-team experience


**Agent:**

Searched all 100 resumes in the pool. Scoring and ranking now...


**Agent:**

**Round 1 shortlist — top 10 of 100:**
1. Miranda Khan (CAND-020) — 81.3/100
2. Kimberly Dudley (CAND-006) — 80.9/100
3. Eugene Higgins (CAND-092) — 75.2/100
4. Benjamin Soto (CAND-072) — 74.5/100
5. Crystal Pham (CAND-099) — 74.5/100
6. Donna Landry (CAND-081) — 74.4/100
7. Sandra Zimmerman (CAND-062) — 74.3/100
8. Katelyn Lee (CAND-025) — 74.1/100
9. David Baker (CAND-076) — 74.0/100
10. Marc Hart (CAND-029) — 73.9/100


**Agent:**

# Candidate Match Report — Fullstack Engineer

**Seniority:** Mid-level  
**Minimum experience:** 2+ years  
**Must-have:** React, TypeScript, SQL  
**Nice-to-have:** Next.js, CI/CD, Startup or fast-moving product-team experience  

## Round 1 — Initial screen: top 10 of 100 resumes

| Rank | Candidate | Score /100 | Must-have coverage | Why |
|---|---|---|---|---|
| 1 | Miranda Khan (CAND-020) | 81.3 | 3/3 | matches 3/3 must-have requirement(s) (React, TypeScript, SQL); also brings 2 nice-to-have(s): Next.js, CI/CD; 10 yrs experience meets the 2+ yr bar |
| 2 | Kimberly Dudley (CAND-006) | 80.9 | 3/3 | matches 3/3 must-have requirement(s) (React, TypeScript, SQL); also brings 2 nice-to-have(s): Next.js, CI/CD; 5 yrs experience meets the 2+ yr bar |
| 3 | Eugene Higgins (CAND-092) | 75.2 | 3/3 | matches 3/3 must-have requirement(s) (React, TypeScript, SQL); also brings 1 nice-to-have(s): CI/CD; 3 yrs experience meets the 2+ yr bar |
| 4 | Benjamin Soto (CAND-072) | 74.5 | 3/3 | matches 3/3 must-have requirement(s) (React, TypeScript, SQL); also brings 1 nice-to-have(s): CI/CD; 6 yrs experience meets the 2+ yr bar |
| 5 | Crystal Pham (CAND-099) | 74.5 | 3/3 | matches 3/3 must-have requirement(s) (React, TypeScript, SQL); also brings 1 nice-to-have(s): CI/CD; 2 yrs experience meets the 2+ yr bar |
| 6 | Donna Landry (CAND-081) | 74.4 | 3/3 | matches 3/3 must-have requirement(s) (React, TypeScript, SQL); also brings 1 nice-to-have(s): CI/CD; 9 yrs experience meets the 2+ yr bar |
| 7 | Sandra Zimmerman (CAND-062) | 74.3 | 3/3 | matches 3/3 must-have requirement(s) (React, TypeScript, SQL); also brings 1 nice-to-have(s): Next.js; 7 yrs experience meets the 2+ yr bar |
| 8 | Katelyn Lee (CAND-025) | 74.1 | 3/3 | matches 3/3 must-have requirement(s) (React, TypeScript, SQL); also brings 1 nice-to-have(s): Next.js; 10 yrs experience meets the 2+ yr bar |
| 9 | David Baker (CAND-076) | 74.0 | 3/3 | matches 3/3 must-have requirement(s) (React, TypeScript, SQL); also brings 1 nice-to-have(s): Next.js; 4 yrs experience meets the 2+ yr bar |
| 10 | Marc Hart (CAND-029) | 73.9 | 3/3 | matches 3/3 must-have requirement(s) (React, TypeScript, SQL); also brings 1 nice-to-have(s): CI/CD; 11 yrs experience meets the 2+ yr bar |

## Round 2 — Deep analysis of the shortlist

### Miranda Khan (CAND-020) — Strong match

**Strengths**
- React
- TypeScript
- SQL
- Next.js
- CI/CD

**Gaps**
- None identified against current requirements.

### Kimberly Dudley (CAND-006) — Strong match

**Strengths**
- React
- TypeScript
- SQL
- Next.js
- CI/CD

**Gaps**
- None identified against current requirements.

### Eugene Higgins (CAND-092) — Strong match

**Strengths**
- React
- TypeScript
- SQL
- CI/CD

**Gaps**
- None identified against current requirements.

### Benjamin Soto (CAND-072) — Borderline

**Strengths**
- React
- TypeScript
- SQL
- CI/CD

**Gaps**
- None identified against current requirements.

### Crystal Pham (CAND-099) — Borderline

**Strengths**
- React
- TypeScript
- SQL
- CI/CD

**Gaps**
- None identified against current requirements.

### Donna Landry (CAND-081) — Borderline

**Strengths**
- React
- TypeScript
- SQL
- CI/CD

**Gaps**
- None identified against current requirements.

### Sandra Zimmerman (CAND-062) — Borderline

**Strengths**
- React
- TypeScript
- SQL
- Next.js

**Gaps**
- None identified against current requirements.

### Katelyn Lee (CAND-025) — Borderline

**Strengths**
- React
- TypeScript
- SQL
- Next.js

**Gaps**
- None identified against current requirements.

### David Baker (CAND-076) — Borderline

**Strengths**
- React
- TypeScript
- SQL
- Next.js

**Gaps**
- None identified against current requirements.

### Marc Hart (CAND-029) — Borderline

**Strengths**
- React
- TypeScript
- SQL
- CI/CD

**Gaps**
- None identified against current requirements.

---
_Ask for a head-to-head comparison, interview questions, or a hire/no-hire recommendation for any candidate above - or refine the requirements and I'll re-rank._

_(saved to `/home/claude/resume-matching-agent/data/reports/Fullstack_Engineer-20260813-225952.md`)_


**You:**

Give me a deep analysis of the top candidate's strengths and gaps


**Agent:**

**Miranda Khan (CAND-020) — Strong match**

Strengths: React, TypeScript, SQL, Next.js, CI/CD

Gaps: none


**You:**

Give me a hire recommendation for the top candidate


**Agent:**

**Round 3 recommendation — Miranda Khan (CAND-020)**

**Decision: Hire**

Score of 81/100 with no missing must-have requirements - a strong, low-risk match.


**You:**

That's all


**Agent:**

Sounds good — wrapping up here. The full report is saved to disk if you want to revisit it (`/home/claude/resume-matching-agent/data/reports/Fullstack_Engineer-20260813-225952.md`). Good luck with the search!


</details>

## Scenario 4: Multiple sequential requirement refinements

**Job description:** Senior Frontend Engineer (React)  
**Demonstrates:** Two refinements back-to-back — adding a must-have skill, then raising the minimum years — each triggering a real re-rank with a "what changed" diff, showing the shortlist compound-adjusting across turns.

<details>
<summary>Full transcript</summary>


**Agent:**

Got the job description (250 words). Parsing requirements...


**Agent:**

**Senior Frontend Engineer** — Staff/Lead, 3+ yrs

**Must-have:** React, TypeScript, Redux, HTML5, CSS3, Jest
**Nice-to-have:** Next.js, GraphQL, WCAG


**Agent:**

Searched all 100 resumes in the pool. Scoring and ranking now...


**Agent:**

**Round 1 shortlist — top 10 of 100:**
1. John Whitfield (CAND-001) — 88.5/100
2. Priya Nataraj (CAND-003) — 80.5/100
3. Olivia Harris (CAND-083) — 74.2/100
4. Nicole Hamilton (CAND-093) — 73.4/100
5. Anthony Rodriguez (CAND-012) — 72.2/100
6. Marcus Webb (CAND-004) — 66.6/100
7. George Hobbs (CAND-056) — 66.4/100
8. Matthew Fernandez (CAND-023) — 65.8/100
9. Paul Larsen (CAND-050) — 65.5/100
10. Daniel Floyd (CAND-044) — 65.5/100


**Agent:**

# Candidate Match Report — Senior Frontend Engineer

**Seniority:** Staff/Lead  
**Minimum experience:** 3+ years  
**Must-have:** React, TypeScript, Redux, HTML5, CSS3, Jest  
**Nice-to-have:** Next.js, GraphQL, WCAG  

## Round 1 — Initial screen: top 10 of 100 resumes

| Rank | Candidate | Score /100 | Must-have coverage | Why |
|---|---|---|---|---|
| 1 | John Whitfield (CAND-001) | 88.5 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 3 nice-to-have(s): Next.js, GraphQL, WCAG; 5 yrs experience meets the 3+ yr bar |
| 2 | Priya Nataraj (CAND-003) | 80.5 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 2 nice-to-have(s): Next.js, GraphQL; 4 yrs experience meets the 3+ yr bar |
| 3 | Olivia Harris (CAND-083) | 74.2 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 1 nice-to-have(s): Next.js; 6 yrs experience meets the 3+ yr bar |
| 4 | Nicole Hamilton (CAND-093) | 73.4 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 1 nice-to-have(s): Next.js; 9 yrs experience meets the 3+ yr bar |
| 5 | Anthony Rodriguez (CAND-012) | 72.2 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 2 nice-to-have(s): Next.js, WCAG; 6 yrs experience meets the 3+ yr bar |
| 6 | Marcus Webb (CAND-004) | 66.6 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); 3 yrs experience meets the 3+ yr bar |
| 7 | George Hobbs (CAND-056) | 66.4 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 2 nice-to-have(s): Next.js, WCAG; 2 yrs experience is below the 3+ yr bar |
| 8 | Matthew Fernandez (CAND-023) | 65.8 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 1 nice-to-have(s): GraphQL; 4 yrs experience meets the 3+ yr bar |
| 9 | Paul Larsen (CAND-050) | 65.5 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 1 nice-to-have(s): WCAG; 5 yrs experience meets the 3+ yr bar |
| 10 | Daniel Floyd (CAND-044) | 65.5 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, HTML5, CSS3); missing Redux; also brings 1 nice-to-have(s): Next.js; 8 yrs experience meets the 3+ yr bar |

## Round 2 — Deep analysis of the shortlist

### John Whitfield (CAND-001) — Strong match

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js
- GraphQL
- WCAG

**Gaps**
- None identified against current requirements.

### Priya Nataraj (CAND-003) — Strong match

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js
- GraphQL

**Gaps**
- None identified against current requirements.

### Olivia Harris (CAND-083) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- None identified against current requirements.

### Nicole Hamilton (CAND-093) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- None identified against current requirements.

### Anthony Rodriguez (CAND-012) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Marcus Webb (CAND-004) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest

**Gaps**
- None identified against current requirements.

### George Hobbs (CAND-056) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Matthew Fernandez (CAND-023) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- GraphQL

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Paul Larsen (CAND-050) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- WCAG

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Daniel Floyd (CAND-044) — Borderline

**Strengths**
- React
- TypeScript
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- Redux

**Improvement suggestions** _(borderline candidate)_
- Hands-on Redux experience would meaningfully strengthen this application.

---
_Ask for a head-to-head comparison, interview questions, or a hire/no-hire recommendation for any candidate above - or refine the requirements and I'll re-rank._

_(saved to `/home/claude/resume-matching-agent/data/reports/Senior_Frontend_Engineer-20260813-225952.md`)_


**You:**

We also need GraphQL experience


**Agent:**

Got it — updating the requirements and re-ranking against all 100 resumes...


**Agent:**

**Round 1 shortlist — top 10 of 100:**
1. John Whitfield (CAND-001) — 88.5/100
2. Priya Nataraj (CAND-003) — 77.1/100
3. Anthony Rodriguez (CAND-012) — 72.9/100
4. Olivia Harris (CAND-083) — 70.4/100
5. Nicole Hamilton (CAND-093) — 69.6/100
6. George Hobbs (CAND-056) — 67.1/100
7. Paul Larsen (CAND-050) — 62.9/100
8. Daniel Floyd (CAND-044) — 62.8/100
9. April Booth (CAND-082) — 62.3/100
10. Natalie Meza (CAND-074) — 62.3/100


**Agent:**

## What changed since the last ranking

- Newly in the top 10: April Booth, Natalie Meza
- Dropped out of the top 10: Marcus Webb, Matthew Fernandez
- Anthony Rodriguez moved up: #5 → #3
- Olivia Harris moved down: #3 → #4
- Nicole Hamilton moved down: #4 → #5
- George Hobbs moved up: #7 → #6
- Paul Larsen moved up: #9 → #7
- Daniel Floyd moved up: #10 → #8

# Candidate Match Report — Senior Frontend Engineer

**Seniority:** Staff/Lead  
**Minimum experience:** 3+ years  
**Must-have:** React, TypeScript, Redux, HTML5, CSS3, Jest, GraphQL  
**Nice-to-have:** Next.js, WCAG  

## Round 1 — Initial screen: top 10 of 100 resumes

| Rank | Candidate | Score /100 | Must-have coverage | Why |
|---|---|---|---|---|
| 1 | John Whitfield (CAND-001) | 88.5 | 7/7 | matches 7/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 2 nice-to-have(s): Next.js, WCAG; 5 yrs experience meets the 3+ yr bar |
| 2 | Priya Nataraj (CAND-003) | 77.1 | 7/7 | matches 7/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 1 nice-to-have(s): Next.js; 4 yrs experience meets the 3+ yr bar |
| 3 | Anthony Rodriguez (CAND-012) | 72.9 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest, GraphQL; also brings 2 nice-to-have(s): Next.js, WCAG; 6 yrs experience meets the 3+ yr bar |
| 4 | Olivia Harris (CAND-083) | 70.4 | 6/7 | matches 6/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing GraphQL; also brings 1 nice-to-have(s): Next.js; 6 yrs experience meets the 3+ yr bar |
| 5 | Nicole Hamilton (CAND-093) | 69.6 | 6/7 | matches 6/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing GraphQL; also brings 1 nice-to-have(s): Next.js; 9 yrs experience meets the 3+ yr bar |
| 6 | George Hobbs (CAND-056) | 67.1 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest, GraphQL; also brings 2 nice-to-have(s): Next.js, WCAG; 2 yrs experience is below the 3+ yr bar |
| 7 | Paul Larsen (CAND-050) | 62.9 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest, GraphQL; also brings 1 nice-to-have(s): WCAG; 5 yrs experience meets the 3+ yr bar |
| 8 | Daniel Floyd (CAND-044) | 62.8 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, HTML5, CSS3); missing Redux, GraphQL; also brings 1 nice-to-have(s): Next.js; 8 yrs experience meets the 3+ yr bar |
| 9 | April Booth (CAND-082) | 62.3 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest, GraphQL; also brings 1 nice-to-have(s): Next.js; 4 yrs experience meets the 3+ yr bar |
| 10 | Natalie Meza (CAND-074) | 62.3 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest, GraphQL; also brings 1 nice-to-have(s): WCAG; 7 yrs experience meets the 3+ yr bar |

## Round 2 — Deep analysis of the shortlist

### John Whitfield (CAND-001) — Strong match

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- GraphQL
- Next.js
- WCAG

**Gaps**
- None identified against current requirements.

### Priya Nataraj (CAND-003) — Strong match

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- GraphQL
- Next.js

**Gaps**
- None identified against current requirements.

### Anthony Rodriguez (CAND-012) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.
- Hands-on GraphQL experience would meaningfully strengthen this application.

### Olivia Harris (CAND-083) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on GraphQL experience would meaningfully strengthen this application.

### Nicole Hamilton (CAND-093) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on GraphQL experience would meaningfully strengthen this application.

### George Hobbs (CAND-056) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.
- Hands-on GraphQL experience would meaningfully strengthen this application.

### Paul Larsen (CAND-050) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- WCAG

**Gaps**
- Jest
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.
- Hands-on GraphQL experience would meaningfully strengthen this application.

### Daniel Floyd (CAND-044) — Borderline

**Strengths**
- React
- TypeScript
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- Redux
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on Redux experience would meaningfully strengthen this application.
- Hands-on GraphQL experience would meaningfully strengthen this application.

### April Booth (CAND-082) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js

**Gaps**
- Jest
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.
- Hands-on GraphQL experience would meaningfully strengthen this application.

### Natalie Meza (CAND-074) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- WCAG

**Gaps**
- Jest
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.
- Hands-on GraphQL experience would meaningfully strengthen this application.

---
_Ask for a head-to-head comparison, interview questions, or a hire/no-hire recommendation for any candidate above - or refine the requirements and I'll re-rank._

_(saved to `/home/claude/resume-matching-agent/data/reports/Senior_Frontend_Engineer-20260813-225952.md`)_


**You:**

Increase the minimum years to 5


**Agent:**

Got it — updating the requirements and re-ranking against all 100 resumes...


**Agent:**

**Round 1 shortlist — top 10 of 100:**
1. John Whitfield (CAND-001) — 88.5/100
2. Priya Nataraj (CAND-003) — 74.1/100
3. Anthony Rodriguez (CAND-012) — 72.9/100
4. Olivia Harris (CAND-083) — 70.4/100
5. Nicole Hamilton (CAND-093) — 69.6/100
6. George Hobbs (CAND-056) — 63.1/100
7. Paul Larsen (CAND-050) — 62.9/100
8. Daniel Floyd (CAND-044) — 62.8/100
9. Natalie Meza (CAND-074) — 62.3/100
10. Jamie Cantu (CAND-088) — 62.1/100


**Agent:**

## What changed since the last ranking

- Newly in the top 10: Jamie Cantu
- Dropped out of the top 10: April Booth
- Natalie Meza moved up: #10 → #9

# Candidate Match Report — Senior Frontend Engineer

**Seniority:** Staff/Lead  
**Minimum experience:** 5+ years  
**Must-have:** React, TypeScript, Redux, HTML5, CSS3, Jest, GraphQL  
**Nice-to-have:** Next.js, WCAG  

## Round 1 — Initial screen: top 10 of 100 resumes

| Rank | Candidate | Score /100 | Must-have coverage | Why |
|---|---|---|---|---|
| 1 | John Whitfield (CAND-001) | 88.5 | 7/7 | matches 7/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 2 nice-to-have(s): Next.js, WCAG; 5 yrs experience meets the 5+ yr bar |
| 2 | Priya Nataraj (CAND-003) | 74.1 | 7/7 | matches 7/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 1 nice-to-have(s): Next.js; 4 yrs experience is below the 5+ yr bar |
| 3 | Anthony Rodriguez (CAND-012) | 72.9 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest, GraphQL; also brings 2 nice-to-have(s): Next.js, WCAG; 6 yrs experience meets the 5+ yr bar |
| 4 | Olivia Harris (CAND-083) | 70.4 | 6/7 | matches 6/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing GraphQL; also brings 1 nice-to-have(s): Next.js; 6 yrs experience meets the 5+ yr bar |
| 5 | Nicole Hamilton (CAND-093) | 69.6 | 6/7 | matches 6/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing GraphQL; also brings 1 nice-to-have(s): Next.js; 9 yrs experience meets the 5+ yr bar |
| 6 | George Hobbs (CAND-056) | 63.1 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest, GraphQL; also brings 2 nice-to-have(s): Next.js, WCAG; 2 yrs experience is below the 5+ yr bar |
| 7 | Paul Larsen (CAND-050) | 62.9 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest, GraphQL; also brings 1 nice-to-have(s): WCAG; 5 yrs experience meets the 5+ yr bar |
| 8 | Daniel Floyd (CAND-044) | 62.8 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, HTML5, CSS3); missing Redux, GraphQL; also brings 1 nice-to-have(s): Next.js; 8 yrs experience meets the 5+ yr bar |
| 9 | Natalie Meza (CAND-074) | 62.3 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest, GraphQL; also brings 1 nice-to-have(s): WCAG; 7 yrs experience meets the 5+ yr bar |
| 10 | Jamie Cantu (CAND-088) | 62.1 | 5/7 | matches 5/7 must-have requirement(s) (React, TypeScript, HTML5, CSS3); missing Redux, Jest; also brings 1 nice-to-have(s): Next.js; 14 yrs experience meets the 5+ yr bar |

## Round 2 — Deep analysis of the shortlist

### John Whitfield (CAND-001) — Strong match

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- GraphQL
- Next.js
- WCAG

**Gaps**
- None identified against current requirements.

### Priya Nataraj (CAND-003) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- GraphQL
- Next.js

**Gaps**
- None identified against current requirements.

### Anthony Rodriguez (CAND-012) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.
- Hands-on GraphQL experience would meaningfully strengthen this application.

### Olivia Harris (CAND-083) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on GraphQL experience would meaningfully strengthen this application.

### Nicole Hamilton (CAND-093) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on GraphQL experience would meaningfully strengthen this application.

### George Hobbs (CAND-056) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.
- Hands-on GraphQL experience would meaningfully strengthen this application.

### Paul Larsen (CAND-050) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- WCAG

**Gaps**
- Jest
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.
- Hands-on GraphQL experience would meaningfully strengthen this application.

### Daniel Floyd (CAND-044) — Borderline

**Strengths**
- React
- TypeScript
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- Redux
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on Redux experience would meaningfully strengthen this application.
- Hands-on GraphQL experience would meaningfully strengthen this application.

### Natalie Meza (CAND-074) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- WCAG

**Gaps**
- Jest
- GraphQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.
- Hands-on GraphQL experience would meaningfully strengthen this application.

### Jamie Cantu (CAND-088) — Borderline

**Strengths**
- React
- TypeScript
- HTML5
- CSS3
- GraphQL
- Next.js

**Gaps**
- Redux
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Redux experience would meaningfully strengthen this application.
- Hands-on Jest experience would meaningfully strengthen this application.

---
_Ask for a head-to-head comparison, interview questions, or a hire/no-hire recommendation for any candidate above - or refine the requirements and I'll re-rank._

_(saved to `/home/claude/resume-matching-agent/data/reports/Senior_Frontend_Engineer-20260813-225952.md`)_


**You:**

Show me interview questions for the top candidate


**Agent:**

**Screening questions for John Whitfield (CAND-001)**

1. Walk me through a production project where you used TypeScript - what was your specific role, and what would you do differently now?
2. You've worked across 2 company(ies) in 5 years - what's driven those moves?
3. You've worked in Fintech / BFSI - what's one domain-specific constraint from that industry that shaped how you built software?
4. Tell me about a time you disagreed with a technical decision on your team. What did you do?


**You:**

I'm done


**Agent:**

Sounds good — wrapping up here. The full report is saved to disk if you want to revisit it (`/home/claude/resume-matching-agent/data/reports/Senior_Frontend_Engineer-20260813-225952.md`). Good luck with the search!


</details>

## Scenario 5: Help fallback + graceful exit

**Job description:** Backend Engineer (Node.js)  
**Demonstrates:** An open-ended "what can you help me with" gets a useful capability summary instead of a dead end, then a normal comparison, then "goodbye".

<details>
<summary>Full transcript</summary>


**Agent:**

Got the job description (133 words). Parsing requirements...


**Agent:**

**Backend Engineer** — Mid-level, 3+ yrs

**Must-have:** Node.js, REST API, SQL, PostgreSQL, Git
**Nice-to-have:** Microservices, Kafka, Docker, Kubernetes, JWT, OAuth2


**Agent:**

Searched all 100 resumes in the pool. Scoring and ranking now...


**Agent:**

**Round 1 shortlist — top 10 of 100:**
1. Jeffrey Wood (CAND-061) — 76.6/100
2. Laura Barnett (CAND-064) — 74.4/100
3. Julie Roberts (CAND-096) — 72.9/100
4. Evelyn Galvan (CAND-037) — 72.5/100
5. Tracey Higgins (CAND-059) — 70.0/100
6. Carmen Rose (CAND-017) — 67.8/100
7. Taylor Harris (CAND-028) — 65.2/100
8. Trevor Walker (CAND-057) — 65.2/100
9. Alicia Hubbard (CAND-079) — 64.1/100
10. Katherine Miller (CAND-078) — 62.4/100


**Agent:**

# Candidate Match Report — Backend Engineer

**Seniority:** Mid-level  
**Minimum experience:** 3+ years  
**Must-have:** Node.js, REST API, SQL, PostgreSQL, Git  
**Nice-to-have:** Microservices, Kafka, Docker, Kubernetes, JWT, OAuth2  

## Round 1 — Initial screen: top 10 of 100 resumes

| Rank | Candidate | Score /100 | Must-have coverage | Why |
|---|---|---|---|---|
| 1 | Jeffrey Wood (CAND-061) | 76.6 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 5 nice-to-have(s): Kafka, Docker, Kubernetes; 3 yrs experience meets the 3+ yr bar |
| 2 | Laura Barnett (CAND-064) | 74.4 | 5/5 | matches 5/5 must-have requirement(s) (Node.js, REST API, SQL, PostgreSQL); also brings 2 nice-to-have(s): Microservices, Kubernetes; 3 yrs experience meets the 3+ yr bar |
| 3 | Julie Roberts (CAND-096) | 72.9 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 4 nice-to-have(s): Kafka, Kubernetes, JWT; 5 yrs experience meets the 3+ yr bar |
| 4 | Evelyn Galvan (CAND-037) | 72.5 | 5/5 | matches 5/5 must-have requirement(s) (Node.js, REST API, SQL, PostgreSQL); also brings 3 nice-to-have(s): Microservices, Docker, Kubernetes; 2 yrs experience is below the 3+ yr bar |
| 5 | Tracey Higgins (CAND-059) | 70.0 | 5/5 | matches 5/5 must-have requirement(s) (Node.js, REST API, SQL, PostgreSQL); also brings 2 nice-to-have(s): JWT, OAuth2; 2 yrs experience is below the 3+ yr bar |
| 6 | Carmen Rose (CAND-017) | 67.8 | 5/5 | matches 5/5 must-have requirement(s) (Node.js, REST API, SQL, PostgreSQL); 8 yrs experience meets the 3+ yr bar |
| 7 | Taylor Harris (CAND-028) | 65.2 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 2 nice-to-have(s): Kafka, Docker; 4 yrs experience meets the 3+ yr bar |
| 8 | Trevor Walker (CAND-057) | 65.2 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 2 nice-to-have(s): JWT, OAuth2; 5 yrs experience meets the 3+ yr bar |
| 9 | Alicia Hubbard (CAND-079) | 64.1 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 2 nice-to-have(s): Microservices, Kafka; 8 yrs experience meets the 3+ yr bar |
| 10 | Katherine Miller (CAND-078) | 62.4 | 4/5 | matches 4/5 must-have requirement(s) (Node.js, REST API, SQL, Git); missing PostgreSQL; also brings 3 nice-to-have(s): Microservices, Kafka, Kubernetes; 2 yrs experience is below the 3+ yr bar |

## Round 2 — Deep analysis of the shortlist

### Jeffrey Wood (CAND-061) — Strong match

**Strengths**
- Node.js
- REST API
- SQL
- Git
- Kafka
- Docker
- Kubernetes
- JWT
- OAuth2

**Gaps**
- PostgreSQL

### Laura Barnett (CAND-064) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- PostgreSQL
- Git
- Microservices
- Kubernetes

**Gaps**
- None identified against current requirements.

### Julie Roberts (CAND-096) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- Git
- Kafka
- Kubernetes
- JWT
- OAuth2

**Gaps**
- PostgreSQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on PostgreSQL experience would meaningfully strengthen this application.

### Evelyn Galvan (CAND-037) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- PostgreSQL
- Git
- Microservices
- Docker
- Kubernetes

**Gaps**
- None identified against current requirements.

**Improvement suggestions** _(borderline candidate)_
- Currently under the 3+ year bar - worth probing depth in the interview.

### Tracey Higgins (CAND-059) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- PostgreSQL
- Git
- JWT
- OAuth2

**Gaps**
- None identified against current requirements.

**Improvement suggestions** _(borderline candidate)_
- Currently under the 3+ year bar - worth probing depth in the interview.

### Carmen Rose (CAND-017) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- PostgreSQL
- Git

**Gaps**
- None identified against current requirements.

### Taylor Harris (CAND-028) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- Git
- Kafka
- Docker

**Gaps**
- PostgreSQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on PostgreSQL experience would meaningfully strengthen this application.

### Trevor Walker (CAND-057) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- Git
- JWT
- OAuth2

**Gaps**
- PostgreSQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on PostgreSQL experience would meaningfully strengthen this application.

### Alicia Hubbard (CAND-079) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- Git
- Microservices
- Kafka

**Gaps**
- PostgreSQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on PostgreSQL experience would meaningfully strengthen this application.

### Katherine Miller (CAND-078) — Borderline

**Strengths**
- Node.js
- REST API
- SQL
- Git
- Microservices
- Kafka
- Kubernetes

**Gaps**
- PostgreSQL

**Improvement suggestions** _(borderline candidate)_
- Hands-on PostgreSQL experience would meaningfully strengthen this application.

---
_Ask for a head-to-head comparison, interview questions, or a hire/no-hire recommendation for any candidate above - or refine the requirements and I'll re-rank._

_(saved to `/home/claude/resume-matching-agent/data/reports/Backend_Engineer-20260813-225952.md`)_


**You:**

What can you help me with?


**Agent:**

I can compare candidates, generate interview questions, give a hire/no-hire recommendation, or re-rank if you adjust the requirements. Current top 3: Jeffrey Wood, Laura Barnett, Julie Roberts.


**You:**

Compare the top matches side by side


**Agent:**

**Comparison**

- **Jeffrey Wood (CAND-061)** — matches 4 must-have(s), 5 nice-to-have(s); strengths: 3 yrs in SaaS / B2B
- **Laura Barnett (CAND-064)** — matches 5 must-have(s), 2 nice-to-have(s); strengths: Certified Kubernetes Administrator (CKA), 3 yrs in Fintech / BFSI
- **Julie Roberts (CAND-096)** — matches 4 must-have(s), 4 nice-to-have(s); strengths: Meta Front-End Developer Professional Certificate, 5 yrs in EdTech

Laura Barnett leads this comparison, covering 5/5 must-have requirement(s) versus Jeffrey Wood's 4/5. The gap comes down to PostgreSQL.


**You:**

goodbye


**Agent:**

Sounds good — wrapping up here. The full report is saved to disk if you want to revisit it (`/home/claude/resume-matching-agent/data/reports/Backend_Engineer-20260813-225952.md`). Good luck with the search!


</details>

## Scenario 6: Direct candidate-ID references

**Job description:** Senior Frontend Engineer (React)  
**Demonstrates:** Power-user path: referencing candidates by their raw CAND-XXX ID instead of by name, including a candidate (CAND-004 / Marcus) who didn't rank #1.

<details>
<summary>Full transcript</summary>


**Agent:**

Got the job description (250 words). Parsing requirements...


**Agent:**

**Senior Frontend Engineer** — Staff/Lead, 3+ yrs

**Must-have:** React, TypeScript, Redux, HTML5, CSS3, Jest
**Nice-to-have:** Next.js, GraphQL, WCAG


**Agent:**

Searched all 100 resumes in the pool. Scoring and ranking now...


**Agent:**

**Round 1 shortlist — top 10 of 100:**
1. John Whitfield (CAND-001) — 88.5/100
2. Priya Nataraj (CAND-003) — 80.5/100
3. Olivia Harris (CAND-083) — 74.2/100
4. Nicole Hamilton (CAND-093) — 73.4/100
5. Anthony Rodriguez (CAND-012) — 72.2/100
6. Marcus Webb (CAND-004) — 66.6/100
7. George Hobbs (CAND-056) — 66.4/100
8. Matthew Fernandez (CAND-023) — 65.8/100
9. Paul Larsen (CAND-050) — 65.5/100
10. Daniel Floyd (CAND-044) — 65.5/100


**Agent:**

# Candidate Match Report — Senior Frontend Engineer

**Seniority:** Staff/Lead  
**Minimum experience:** 3+ years  
**Must-have:** React, TypeScript, Redux, HTML5, CSS3, Jest  
**Nice-to-have:** Next.js, GraphQL, WCAG  

## Round 1 — Initial screen: top 10 of 100 resumes

| Rank | Candidate | Score /100 | Must-have coverage | Why |
|---|---|---|---|---|
| 1 | John Whitfield (CAND-001) | 88.5 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 3 nice-to-have(s): Next.js, GraphQL, WCAG; 5 yrs experience meets the 3+ yr bar |
| 2 | Priya Nataraj (CAND-003) | 80.5 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 2 nice-to-have(s): Next.js, GraphQL; 4 yrs experience meets the 3+ yr bar |
| 3 | Olivia Harris (CAND-083) | 74.2 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 1 nice-to-have(s): Next.js; 6 yrs experience meets the 3+ yr bar |
| 4 | Nicole Hamilton (CAND-093) | 73.4 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); also brings 1 nice-to-have(s): Next.js; 9 yrs experience meets the 3+ yr bar |
| 5 | Anthony Rodriguez (CAND-012) | 72.2 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 2 nice-to-have(s): Next.js, WCAG; 6 yrs experience meets the 3+ yr bar |
| 6 | Marcus Webb (CAND-004) | 66.6 | 6/6 | matches 6/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); 3 yrs experience meets the 3+ yr bar |
| 7 | George Hobbs (CAND-056) | 66.4 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 2 nice-to-have(s): Next.js, WCAG; 2 yrs experience is below the 3+ yr bar |
| 8 | Matthew Fernandez (CAND-023) | 65.8 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 1 nice-to-have(s): GraphQL; 4 yrs experience meets the 3+ yr bar |
| 9 | Paul Larsen (CAND-050) | 65.5 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, Redux, HTML5); missing Jest; also brings 1 nice-to-have(s): WCAG; 5 yrs experience meets the 3+ yr bar |
| 10 | Daniel Floyd (CAND-044) | 65.5 | 5/6 | matches 5/6 must-have requirement(s) (React, TypeScript, HTML5, CSS3); missing Redux; also brings 1 nice-to-have(s): Next.js; 8 yrs experience meets the 3+ yr bar |

## Round 2 — Deep analysis of the shortlist

### John Whitfield (CAND-001) — Strong match

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js
- GraphQL
- WCAG

**Gaps**
- None identified against current requirements.

### Priya Nataraj (CAND-003) — Strong match

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js
- GraphQL

**Gaps**
- None identified against current requirements.

### Olivia Harris (CAND-083) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- None identified against current requirements.

### Nicole Hamilton (CAND-093) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- None identified against current requirements.

### Anthony Rodriguez (CAND-012) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Marcus Webb (CAND-004) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Jest

**Gaps**
- None identified against current requirements.

### George Hobbs (CAND-056) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- Next.js
- WCAG

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Matthew Fernandez (CAND-023) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- GraphQL

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Paul Larsen (CAND-050) — Borderline

**Strengths**
- React
- TypeScript
- Redux
- HTML5
- CSS3
- WCAG

**Gaps**
- Jest

**Improvement suggestions** _(borderline candidate)_
- Hands-on Jest experience would meaningfully strengthen this application.

### Daniel Floyd (CAND-044) — Borderline

**Strengths**
- React
- TypeScript
- HTML5
- CSS3
- Jest
- Next.js

**Gaps**
- Redux

**Improvement suggestions** _(borderline candidate)_
- Hands-on Redux experience would meaningfully strengthen this application.

---
_Ask for a head-to-head comparison, interview questions, or a hire/no-hire recommendation for any candidate above - or refine the requirements and I'll re-rank._

_(saved to `/home/claude/resume-matching-agent/data/reports/Senior_Frontend_Engineer-20260813-225952.md`)_


**You:**

Compare CAND-001 and CAND-002


**Agent:**

**Comparison**

- **John Whitfield (CAND-001)** — matches 6 must-have(s), 3 nice-to-have(s); strengths: Meta Front-End Developer Professional Certificate, 5 yrs in Fintech / BFSI
- **Jane Okafor (CAND-002)** — matches 5 must-have(s), 1 nice-to-have(s); strengths: Certified Kubernetes Administrator (CKA), 2 yrs in E-commerce

John Whitfield leads this comparison, covering 6/6 must-have requirement(s) versus Jane Okafor's 5/6. The gap comes down to TypeScript.


**You:**

Generate interview questions for CAND-004


**Agent:**

**Screening questions for Marcus Webb (CAND-004)**

1. Walk me through a production project where you used React - what was your specific role, and what would you do differently now?
2. You've worked across 3 company(ies) in 3 years - what's driven those moves?
3. This role expects Next.js, which isn't explicit on your resume - how would you ramp up on that, and have you touched anything adjacent to it?
4. This role expects GraphQL, which isn't explicit on your resume - how would you ramp up on that, and have you touched anything adjacent to it?
5. This role expects WCAG, which isn't explicit on your resume - how would you ramp up on that, and have you touched anything adjacent to it?
6. You've worked in Logistics - what's one domain-specific constraint from that industry that shaped how you built software?
7. Tell me about a time you disagreed with a technical decision on your team. What did you do?


**You:**

That's all


**Agent:**

Sounds good — wrapping up here. The full report is saved to disk if you want to revisit it (`/home/claude/resume-matching-agent/data/reports/Senior_Frontend_Engineer-20260813-225952.md`). Good luck with the search!


</details>
