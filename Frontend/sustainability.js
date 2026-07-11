const addGoalBtn = document.getElementById("add-goal-btn");
const activeGoalsContainer =
    document.getElementById("active-goals");

const completedGoalsContainer =
    document.getElementById("completed-goals");

let goals =
    JSON.parse(localStorage.getItem("sustainabilityGoals")) || [];

function saveGoals() {
    localStorage.setItem(
        "sustainabilityGoals",
        JSON.stringify(goals)
    );
}

function renderGoals() {
    activeGoalsContainer.innerHTML = "";
    completedGoalsContainer.innerHTML = "";
    let activeCount = 0;
    let completedCount = 0;
    goals.forEach((goal, index) => {
        const progress =
            goal.target > 0
                ? (goal.current / goal.target) * 100
                : 0;

        const card = document.createElement("article");

        card.className = "feature-card";

        card.innerHTML = `
      <div class="feature-icon">🌱</div>

      <h3>${goal.name}</h3>
      <p><strong>Deadline:</strong> ${goal.deadline || "Not Set"}</p>
      <p>${goal.current} / ${goal.target}</p>
      <p>${Math.round(progress)}% Complete</p>
      <progress
        value="${goal.current}"
        max="${goal.target}">
      </progress>

      <button onclick="updateGoal(${index})">
        + Progress
      </button>

      ${progress >= 100
                ? '<p class="goal-badge">🏆 Achievement Unlocked!</p>'
                : ''
            }
    `;

        if (progress >= 100) {
            completedCount++;
            completedGoalsContainer.appendChild(card);
        } else {
            activeCount++;
            activeGoalsContainer.appendChild(card);
        }
    });
    const totalGoals = goals.length;

    const completionRate =
        totalGoals > 0
            ? Math.round((completedCount / totalGoals) * 100)
            : 0;

    const activeCountEl = document.getElementById("active-count");
    const completedCountEl = document.getElementById("completed-count");
    const completionRateEl = document.getElementById("completion-rate");

    if (activeCountEl) activeCountEl.textContent = activeCount;
    if (completedCountEl) completedCountEl.textContent = completedCount;
    if (completionRateEl) completionRateEl.textContent = `${completionRate}%`;
}

function updateGoal(index) {
    goals[index].current = Math.min(
        goals[index].current + 10,
        goals[index].target
    );

    saveGoals();

    renderGoals();
}

addGoalBtn.addEventListener("click", () => {
    const name =
        document.getElementById("goal-name").value.trim();

    const target =
        parseInt(
            document.getElementById("goal-target").value
        );
    const deadline =
        document.getElementById("goal-deadline").value;

    if (!name || isNaN(target) || target <= 0 || !deadline) {
        alert("Please fill all fields.");
        return;
    }
    goals.push({
        name,
        target,
        deadline,
        current: 0
    });

    document.getElementById("goal-name").value = "";
    document.getElementById("goal-target").value = "";
    document.getElementById("goal-deadline").value = "";

    saveGoals();
    renderGoals();
});

renderGoals();