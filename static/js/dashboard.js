const recommendationList = document.getElementById("career-recommendations");
const recommendationButton = document.getElementById("recommendation-toggle");

if (recommendationList && recommendationButton) {
    recommendationButton.addEventListener("click", function () {
        const isVisible = recommendationButton.getAttribute("aria-expanded") === "true";
        recommendationButton.setAttribute("aria-expanded", String(!isVisible));
        recommendationButton.textContent = isVisible
            ? "Show career ideas"
            : "Hide career ideas";
        recommendationList.hidden = isVisible;
    });
}
