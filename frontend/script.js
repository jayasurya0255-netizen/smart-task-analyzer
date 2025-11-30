/************************************
 * Smart Task Analyzer - script.js
 * With Eisenhower Matrix View
 ************************************/

console.log("%cScript Loaded", "color: green; font-weight: bold;");

// ----------------------
// Local Task Storage
// ----------------------
let localTasks = [];

function updateLocalCount() {
    const badge = document.getElementById('localCount');
    if (badge) badge.textContent = localTasks.length.toString();
}

function showLocalTasks() {
    const listDiv = document.getElementById('localTasksList');
    listDiv.innerHTML = '';

    if (localTasks.length === 0) {
        listDiv.innerHTML = "<p>No tasks added yet.</p>";
        updateLocalCount();
        return;
    }

    localTasks.forEach(t => {
        const item = document.createElement('div');
        item.className = "task-card";

        item.innerHTML = `
            <strong>${t.title}</strong><br>
            <small>Due: ${t.due_date || "N/A"}</small><br>
            <small>Importance: ${t.importance}</small><br>
            <small>Estimated Hours: ${t.estimated_hours || "N/A"}</small><br>
            <small>Dependencies: ${t.dependencies.join(", ") || "None"}</small>
        `;

        listDiv.appendChild(item);
    });

    updateLocalCount();
}

// Add Task Manually
document.getElementById("task-form").addEventListener("submit", (e) => {
    e.preventDefault();

    const t = {
        id: "task_" + Date.now(),
        title: document.getElementById("title").value.trim(),
        due_date: document.getElementById("due_date").value.trim() || null,
        estimated_hours: document.getElementById("estimated_hours").value.trim()
            ? Number(document.getElementById("estimated_hours").value.trim())
            : null,
        importance: document.getElementById("importance").value.trim()
            ? Number(document.getElementById("importance").value.trim())
            : 5,
        dependencies: document.getElementById("dependencies").value
            .split(",").map(d => d.trim()).filter(Boolean)
    };

    localTasks.push(t);
    showLocalTasks();
    e.target.reset();
});

// ----------------------
// Display Task Results
// ----------------------
function displayResults(tasks) {
    const resultsDiv = document.getElementById('results');
    const hint = document.getElementById('resultsHint');
    resultsDiv.innerHTML = '';

    if (hint) {
        hint.textContent = tasks.length
            ? "Tasks sorted by priority score (highest first)."
            : "Run an analysis to see prioritized tasks.";
    }

    if (!tasks.length) {
        resultsDiv.innerHTML = '<p>No tasks to display.</p>';
        return;
    }

    tasks.forEach(task => {
        const card = document.createElement('div');
        card.className = 'task-card';

        let urgencyColor = 'green';
        if (task.score >= 0.7) urgencyColor = 'red';
        else if (task.score >= 0.4) urgencyColor = 'orange';

        card.innerHTML = `
            <h3>${task.title}</h3>
            <p class="task-meta"><strong>Score:</strong> <span style="color:${urgencyColor}">${task.score}</span></p>
            <p class="task-meta">Due Date: ${task.raw?.due_date || 'N/A'}</p>
            <p class="task-meta">Importance: ${task.raw?.importance ?? 'N/A'}</p>
            <p class="task-meta">Estimated Hours: ${task.raw?.estimated_hours ?? 'N/A'}</p>
            <small>${task.explanation}</small>
        `;

        resultsDiv.appendChild(card);
    });
}

// ----------------------
// Analyze Tasks (calls backend)
// ----------------------
async function analyzeTasks() {
    console.log("Analyze button clicked");

    let jsonTasks = [];
    const inputText = document.getElementById('taskInput').value.trim();

    if (inputText) {
        try {
            jsonTasks = JSON.parse(inputText);
            if (!Array.isArray(jsonTasks)) throw new Error("JSON must be an array");
        } catch (e) {
            alert("Invalid JSON: " + e.message);
            return;
        }
    }

    const finalTasks = [...localTasks, ...jsonTasks];
    if (finalTasks.length === 0) {
        alert("No tasks to analyze.");
        return;
    }

    console.log("Sending data:", finalTasks);

    try {
        const response = await fetch('https://dashboard.render.com/web/srv-d4m56eruibrs738cakc0/deploys/dep-d4m5ragdl3ps73fu459g?m=max', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                tasks: finalTasks,
                strategy: document.getElementById("strategyDropdown").value
            })
        });

        const data = await response.json();
        console.log("Response received:", data);

        if (!response.ok) {
            console.error("Server error:", data);
            alert("Error: " + JSON.stringify(data));
            return;
        }

        // Ensure urgency and importance_norm exist for each task (fallback to client-side calculation)
        data.tasks.forEach(t => {
            if (typeof t.importance_norm !== "number") {
                const rawImp = t.raw?.importance;
                if (typeof rawImp === "number") {
                    t.importance_norm = Math.max(0, Math.min(1, (rawImp - 1) / 9));
                } else {
                    t.importance_norm = 0;
                }
            }

            if (typeof t.urgency !== "number") {
                t.urgency = computeUrgencyFromDate(t.raw?.due_date);
            }
        });

        window.lastAnalysis = data;
        console.log("lastAnalysis updated:", window.lastAnalysis);

        displayResults(data.tasks);

    } catch (error) {
        console.error("Network error:", error);
        alert("Network error. Is Django running?");
    }
}

