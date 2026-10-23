
"use strict";

const TEAPOT_PYODIDE =
  "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";

const TEAPOT_REPOSITORY = "Sim20004/teapot-lang";
const TEAPOT_BRANCH = "main";
const TEAPOT_PACKAGE = "/teapot/src/teapot";

const escapeText = (value) => {
  const element = document.createElement("span");
  element.textContent = String(value);
  return element.textContent;
};

const renderValue = (value) => {
  if (value === null) return "None";

  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
};

const makeElement = (tag, className, text) => {
  const element = document.createElement(tag);

  if (className) element.className = className;
  if (text !== undefined) element.textContent = String(text);

  return element;
};

const appendCell = (row, value, header = false) => {
  const cell = makeElement(
    header ? "th" : "td",
    null,
    renderValue(value),
  );

  row.append(cell);
  return cell;
};

const makeTable = (headers) => {
  const table = makeElement("table");
  const thead = makeElement("thead");
  const headingRow = makeElement("tr");

  headers.forEach((header) => {
    appendCell(headingRow, header, true);
  });

  thead.append(headingRow);
  table.append(thead);
  table.append(makeElement("tbody"));

  return table;
};

const appendError = (container, message) => {
  container.replaceChildren(
    makeElement("code", "compiler-error", message),
  );
  container.classList.add("error");
};

const clearError = (container) => {
  container.classList.remove("error");
};

const fetchJSON = async (url) => {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(
      `Request failed (${response.status}): ${url}`,
    );
  }

  return response.json();
};

const loadPyodideScript = async () => {
  if (typeof window.loadPyodide === "function") {
    return;
  }

  if (!window.teapotPyodideScriptLoading) {
    window.teapotPyodideScriptLoading = new Promise(
      (resolve, reject) => {
        const script = document.createElement("script");

        script.src = `${TEAPOT_PYODIDE}pyodide.js`;
        script.async = true;

        script.addEventListener("load", resolve, { once: true });
        script.addEventListener(
          "error",
          () => reject(new Error("Could not load Pyodide.")),
          { once: true },
        );

        document.head.append(script);
      },
    ).catch((error) => {
      window.teapotPyodideScriptLoading = null;
      throw error;
    });
  }

  await window.teapotPyodideScriptLoading;
};

const loadTeapotCompiler = async () => {
  if (window.teapotCompiler) {
    return window.teapotCompiler;
  }

  if (!window.teapotCompilerLoading) {
    window.teapotCompilerLoading = (async () => {
      // Resolve main once, so every Python file comes from the same commit.
      const reference = await fetchJSON(
        `https://api.github.com/repos/${TEAPOT_REPOSITORY}` +
        `/git/ref/heads/${TEAPOT_BRANCH}`,
      );

      const commit = reference.object.sha;

      // Discover the package recursively instead of maintaining a module list.
      const tree = await fetchJSON(
        `https://api.github.com/repos/${TEAPOT_REPOSITORY}` +
        `/git/trees/${commit}?recursive=1`,
      );

      if (tree.truncated) {
        throw new Error(
          "GitHub truncated the repository tree; cannot safely load the package.",
        );
      }

      const files = tree.tree.filter(
        (entry) =>
          entry.type === "blob" &&
          entry.path.startsWith("src/teapot/") &&
          entry.path.endsWith(".py"),
      );

      if (!files.some((file) => file.path === "src/teapot/web.py")) {
        throw new Error("The TeapotLang browser entry point was not found.");
      }

      const pyodide = await (async () => {
        await loadPyodideScript();

        return window.loadPyodide({
          indexURL: TEAPOT_PYODIDE,
        });
      })();

      pyodide.FS.mkdirTree("/teapot/src");

      // Preserve the package's complete directory structure.
      for (const file of files) {
        const relativePath = file.path.slice("src/".length);
        const destination = `/teapot/src/${relativePath}`;
        const directory = destination.slice(
          0,
          destination.lastIndexOf("/"),
        );

        pyodide.FS.mkdirTree(directory);
      }

      // Fetch all files from the exact commit selected above.
      const results = await Promise.all(
        files.map(async (file) => {
          const url =
            `https://raw.githubusercontent.com/${TEAPOT_REPOSITORY}/` +
            `${commit}/${file.path}`;

          const response = await fetch(url);

          if (!response.ok) {
            throw new Error(
              `Could not load ${file.path} (${response.status}).`,
            );
          }

          return {
            path: `/teapot/${file.path.slice("src/".length)}`,
            content: await response.text(),
          };
        }),
      );

      for (const file of results) {
        pyodide.FS.writeFile(file.path, file.content);
      }

      pyodide.runPython(`
import sys
sys.path.insert(0, "/teapot/src")
      `);

      // Import once to catch missing dependencies before the user compiles.
      pyodide.runPython(`
import teapot.web
      `);

      return pyodide;
    })();

    window.teapotCompilerLoading.catch(() => {
      window.teapotCompilerLoading = null;
    });
  }

  window.teapotCompiler = await window.teapotCompilerLoading;

  return window.teapotCompiler;
};

