function scrollToSection(sectionId) {

    const section = document.getElementById(sectionId);

    if (section) {
        section.scrollIntoView({
            behavior: "smooth"
        });
    }
}


function showProjectInfo() {

    alert(
        "Ready for Future helps you analyze your skills, " +
        "build a learning roadmap, and prepare for interviews."
    );
}


function showFeatureMessage(featureName) {

    alert(
        featureName +
        " will be available after you create your career profile."
    );
}