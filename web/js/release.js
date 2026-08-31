const GITHUB_API =
  "https://api.github.com";

const GITHUB_OWNER =
  "Sim20004";

const GITHUB_REPO =
  "teapot-lang";

const GITHUB_API_VERSION =
  "2022-11-28";


const githubHeaders = {
  Accept:
    "application/vnd.github+json",

  "X-GitHub-Api-Version":
    GITHUB_API_VERSION
};


async function githubFetch(endpoint) {
  const response = await fetch(
    `${GITHUB_API}${endpoint}`,
    {
      headers: githubHeaders,
      cache: "no-store"
    }
  );

  if (response.status === 403 ||
      response.status === 429) {

    const remaining =
      response.headers.get(
        "X-RateLimit-Remaining"
      );

    if (
      response.status === 429 ||
      remaining === "0"
    ) {
      throw new Error(
        "GitHub API rate limit exceeded."
      );
    }
  }

  if (!response.ok) {
    throw new Error(
      `GitHub API returned ${response.status} ${response.statusText}.`
    );
  }

  return response.json();
}


function getReleaseId() {
  const params =
    new URLSearchParams(
      window.location.search
    );

  return params.get("id");
}


function createElement(
  tag,
  text = "",
  className = ""
) {
  const element =
    document.createElement(tag);

  if (className) {
    element.className =
      className;
  }

  element.textContent =
    text;

  return element;
}


async function loadRelease() {
  const container =
    document.getElementById(
      "release-page"
    );

  const errorElement =
    document.getElementById(
      "release-error"
    );

  if (!container) {
    return;
  }


  const releaseId =
    getReleaseId();


  if (!releaseId) {
    container.replaceChildren();

    const message =
      createElement(
        "p",
        "No release was specified."
      );

    container.appendChild(
      message
    );

    return;
  }


  try {
    /*
     * Fetch the specific release.
     *
     * GitHub provides /releases/{id}, which means
     * we don't need to download every release.
     */

    const release =
      await githubFetch(
        `/repos/${GITHUB_OWNER}/${GITHUB_REPO}/releases/${encodeURIComponent(releaseId)}`
      );


    document.title =
      `${release.name || release.tag_name} | TeapotLang`;


    container.replaceChildren();


    /* Header */

    const header =
      document.createElement("header");

    header.className =
      "release-page-header";


    const eyebrow =
      createElement(
        "p",
        "Project release",
        "eyebrow"
      );


    const title =
      createElement(
        "h1",
        release.name ||
        release.tag_name ||
        "Unnamed release"
      );


    const metadata =
      document.createElement("div");

    metadata.className =
      "release-meta";


    const tag =
      document.createElement("code");

    tag.textContent =
      release.tag_name ||
      "unknown";


    const date =
      document.createElement("span");


    if (release.published_at) {
      const published =
        new Date(
          release.published_at
        );

      date.textContent =
        `Published ${published.toLocaleDateString("en-GB")}`;
    }


    metadata.append(
      tag,
      date
    );


    /* GitHub link */

    const github =
      document.createElement("a");

    github.className =
      "btn ghost";

    github.href =
      release.html_url;

    github.target =
      "_blank";

    github.rel =
      "noopener noreferrer";

    github.textContent =
      "View on GitHub ↗";


    header.append(
      eyebrow,
      title,
      metadata,
      github
    );


    container.appendChild(
      header
    );


    /* Release notes */

    const notes =
      document.createElement("article");

    notes.className =
      "release-notes-page";


    if (release.body) {
      /*
       * marked.parse() converts GitHub's Markdown
       * into HTML.
       *
       * The release body is coming from your own
       * GitHub repository, so this is appropriate
       * for your release-note page.
       */

      notes.innerHTML =
        marked.parse(
          release.body
        );
    } else {
      notes.appendChild(
        createElement(
          "p",
          "This release does not contain release notes."
        )
      );
    }


    container.appendChild(
      notes
    );


    /* Downloads */

    if (
      Array.isArray(release.assets) &&
      release.assets.length > 0
    ) {
      const downloads =
        document.createElement(
          "section"
        );

      downloads.className =
        "release-downloads";


      downloads.appendChild(
        createElement(
          "h2",
          "Downloads"
        )
      );


      for (
        const asset of release.assets
      ) {
        const row =
          document.createElement(
            "div"
          );

        row.className =
          "release-asset";


        const name =
          createElement(
            "strong",
            asset.name
          );


        const download =
          document.createElement(
            "a"
          );

        download.className =
          "btn ghost";

        download.href =
          asset.browser_download_url;

        download.target =
          "_blank";

        download.rel =
          "noopener noreferrer";

        download.textContent =
          "Download";


        row.append(
          name,
          download
        );


        downloads.appendChild(
          row
        );
      }


      container.appendChild(
        downloads
      );
    }


  } catch (error) {
    console.error(
      "Failed to load release:",
      error
    );

    container.replaceChildren();

    if (errorElement) {
      errorElement.hidden =
        false;

      errorElement.textContent =
        error instanceof Error &&
        error.message.includes(
          "rate limit"
        )
          ? "GitHub's API rate limit has been reached. Please try again later."
          : "Unable to load this release from GitHub right now.";
    }
  }
}


document.addEventListener(
  "DOMContentLoaded",
  loadRelease
);