const renderTokens = (container, tokens) => {
  const table = makeTable(["#", "Type", "Value", "Position"]);
  const body = table.querySelector("tbody");

  tokens.forEach((token, index) => {
    const row = makeElement("tr");

    appendCell(row, index + 1);

    const typeCell = appendCell(row, token.type);
    typeCell.classList.add("token-type");

    appendCell(row, token.value);
    appendCell(row, `${token.line}:${token.col}`);

    body.append(row);
  });

  container.replaceChildren(table);
};

const renderAST = (container, ast) => {
  const root = makeElement("ul", "ast-tree");

  const appendNode = (parent, value, label = null, depth = 0) => {
    const item = makeElement("li");
    const row = makeElement("div", "ast-row");

    const isObject =
      value !== null &&
      typeof value === "object";

    const title =
      label ?? (isObject ? value.node ?? "Program" : "Value");

    row.append(makeElement("span", "ast-branch", depth ? "├─" : ""));
    row.append(makeElement("strong", null, title));

    if (!isObject) {
      row.append(makeElement("span", "ast-value", renderValue(value)));
      item.append(row);
      parent.append(item);
      return;
    }

    item.append(row);

    const children = makeElement("ul");

    for (const [key, child] of Object.entries(value)) {
      if (Array.isArray(child)) {
        child.forEach((entry, index) => {
          appendNode(children, entry, `${key}[${index}]`, depth + 1);
        });
      } else if (child !== null && typeof child === "object") {
        appendNode(children, child, key, depth + 1);
      } else {
        appendNode(children, child, key, depth + 1);
      }
    }

    if (children.children.length > 0) {
      item.append(children);
    }

    parent.append(item);
  };

  appendNode(root, ast);
  container.replaceChildren(root);
};

const renderSymbols = (container, symbols) => {
  const table = makeTable(["Name", "Kind", "Type", "Scope"]);
  const body = table.querySelector("tbody");

  const appendSymbols = (entries, parentScope = "module") => {
    for (const symbol of entries) {
      const row = makeElement("tr");

      appendCell(row, symbol.name);
      appendCell(row, symbol.kind);
      appendCell(row, symbol.type);
      appendCell(row, symbol.scope ?? parentScope);

      body.append(row);

      if (Array.isArray(symbol.members)) {
        appendSymbols(symbol.members, symbol.name);
      }
    }
  };

  appendSymbols(symbols);
  container.replaceChildren(table);
};

const renderResult = (outputs, data) => {
  renderTokens(outputs.tokens, data.tokens);
  renderAST(outputs.ast, data.ast);
  renderSymbols(outputs.symbols, data.symbols);

  Object.values(outputs).forEach(clearError);
};

const compileSource = async (pyodide, source) => {
  pyodide.globals.set("teapot_source", source);

  try {
    const result = await pyodide.runPythonAsync(`
import json
from teapot.web import compile_source

json.dumps(compile_source(teapot_source))
    `);

    return JSON.parse(result);
  } finally {
    pyodide.globals.delete("teapot_source");
  }
};

const initialisePlayground = (compiler) => {
  const source = compiler.querySelector("textarea");
  const button = compiler.querySelector(".preview-button");
  const stage = compiler.querySelector(".compile-stage");

  if (!source || !button || !stage) {
    console.warn("TeapotLang playground is missing required elements.");
    return;
  }

  const outputs = Object.fromEntries(
    [...compiler.querySelectorAll(".compiler-output")].map(
      (element) => [element.dataset.output, element],
    ),
  );

  if (!outputs.tokens || !outputs.ast || !outputs.symbols) {
    stage.textContent = "invalid playground markup";
    return;
  }

  compiler.querySelectorAll(".compiler-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      compiler.querySelectorAll(".compiler-tab").forEach((item) => {
        const active = item === tab;

        item.classList.toggle("active", active);
        item.setAttribute("aria-selected", String(active));
      });

      Object.values(outputs).forEach((output) => {
        output.hidden = output.dataset.output !== tab.dataset.view;
      });
    });
  });

  source.addEventListener("keydown", (event) => {
    if (event.key !== "Tab") return;

    event.preventDefault();

    const start = source.selectionStart;
    const end = source.selectionEnd;

    source.setRangeText("    ", start, end, "end");
  });

  button.addEventListener("click", async () => {
    button.disabled = true;
    stage.textContent = "loading compiler...";

    Object.values(outputs).forEach((output) => {
      clearError(output);
      output.replaceChildren();
    });

    try {
      const pyodide = await loadTeapotCompiler();

      stage.textContent = "compiling...";

      const result = await compileSource(pyodide, source.value);

      renderResult(outputs, result);

      stage.textContent = `${renderValue(result.memory_mode)} / complete`;
    } catch (error) {
      const message = escapeText(error?.message ?? error);

      appendError(outputs.tokens, message);
      stage.textContent = "compilation failed";

      console.error("TeapotLang playground error:", error);
    } finally {
      button.disabled = false;
    }
  });
};

document.querySelectorAll("[data-compiler]").forEach(initialisePlayground);
