const GITHUB_OWNER = "Sim20004";
const GITHUB_REPO = "teapot-lang";

const GITHUB_API = "https://api.github.com";
const GITHUB_API_VERSION = "2022-11-28";
const GITHUB_PER_PAGE = 100;

const MAINTAINERS = new Set([
  "Sim20004"
]);

const githubHeaders = {
  Accept: "application/vnd.github+json",
  "X-GitHub-Api-Version": GITHUB_API_VERSION
};


/* =========================================================
   General helpers
   ========================================================= */

function createTextElement(tag, text, className = "") {
  const element = document.createElement(tag);

  if (className) {
    element.className = className;
  }

  element.textContent = text ?? "";

  return element;
}


function formatNumber(value) {
  if (!Number.isFinite(value)) {
    return "0";
  }

  return new Intl.NumberFormat("en-GB").format(value);
}


function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];
  const exponent = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1
  );

  const value = bytes / Math.pow(1024, exponent);

  return `${value.toFixed(exponent === 0 ? 0 : 1)} ${units[exponent]}`;
}


/* =========================================================
   GitHub API
   ========================================================= */

async function githubFetch(endpoint) {
  const response = await fetch(`${GITHUB_API}${endpoint}`, {
    headers: githubHeaders,
    cache: "no-store"
  });

  if (response.status === 403 || response.status === 429) {
    const remaining = response.headers.get("X-RateLimit-Remaining");

    if (response.status === 429 || remaining === "0") {
      throw new Error("GitHub API rate limit exceeded.");
    }
  }

  if (!response.ok) {
    throw new Error(
      `GitHub API returned ${response.status} ${response.statusText}.`
    );
  }

  return response.json();
}


/* =========================================================
   Latest version
   ========================================================= */

function renderLatestVersion(releases) {
  const badge = document.querySelector("#version-badge");

  if (!badge) {
    return;
  }

  if (!Array.isArray(releases) || releases.length === 0) {
    badge.textContent = "No releases";
    badge.removeAttribute("href");
    return;
  }

  const latest = releases[0];

  badge.textContent = latest.tag_name || "Unknown";
  badge.title = latest.name || latest.tag_name || "";
  badge.href = latest.html_url || "#";
}


async function loadLatestVersion(releasesPromise) {
  const badge = document.querySelector("#version-badge");

  if (!badge) {
    return;
  }

  try {
    const releases = await releasesPromise;

    renderLatestVersion(releases);
  } catch (error) {
    console.error(
      "Failed to fetch latest TeapotLang release:",
      error
    );

    badge.textContent = "version unavailable";
    badge.removeAttribute("href");
  }
}


/* =========================================================
   Contributors
   ========================================================= */

async function fetchAllContributors() {
  const contributors = [];

  for (let page = 1; ; page += 1) {
    const endpoint =
      `/repos/${GITHUB_OWNER}/${GITHUB_REPO}` +
      `/contributors?per_page=${GITHUB_PER_PAGE}&page=${page}`;

    const batch = await githubFetch(endpoint);

    if (!Array.isArray(batch) || batch.length === 0) {
      break;
    }

    contributors.push(...batch);

    if (batch.length < GITHUB_PER_PAGE) {
      break;
    }
  }

  return contributors;
}


function createStat(value, label) {
  const stat = document.createElement("div");
  stat.className = "person-stat";

  const valueElement = createTextElement(
    "span",
    value,
    "stat-value"
  );

  const labelElement = createTextElement(
    "span",
    label,
    "stat-label"
  );

  stat.append(valueElement, labelElement);

  return stat;
}