document.getElementById("analyzeBtn").addEventListener("click", analyzeTasks);

// ----------------------
// Count Complete Entries
// ----------------------
document.getElementById('countBtn').addEventListener('click', () => {
    let jsonTasks = [];
    const inputText = document.getElementById('taskInput').value.trim();

    if (inputText) {
        try {
            jsonTasks = JSON.parse(inputText);
        } catch (e) {
            alert("Invalid JSON");
            return;
        }
    }

    const finalTasks = [...localTasks, ...jsonTasks];

    const complete = finalTasks.filter(t =>
        t.title &&
        t.due_date &&
        t.importance !== undefined &&
        t.importance !== null &&
        t.estimated_hours !== undefined &&
        t.estimated_hours !== null &&
        t.estimated_hours !== ''
    );

    const box = document.getElementById("countResults");
    box.innerHTML = `<strong>${complete.length} complete entries:</strong>`;

    if (!complete.length) return;

    const list = document.createElement("div");
    list.className = "complete-list";

    complete.forEach(t => {
        const div = document.createElement("div");
        div.className = "task-card";
        div.innerHTML = `<strong>${t.title}</strong> — Due: ${t.due_date}, Est: ${t.estimated_hours}h, Imp: ${t.importance}`;
        list.appendChild(div);
    });

    box.appendChild(list);
});

// ----------------------
// Utility: compute urgency from due_date (client-side fallback)
// ----------------------
function computeUrgencyFromDate(dueDateStr) {
    if (!dueDateStr) return 0;
    const today = new Date();
    const due = new Date(dueDateStr);
    if (isNaN(due.getTime())) return 0;

    const msPerDay = 24 * 60 * 60 * 1000;
    const diffDays = Math.round((due - today) / msPerDay); // can be negative for overdue

    if (diffDays <= 0) return 1;       // overdue or due today => max urgency
    if (diffDays >= 30) return 0;      // >= 30 days away => low urgency

    // linearly scale between 0 and 1 for 1..29 days
    return Math.max(0, Math.min(1, 1 - diffDays / 30));
}

// ----------------------
// Eisenhower Matrix
// ----------------------
function renderEisenhowerMatrix() {
    console.log("renderEisenhowerMatrix called");

    const analysis = window.lastAnalysis;
    const wrapper = document.getElementById("matrixContainer");
    const matrix = document.getElementById("matrix");

    if (!analysis || !analysis.tasks || !analysis.tasks.length) {
        alert("Run Analyze first.");
        return;
    }

    wrapper.style.display = "block";
    matrix.innerHTML = "";

    const grid = document.createElement("div");
    grid.className = "eisen-grid";

    // Buckets
    const zones = {
        do: [],         // Urgent + Important
        plan: [],       // Not Urgent + Important
        delegate: [],   // Urgent + Not Important
        eliminate: []   // Not Urgent + Not Important
    };

    analysis.tasks.forEach(t => {
        const urgent = (t.urgency || 0) >= 0.5;
        const important = (t.importance_norm || 0) >= 0.5;

        if (urgent && important) zones.do.push(t);
        else if (!urgent && important) zones.plan.push(t);
        else if (urgent && !important) zones.delegate.push(t);
        else zones.eliminate.push(t);
    });

    const labels = {
        do: "Urgent + Important (DO NOW)",
        plan: "Not Urgent + Important (PLAN)",
        delegate: "Urgent + Not Important (DELEGATE)",
        eliminate: "Not Urgent + Not Important (ELIMINATE)"
    };

    Object.keys(zones).forEach(k => {
        const cell = document.createElement("div");
        // class names used by CSS: .eisen-cell.do, .plan, .delegate, .eliminate
        cell.className = `eisen-cell ${k}`;

        const header = document.createElement("div");
        header.className = "eisen-header";
        header.textContent = `${labels[k]} — ${zones[k].length}`;
        cell.appendChild(header);

        const list = document.createElement("div");
        list.className = "eisen-list";

        zones[k].forEach(t => {
            const card = document.createElement("div");
            card.className = "task-card eisen-item";
            card.innerHTML = `
                <strong>${t.title}</strong>
                <div class="muted">
                  Urgency: ${(t.urgency * 100).toFixed(0)}% • Importance: ${(t.importance_norm * 100).toFixed(0)}%
                </div>
            `;
            list.appendChild(card);
        });

        cell.appendChild(list);
        grid.appendChild(cell);
    });

    matrix.appendChild(grid);
}

document.getElementById("showMatrixBtn").addEventListener("click", renderEisenhowerMatrix);
