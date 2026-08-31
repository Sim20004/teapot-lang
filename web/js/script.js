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
const GITHUB_OWNER = "Sim20004";
const GITHUB_REPO = "teapot-lang";

const GITHUB_API = "https://api.github.com";

const GITHUB_API_VERSION = "2022-11-28";

const GITHUB_PER_PAGE = 100;

/*
 * This is deliberately fixed.

 * GitHub does NOT determine who is a maintainer.
 * To add a maintainer, change this list manually.
 */
const MAINTAINERS = new Set([
  "Sim20004"
]);


/*
 * GitHub's public API allows unauthenticated requests,
 * but those requests are rate limited.
 *
 * Do not put a personal GitHub token in this frontend.
 */
const githubHeaders = {
  Accept: "application/vnd.github+json",
  "X-GitHub-Api-Version": GITHUB_API_VERSION
};


/*
 * Small helper for safely creating text nodes.
 *
 * We don't insert usernames, names, bios, etc. directly
 * into HTML. GitHub data is external input.
 */
function createTextElement(tag, text, className = "") {
  const element = document.createElement(tag);

  if (className) {
    element.className = className;
  }

  element.textContent = text ?? "";

  return element;
}


/*
 * Format numbers using the user's locale.
 *
 * 1234 -> 1,234
 */
function formatNumber(value) {
  if (!Number.isFinite(value)) {
    return "0";
  }

  return new Intl.NumberFormat("en-GB").format(value);
}


/*
 * Fetch JSON from GitHub.
 *
 * We explicitly handle rate limiting because this is
 * one of the most likely API failures for a public site.
 */
async function githubFetch(endpoint) {
  const response = await fetch(`${GITHUB_API}${endpoint}`, {
    headers: githubHeaders,
    cache: "no-store"
  });

  if (response.status === 403 || response.status === 429) {
    const remaining = response.headers.get("X-RateLimit-Remaining");

    if (remaining === "0" || response.status === 429) {
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


/*
 * Fetch all contributor pages.
 *
 * This means the site doesn't silently stop at the first
 * 100 contributors.
 */
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


/*
 * Create the basic structure shared by maintainer and
 * contributor cards.
 */
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

  /*
   * If GitHub's avatar ever fails, don't leave a broken-image
   * icon as the entire visual identity.
   */
  avatar.addEventListener("error", () => {
    avatar.removeAttribute("src");
    avatar.alt = "";
  }, { once: true });

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

  const summaryText = createTextElement(
    "p",
    summary
  );

  summaryContainer.appendChild(summaryText);


  const stats = document.createElement("div");
  stats.className = "person-stats";

  const stat1 = createStat(
    commits,
    "Commits"
  );

  const stat2 = createStat(
    stat2Value,
    stat2Label
  );

  const stat3 = createStat(
    stat3Value,
    stat3Label
  );

  stats.append(
    stat1,
    stat2,
    stat3
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

  const contributionItem = createTextElement(
    "li",
    contributionText
  );

  contributionList.appendChild(contributionItem);

  contributionContainer.append(
    contributionTitle,
    contributionList
  );


  const footer = document.createElement("div");
  footer.className = "person-footer";

  const footerText = createTextElement(
    "span",
    "View GitHub profile"
  );

  const arrow = createTextElement(
    "span",
    "→",
    "person-arrow"
  );

  footer.append(
    footerText,
    arrow
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


/*
 * Create an individual statistic.
 */
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

  stat.append(
    valueElement,
    labelElement
  );

  return stat;
}


/*
 * Load the fixed maintainer list.
 *
 * Important:
 *
 * The list of maintainers comes from MAINTAINERS above.
 * GitHub is only used to retrieve their public profile
 * information and repository contribution count.
 */
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
          item.login?.toLowerCase() === username.toLowerCase()
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

        /*
         * These are deliberately profile-level details rather
         * than pretending they are TeapotLang statistics.
         */
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


/*
 * Render contributors.

 * No additional API request is made for every contributor.
 *
 * This is important because the contributor endpoint already
 * provides:
 *
 * - username
 * - avatar
 * - profile URL
 * - contribution count
 */
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
          maintainer.toLowerCase() === username.toLowerCase()
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

      commits: contributor.contributions,

      /*
       * The contributor endpoint doesn't provide public
       * repository/follower counts, so don't make another
       * request just to fill those fields.
       */
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


/*
 * Show an error without taking down the rest of the page.
 */
function showPeopleError(error) {
  console.error(
    "Failed to load GitHub people information:",
    error
  );

  const contributors = document.getElementById(
    "contributors"
  );

  const maintainers = document.getElementById(
    "maintainers"
  );

  const errorElement = document.getElementById(
    "contributors-error"
  );


  if (maintainers) {
    maintainers.replaceChildren();

    const message = document.createElement("div");

    message.className = "person-loading";

    message.textContent =
      "GitHub information is currently unavailable.";

    maintainers.appendChild(message);
  }


  if (contributors) {
    contributors.replaceChildren();

    const message = document.createElement("div");

    message.className = "person-loading";

    if (
      error instanceof Error &&
      error.message.includes("rate limit")
    ) {
      message.textContent =
        "GitHub's API rate limit has been reached. Please try again later.";
    } else {
      message.textContent =
        "Contributor information is currently unavailable.";
    }

    contributors.appendChild(message);
  }


  if (errorElement) {
    errorElement.textContent =
      "Contributor information is loaded directly from GitHub and may be temporarily unavailable.";
    
    errorElement.hidden = false;
  }
}


/*
 * Main entry point.
 */
async function loadPeople() {
  try {
    const contributors = await fetchAllContributors();

    /*
     * Render contributors immediately from the repository
     * endpoint. Only the maintainer needs a separate profile
     * request.
     */
    loadContributors(contributors);

    await loadMaintainers(contributors);
  } catch (error) {
    showPeopleError(error);
  }
}


/*
 * Start after the DOM exists.
 */
document.addEventListener(
  "DOMContentLoaded",
  loadPeople
);
        