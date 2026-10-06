document.querySelectorAll(".practice-card").forEach(function (card) {
    const answer = card.querySelector(".practice-answer");
    const wordCount = card.querySelector(".answer-count");
    const toggle = card.querySelector(".answer-toggle");
    const tip = card.querySelector(".answer-tip");

    answer.addEventListener("input", function () {
        const words = answer.value.trim().split(/\s+/).filter(Boolean);
        wordCount.textContent = `${words.length} words`;
    });

    toggle.addEventListener("click", function () {
        const isExpanded = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", String(!isExpanded));
        toggle.textContent = isExpanded
            ? "Hide answer tip"
            : "Show answer tip";
        tip.hidden = isExpanded;
    });
});
