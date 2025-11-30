📌 Smart Task Analyzer — README

A lightweight, intelligent task-ranking engine that scores and prioritizes tasks using urgency, importance, effort, and dependency logic. Includes a modern UI, JSON input support, live scoring, and visualization extensions (Eisenhower Matrix + Dependency Graph).

🚀 Setup Instructions
1. Clone repository
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

2. Install Backend (Django + DRF)
pip install -r requirements.txt


If you don’t have a requirements.txt, generate one:

pip freeze > requirements.txt

3. Run Backend API
python manage.py migrate
python manage.py runserver


Backend runs on:

http://127.0.0.1:8000


Endpoints:

POST /api/tasks/analyze/ → Returns scored + sorted tasks

POST /api/tasks/validate/ → Checks JSON completeness (optional)

4. Launch Frontend

Just open:

index.html


or use a static server (optional):

npx serve .

🧠 Algorithm Explanation (400 words)

The Smart Task Analyzer uses a weighted multi-factor scoring model designed to mimic real-world human prioritization. The goal is to generate a priority score between 0 and 1, which determines the task order.

1. Urgency Calculation

Urgency measures how close today is to the task’s due date.
Formula:

urgency = max(0, 1 - (days_until_due / 10))


Meaning:

Tasks overdue → urgency = 1.0

Due within 3 days → urgency ~0.7–1.0

Far deadlines → low urgency

This models natural pressure experienced as deadlines approach.

2. Importance Normalization

A task’s importance uses a 1–10 scale but normalized:

importance_norm = importance / 10


Importance represents:

business value

customer impact

severity/priority
This ensures importance remains proportional and intuitive.

3. Effort / Quick-Wins Logic

To avoid always prioritizing large tasks, the algorithm rewards "quick wins":

if estimated_hours < 2:
    + small booster


This aligns with productivity principles (Pareto, GTD, quick wins).

4. Dependency Weighting

If a task blocks many others, its priority increases:

dependency_weight = 0.1 * (number_of_tasks_depending_on_it)


Circular dependencies are detected and flagged; they increase priority to indicate critical workflow issues.

5. Strategy Modes

The user selects how the weighting behaves:

Strategy	Behavior
Smart Balance	Combines all factors evenly
Fastest Wins	Smallest tasks first
High Impact	Prioritizes importance heavily
Deadline Driven	Urgency dominates scoring
6. Final Score
final_score = 
  (0.45 * urgency) +
  (0.35 * importance_norm) +
  (0.10 * effort_modifier) +
  (0.10 * dependency_weight)


This ensures:

Deadlines matter

High importance tasks surface

Short tasks can bubble up

Workflow blockers get priority

The scoring feels natural, fair, and adaptable to multiple workflows.

🎨 Design Decisions
1. Client-Side Rendering

The entire UI runs in the browser for speed and simplicity. No frameworks required.
Trade-off:
No virtual DOM → code is slightly more verbose, but loads instantly.

2. Django API

Django + DRF was chosen because:

clean request validation

fast scoring logic

easy extensibility
Trade-off:
Heavier than lightweight Flask, but more structured and scalable.

3. No Database Needed

Tasks are sent as JSON → fully stateless.
Trade-off:
No persistence, but extremely easy to test and deploy.

4. Visualization

Eisenhower Matrix and Dependency Graph provide deeper insights.
Trade-off:
SVG rendering is manual, but gives full control and zero dependencies.

⏳ Time Breakdown
Task	Time
Frontend UI development	2 hours
JSON parsing + validation	40 minutes
Scoring algorithm design	1 hour
Strategy modes implementation	45 minutes
Django backend setup	45 minutes
Visualization (Matrix + Graph)	1 hour
Testing + debugging	30 minutes
README + documentation	30 minutes

Total: ~7 hours

⭐ Bonus Challenges Attempted

✔ Eisenhower Matrix View
✔ Dependency Graph Visualization
✔ Circular dependency detection
✖ Date intelligence (weekends/holidays)
✖ Reinforcement-learning feedback system
✖ Unit testing suite

🚀 Future Improvements

If given more time, I would add:

1. Machine Learning-Driven Priority Learning

Allow users to mark recommendations as "helpful / not helpful"
→ algorithm auto-adjusts weights per user.

2. Task Persistence

Save tasks using:

localStorage

SQLite backend

Firebase or Supabase cloud storage

3. Natural-Language Task Input

User types:

“Finish report by Friday, takes 2 hours, high priority”

The system auto-generates a structured task object.

4. Team Mode

Multiple users, shared tasks, real-time dependency resolution.

5. Calendar + Gantt Timeline

Visual timeline showing deadlines and effort distribution.