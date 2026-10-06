const progressBar = document.querySelector(".learning-progress-bar");

if (progressBar) {
    const completed = Number(progressBar.dataset.completed);
    const total = Number(progressBar.dataset.total);
    const percent = total ? (completed / total) * 100 : 0;

    window.requestAnimationFrame(function () {
        progressBar.style.width = `${percent}%`;
    });
}
