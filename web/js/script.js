document.addEventListener("DOMContentLoaded", () => {
    loadLatestVersion();
});

async function loadLatestVersion() {
    const badge = document.querySelector("#version-badge");

    if (!badge) {
        console.error("Could not find .version-badge");
        return;
    }

    try {
        const response = await fetch(
            "https://api.github.com/repos/Sim20004/teapot-lang/releases"
        );

        if (!response.ok) {
            throw new Error(`GitHub API returned ${response.status}`);
        }

        const releases = await response.json();

        if (!releases.length) {
            badge.textContent = "No releases";
            return;
        }

        // GitHub returns releases newest first.
        const latest = releases[0];

        badge.textContent = latest.tag_name;
        badge.title = latest.name || latest.tag_name;
        badge.href = latest.html_url;

    } catch (error) {
        console.error("Failed to fetch latest TeapotLang release:", error);
        badge.textContent = "version unavailable";
    }
}