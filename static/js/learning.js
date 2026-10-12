document.body.classList.add("js-enabled");

const feedback = document.querySelector("[data-learning-feedback]");

function showFeedback(message, isError = false) {
    if (!feedback) return;
    feedback.textContent = message;
    feedback.classList.toggle("feedback-error", isError);
}

function updateTaskStatus(taskKey, status) {
    document.querySelectorAll("[data-skill-card]").forEach((card) => {
        if (card.dataset.skillCard !== taskKey) return;

        card.classList.toggle("is-completed", status === "completed");
        const statusLabel = card.querySelector("[data-skill-status]");
        statusLabel.className = `skill-status status-${status}`;
        statusLabel.textContent = status === "completed"
            ? "Completed"
            : status === "in_progress"
                ? "In Progress"
                : "Recommended";

        const checkbox = card.querySelector("[data-task-checkbox]");
        if (checkbox) checkbox.checked = status === "completed";
    });

    document.querySelectorAll("[data-checklist-item]").forEach((item) => {
        if (item.dataset.checklistItem !== taskKey) return;
        const completed = status === "completed";
        item.classList.toggle("is-completed", completed);
        const checkbox = item.querySelector("[data-task-checkbox]");
        if (checkbox) checkbox.checked = completed;
        const label = item.querySelector("[data-checklist-status]");
        if (label) label.textContent = completed ? "Completed" : "To do";
    });

    document.querySelectorAll("[data-progress-form]").forEach((form) => {
        if (form.dataset.taskKey !== taskKey) return;
        const state = form.querySelector('input[name="state"]');
        if (state) state.value = status === "completed" ? "incomplete" : "completed";
    });
}

function updateProgress(data) {
    const count = document.querySelector("[data-progress-count]");
    const total = document.querySelector("[data-progress-total]");
    const percent = document.querySelector("[data-progress-percent]");
    const bar = document.querySelector("[data-progress-bar]");

    if (count) count.textContent = String(data.completed);
    if (total) total.textContent = String(data.total);
    if (percent) percent.textContent = `${data.percentage}%`;
    if (bar) {
        bar.setAttribute("aria-valuemax", String(data.total));
        bar.setAttribute("aria-valuenow", String(data.completed));
        const fill = bar.querySelector(".learning-progress-bar");
        if (fill) fill.style.width = `${data.percentage}%`;
    }
}

async function saveProgress(url, taskKey, state, form = null) {
    const body = form ? new FormData(form) : new FormData();
    body.set("state", state);

    const response = await fetch(url, {
        method: "POST",
        body,
        credentials: "same-origin",
        headers: {
            Accept: "application/json",
            "X-Requested-With": "XMLHttpRequest",
        },
    });

    let result;
    try {
        result = await response.json();
    } catch {
        throw new Error("Your session may have expired. Refresh the page and try again.");
    }
    if (!response.ok) {
        throw new Error(result.error || "Progress could not be saved. Please try again.");
    }

    updateTaskStatus(taskKey, result.status);
    updateProgress(result);
    showFeedback(result.message);
}

document.addEventListener("submit", async (event) => {
    const form = event.target.closest("[data-progress-form]");
    if (!form) return;

    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    const checkbox = form.querySelector("[data-task-checkbox]");
    const stateField = form.querySelector('input[name="state"]');
    const taskKey = form.dataset.taskKey;
    const state = stateField?.value
        || (checkbox?.checked ? "completed" : "incomplete");

    if (button) button.disabled = true;
    if (checkbox) checkbox.disabled = true;
    form.setAttribute("aria-busy", "true");

    try {
        await saveProgress(form.action, taskKey, state, form);
    } catch (error) {
        if (checkbox) checkbox.checked = state === "incomplete";
        showFeedback(error.message, true);
    } finally {
        if (button) button.disabled = false;
        if (checkbox) checkbox.disabled = false;
        form.removeAttribute("aria-busy");
    }
});

document.addEventListener("change", (event) => {
    const checkbox = event.target.closest("[data-task-checkbox]");
    if (!checkbox) return;
    const form = checkbox.closest("[data-progress-form]");
    if (!form) return;

    const state = form.querySelector('input[name="state"]');
    if (state) state.value = checkbox.checked ? "completed" : "incomplete";
    form.requestSubmit();
});

document.addEventListener("click", async (event) => {
    const startButton = event.target.closest("[data-start-task]");
    if (!startButton) return;
    if (startButton.dataset.saving === "true") return;

    const taskKey = startButton.dataset.startTask;
    const progressUrl = startButton.dataset.progressUrl;
    const card = document.querySelector(`[data-skill-card="${CSS.escape(taskKey)}"]`);
    const plan = card?.querySelector(".learning-plan");
    if (plan) plan.open = true;

    startButton.dataset.saving = "true";
    startButton.setAttribute("aria-busy", "true");
    startButton.setAttribute("aria-disabled", "true");
    try {
        await saveProgress(
            progressUrl,
            taskKey,
            startButton.dataset.state,
        );
    } catch (error) {
        showFeedback(error.message, true);
    } finally {
        delete startButton.dataset.saving;
        startButton.removeAttribute("aria-busy");
        startButton.removeAttribute("aria-disabled");
    }
});