function createPersonCard({
  username,
  displayName,
  avatarUrl,
  profileUrl,
  role,
  summary,
  commits,
  stat2Value,
  stat2Label,
  stat3Value,
  stat3Label,
  contributionText,
  maintainer = false
}) {
  const card = document.createElement("a");

  card.className = "person-card";

  if (maintainer) {
    card.classList.add("maintainer-card");
  }

  card.href = profileUrl;
  card.target = "_blank";
  card.rel = "noopener noreferrer";

  const top = document.createElement("div");
  top.className = "person-top";

  const avatar = document.createElement("img");

  avatar.className = "person-avatar";
  avatar.src = avatarUrl;
  avatar.alt = `${username}'s GitHub avatar`;
  avatar.loading = "lazy";
  avatar.referrerPolicy = "no-referrer";

  avatar.addEventListener(
    "error",
    () => {
      avatar.removeAttribute("src");
      avatar.alt = "";
    },
    { once: true }
  );

  const identity = document.createElement("div");
  identity.className = "person-identity";

  const name = createTextElement(
    "h4",
    displayName || username
  );

  const handle = createTextElement(
    "span",
    `@${username}`,
    "person-handle"
  );

  identity.append(name, handle);

  const roleElement = createTextElement(
    "span",
    role,
    "person-role"
  );

  if (!maintainer) {
    roleElement.classList.add("contributor-role");
  }

  top.append(
    avatar,
    identity,
    roleElement
  );


  const summaryContainer = document.createElement("div");
  summaryContainer.className = "person-summary";

  summaryContainer.appendChild(
    createTextElement("p", summary)
  );


  const stats = document.createElement("div");
  stats.className = "person-stats";

  stats.append(
    createStat(commits, "Commits"),
    createStat(stat2Value, stat2Label),
    createStat(stat3Value, stat3Label)
  );


  const contributionContainer = document.createElement("div");
  contributionContainer.className = "person-contributions";

  const contributionTitle = createTextElement(
    "span",
    maintainer
      ? "TeapotLang Contributions"
      : "Repository Contributions",
    "contribution-title"
  );

  const contributionList = document.createElement("ul");

  contributionList.appendChild(
    createTextElement("li", contributionText)
  );

  contributionContainer.append(
    contributionTitle,
    contributionList
  );


  const footer = document.createElement("div");
  footer.className = "person-footer";

  footer.append(
    createTextElement(
      "span",
      "View GitHub profile"
    ),
    createTextElement(
      "span",
      "→",
      "person-arrow"
    )
  );


  card.append(
    top,
    summaryContainer,
    stats,
    contributionContainer,
    footer
  );

  return card;
}


async function loadMaintainers(contributors) {
  const container = document.getElementById("maintainers");

  if (!container) {
    return;
  }

  container.replaceChildren();

  for (const username of MAINTAINERS) {
    try {
      const contributor = contributors.find(
        item =>
          item.login?.toLowerCase() ===
          username.toLowerCase()
      );

      const user = await githubFetch(
        `/users/${encodeURIComponent(username)}`
      );

      const commits = contributor?.contributions ?? 0;

      const card = createPersonCard({
        username: user.login,
        displayName: user.name || user.login,
        avatarUrl: user.avatar_url,
        profileUrl: user.html_url,
        role: "Maintainer",

        summary:
          user.bio ||
          "Creator and primary maintainer of TeapotLang.",

        commits,

        stat2Value: formatNumber(user.public_repos),
        stat2Label: "Public Repos",

        stat3Value: formatNumber(user.followers),
        stat3Label: "Followers",

        contributionText:
          "Language design, compiler architecture, lexer, parser, AST, semantic analysis, testing, and project infrastructure.",

        maintainer: true
      });

      container.appendChild(card);
    } catch (error) {
      console.error(
        `Unable to load maintainer ${username}:`,
        error
      );

      const fallback = document.createElement("div");

      fallback.className = "person-loading";

      fallback.textContent =
        `Unable to load maintainer information for @${username}.`;

      container.appendChild(fallback);
    }
  }
}


function loadContributors(contributors) {
  const container = document.getElementById("contributors");

  if (!container) {
    return;
  }

  container.replaceChildren();

  const visibleContributors = contributors.filter(
    contributor => {
      const username = contributor.login;

      if (!username) {
        return false;
      }

      return !Array.from(MAINTAINERS).some(
        maintainer =>
          maintainer.toLowerCase() ===
          username.toLowerCase()
      );
    }
  );

  if (visibleContributors.length === 0) {
    const empty = document.createElement("div");

    empty.className = "person-loading";

    empty.textContent =
      "No contributors other than the maintainers yet.";

    container.appendChild(empty);

    return;
  }

  for (const contributor of visibleContributors) {
    const username = contributor.login;

    const card = createPersonCard({
      username,

      displayName: username,

      avatarUrl: contributor.avatar_url,

      profileUrl: contributor.html_url,

      role: "Contributor",

      summary:
        "Contributor to TeapotLang through code, testing, documentation, or other project improvements.",

      commits: formatNumber(
        contributor.contributions
      ),

      stat2Value: "GitHub",
      stat2Label: "Profile",

      stat3Value: "Open",
      stat3Label: "Source",

      contributionText:
        `${formatNumber(contributor.contributions)} repository commit${contributor.contributions === 1 ? "" : "s"}.`
    });

    container.appendChild(card);
  }
}


