const recommendationList = document.getElementById("career-recommendations");
const recommendationButton = document.getElementById("recommendation-toggle");

if (recommendationList && recommendationButton) {
    recommendationButton.addEventListener("click", () => {
        const isVisible = recommendationButton.getAttribute("aria-expanded") === "true";
        recommendationButton.setAttribute("aria-expanded", String(!isVisible));
        recommendationButton.textContent = isVisible
            ? "Show career ideas"
            : "Hide career ideas";
        recommendationList.hidden = isVisible;
    });
}

const aiRecommendationForm = document.querySelector("[data-ai-form]");

if (aiRecommendationForm) {
    aiRecommendationForm.addEventListener("submit", () => {
        const button = aiRecommendationForm.querySelector("button[type='submit']");
        if (!button) return;

        button.disabled = true;
        button.setAttribute("aria-busy", "true");
        button.textContent = button.dataset.loadingLabel || "Building your plan...";
    });
}