function showPeopleError(error) {
  console.error(
    "Failed to load GitHub people information:",
    error
  );

  const contributors =
    document.getElementById("contributors");

  const maintainers =
    document.getElementById("maintainers");

  const errorElement =
    document.getElementById("contributors-error");


  const isRateLimited =
    error instanceof Error &&
    error.message.includes("rate limit");


  if (maintainers) {
    maintainers.replaceChildren();

    const message = document.createElement("div");

    message.className = "person-loading";

    message.textContent = isRateLimited
      ? "GitHub's API rate limit has been reached. Please try again later."
      : "GitHub information is currently unavailable.";

    maintainers.appendChild(message);
  }


  if (contributors) {
    contributors.replaceChildren();

    const message = document.createElement("div");

    message.className = "person-loading";

    message.textContent = isRateLimited
      ? "GitHub's API rate limit has been reached. Please try again later."
      : "Contributor information is currently unavailable.";

    contributors.appendChild(message);
  }


  if (errorElement) {
    errorElement.textContent =
      "Contributor information is loaded directly from GitHub and may be temporarily unavailable.";

    errorElement.hidden = false;
  }
}


async function loadPeople() {
  try {
    const contributors =
      await fetchAllContributors();

    loadContributors(contributors);

    await loadMaintainers(contributors);
  } catch (error) {
    showPeopleError(error);
  }
}


/* =========================================================
   Releases
   ========================================================= */

function renderReleases(releases) {
  const releasesList =
    document.getElementById("releases-list");

  const releasesError =
    document.getElementById("releases-error");

  if (!releasesList) {
    return;
  }

  releasesList.replaceChildren();

  if (releasesError) {
    releasesError.hidden = true;
  }

  if (!Array.isArray(releases) || releases.length === 0) {
    const empty = document.createElement("div");

    empty.className = "release-empty";
    empty.textContent =
      "No releases have been published yet.";

    releasesList.appendChild(empty);

    return;
  }

  for (const release of releases) {
    const article =
      document.createElement("article");

    article.className = "release release-compact";


    /* Release name */

    const title =
      document.createElement("h3");

    title.textContent =
      release.name ||
      release.tag_name ||
      "Unnamed release";


    /* Metadata */

    const metadata =
      document.createElement("div");

    metadata.className =
      "release-meta";


    const tag =
      document.createElement("code");

    tag.textContent =
      release.tag_name || "unknown";


    const published =
      document.createElement("span");

    if (release.published_at) {
      const date =
        new Date(release.published_at);

      published.textContent =
        `Published ${date.toLocaleDateString("en-GB")}`;
    }


    metadata.append(
      tag,
      published
    );


    /* Actions */

    const actions =
      document.createElement("div");

    actions.className =
      "release-actions";


    /*
     * Internal release notes page.
     *
     * We use the GitHub release ID because it is unique
     * and avoids putting the entire release object in
     * the URL.
     */

    const notesLink =
      document.createElement("a");

    notesLink.className =
      "btn primary";

    notesLink.href =
      `release.html?id=${encodeURIComponent(release.id)}`;

    notesLink.textContent =
      "Release notes →";


    /* GitHub */

    const githubLink =
      document.createElement("a");

    githubLink.className =
      "btn ghost";

    githubLink.href =
      release.html_url;

    githubLink.target =
      "_blank";

    githubLink.rel =
      "noopener noreferrer";

    githubLink.textContent =
      "GitHub ↗";


    actions.append(
      notesLink,
      githubLink
    );


    article.append(
      title,
      metadata,
      actions
    );

    releasesList.appendChild(
      article
    );
  }
}


async function loadReleases() {
  const releasesList =
    document.getElementById("releases-list");

  const releasesError =
    document.getElementById("releases-error");

  if (!releasesList) {
    return [];
  }

  try {
    const releases = await githubFetch(
      `/repos/${GITHUB_OWNER}/${GITHUB_REPO}/releases`
    );

    renderReleases(releases);

    return releases;
  } catch (error) {
    console.error(
      "Failed to load releases:",
      error
    );

    releasesList.replaceChildren();

    if (releasesError) {
      releasesError.hidden = false;

      releasesError.textContent =
        error instanceof Error &&
        error.message.includes("rate limit")
          ? "GitHub's API rate limit has been reached. Please try again later."
          : "Unable to load releases from GitHub right now.";
    }

    throw error;
  }
}


/* =========================================================
   Page startup
   ========================================================= */

document.addEventListener(
  "DOMContentLoaded",
  () => {
    /*
     * Start the releases request ONCE.
     *
     * Both the release section and version badge
     * use this same promise.
     */
    const releasesPromise =
      loadReleases();

    loadLatestVersion(
      releasesPromise
    );

    loadPeople();
  }
);