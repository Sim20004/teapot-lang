
"use strict";

const LOG_PREFIX = "[TeapotLang Playground]";
const TEAPOT_PYODIDE =
  "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/";
const TEAPOT_REPOSITORY = "Sim20004/teapot-lang";
const TEAPOT_BRANCH = "main";
const PYTHON_SOURCE_ROOT = "/teapot/src";

const log = (...args) => console.info(LOG_PREFIX, ...args);
const logError = (...args) => console.error(LOG_PREFIX, ...args);

const makeElement = (tag, className, text) => {
  const element = document.createElement(tag);

  if (className) element.className = className;
  if (text !== undefined) element.textContent = String(text);

  return element;
};

const renderValue = (value) => {
  if (value === null || value === undefined) return "None";

  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }

  if (typeof value === "object") {
    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  }

  return String(value);
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

  headers.forEach((header) => appendCell(headingRow, header, true));

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

const describeError = (error) => {
  if (error instanceof Error) {
    return `${error.name}: ${error.message}`;
  }

  return String(error);
};

const fetchJSON = async (url) => {
  log("Fetching JSON:", url);

  const response = await fetch(url);

  log("HTTP response:", {
    url,
    status: response.status,
    ok: response.ok,
  });

  if (!response.ok) {
    const body = await response.text().catch(() => "");
    throw new Error(
      `HTTP ${response.status} fetching ${url}: ${body.slice(0, 300)}`,
    );
  }

  const body = await response.text();

  try {
    return JSON.parse(body);
  } catch (error) {
    throw new Error(
      `Expected JSON from ${url}, received: ` +
      `${body.slice(0, 200)}. ${describeError(error)}`,
    );
  }
};

const loadPyodideScript = async () => {
  if (typeof window.loadPyodide === "function") return;

  if (!window.teapotPyodideScriptLoading) {
    window.teapotPyodideScriptLoading = new Promise(
      (resolve, reject) => {
        const script = document.createElement("script");

        script.src = `${TEAPOT_PYODIDE}pyodide.js`;
        script.async = true;

        script.addEventListener("load", resolve, { once: true });
        script.addEventListener(
          "error",
          () => reject(new Error("Could not load the Pyodide script.")),
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
  if (window.teapotCompiler) return window.teapotCompiler;

  if (!window.teapotCompilerLoading) {
    window.teapotCompilerLoading = (async () => {
      log("Finding the current repository commit.");

      const reference = await fetchJSON(
        `https://api.github.com/repos/${TEAPOT_REPOSITORY}` +
        `/git/ref/heads/${TEAPOT_BRANCH}`,
      );

      const commit = reference?.object?.sha;

      if (!commit) {
        throw new Error("GitHub did not return a commit SHA.");
      }

      log("Using repository commit:", commit);

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
        throw new Error("Could not find src/teapot/web.py in the repository.");
      }

      log("Python files discovered:", files.length);

      await loadPyodideScript();

      log("Initialising Pyodide.");

      const pyodide = await window.loadPyodide({
        indexURL: TEAPOT_PYODIDE,
      });

      log("Pyodide initialised:", {
        version: pyodide.version,
        pythonVersion: pyodide.runPython("import sys; sys.version"),
      });

      // Create the source root and every package directory.
      pyodide.FS.mkdirTree(PYTHON_SOURCE_ROOT);

      for (const file of files) {
        const relativePath = file.path.slice("src/".length);
        const destination = `${PYTHON_SOURCE_ROOT}/${relativePath}`;
        const directory = destination.slice(
          0,
          destination.lastIndexOf("/"),
        );

        pyodide.FS.mkdirTree(directory);
      }

      log(
        "Package directories created:",
        pyodide.FS.readdir(`${PYTHON_SOURCE_ROOT}/teapot`),
      );

      // Download every module from the same immutable commit.
      const results = await Promise.all(
        files.map(async (file) => {
          const url =
            `https://raw.githubusercontent.com/${TEAPOT_REPOSITORY}/` +
            `${commit}/${file.path}`;

          log("Downloading:", file.path);

          const response = await fetch(url);

          if (!response.ok) {
            throw new Error(
              `HTTP ${response.status} downloading ${file.path}`,
            );
          }

          const content = await response.text();

          if (content.length === 0) {
            throw new Error(`Downloaded an empty Python file: ${file.path}`);
          }

          return {
            repositoryPath: file.path,
            path:
              `${PYTHON_SOURCE_ROOT}/` +
              file.path.slice("src/".length),
            content,
          };
        }),
      );

      log("All Python files downloaded:", results.length);

      // IMPORTANT: write into /teapot/src/teapot, not /teapot/teapot.
      for (const file of results) {
        try {
          pyodide.FS.writeFile(file.path, file.content);
        } catch (error) {
          throw new Error(
            `Could not write ${file.repositoryPath} to ${file.path}: ` +
            describeError(error),
          );
        }
      }

      const webModulePath = `${PYTHON_SOURCE_ROOT}/teapot/web.py`;
      const initPath = `${PYTHON_SOURCE_ROOT}/teapot/__init__.py`;

      const filesystemCheck = {
        count: results.length,
        webModuleExists: pyodide.FS.analyzePath(webModulePath).exists,
        initFileExists: pyodide.FS.analyzePath(initPath).exists,
      };

      log("Python filesystem check:", filesystemCheck);

      if (
        !filesystemCheck.webModuleExists ||
        !filesystemCheck.initFileExists
      ) {
        throw new Error(
          "The TeapotLang package files are missing from the Pyodide filesystem.",
        );
      }

      // Configure Python's module search path and verify the import.
      await pyodide.runPythonAsync(`
import sys
sys.path.insert(0, ${JSON.stringify(PYTHON_SOURCE_ROOT)})

import teapot.web
print("TeapotLang module loaded from:", teapot.web.__file__)
      `);

      log("TeapotLang compiler imported successfully.");

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

    const isObject = value !== null && typeof value === "object";
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
      } else {
        appendNode(children, child, key, depth + 1);
      }
    }

    if (children.children.length > 0) item.append(children);
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
  if (
    !data ||
    !Array.isArray(data.tokens) ||
    !data.ast ||
    !Array.isArray(data.symbols)
  ) {
    throw new Error(
      `Compiler returned an unexpected result: ${renderValue(data)}`,
    );
  }

  renderTokens(outputs.tokens, data.tokens);
  renderAST(outputs.ast, data.ast);
  renderSymbols(outputs.symbols, data.symbols);

  Object.values(outputs).forEach(clearError);
};

const compileSource = async (pyodide, source) => {
  log("Compiling source:", {
    characters: source.length,
    preview: source.slice(0, 120),
  });

  pyodide.globals.set("teapot_source", source);

  let pythonResult;

  try {
    // Return the Python dictionary directly. Avoid JSON serialisation and
    // JSON.parse(), which can fail if the result is not a JSON string.
    pythonResult = await pyodide.runPythonAsync(`
from teapot.web import compile_source
compile_source(teapot_source)
    `);

    if (
      pythonResult === null ||
      typeof pythonResult?.toJs !== "function"
    ) {
      throw new Error(
        "Pyodide did not return a Python dictionary proxy. " +
        `Received ${typeof pythonResult}: ${String(pythonResult)}`,
      );
    }

    const result = pythonResult.toJs({
      dict_converter: Object.fromEntries,
    });

    log("Compiler result converted:", {
      tokens: result.tokens?.length,
      hasAST: result.ast !== undefined,
      symbols: result.symbols?.length,
      memoryMode: result.memory_mode,
    });

    return result;
  } catch (error) {
    logError("Python compilation failed:", error);
    throw error;
  } finally {
    if (pythonResult && typeof pythonResult.destroy === "function") {
      pythonResult.destroy();
    }

    pyodide.globals.delete("teapot_source");
  }
};

const initialisePlayground = (compiler) => {
  log("Initialising playground element:", compiler);

  const source = compiler.querySelector("textarea");
  const button = compiler.querySelector(".preview-button");
  const stage = compiler.querySelector(".compile-stage");

  if (!source || !button || !stage) {
    logError("Playground is missing its textarea, button or compile stage.");
    return;
  }

  const outputs = Object.fromEntries(
    [...compiler.querySelectorAll(".compiler-output")].map(
      (element) => [element.dataset.output, element],
    ),
  );

  if (!outputs.tokens || !outputs.ast || !outputs.symbols) {
    stage.textContent = "Invalid playground markup";
    logError("Expected tokens, ast and symbols compiler-output elements.");
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
    log("Compile button clicked.");

    button.disabled = true;
    stage.textContent = "Loading compiler...";

    Object.values(outputs).forEach((output) => {
      clearError(output);
      output.replaceChildren();
    });

    try {
      const pyodide = await loadTeapotCompiler();

      stage.textContent = "Compiling...";

      const result = await compileSource(pyodide, source.value);

      renderResult(outputs, result);

      stage.textContent = `${renderValue(result.memory_mode)} / complete`;
      log("Compilation completed successfully.");
    } catch (error) {
      const message = describeError(error);

      appendError(outputs.tokens, message);
      stage.textContent = "Compilation failed";

      logError("Playground compilation failed:", error);
    } finally {
      button.disabled = false;
    }
  });
};

const initialisePlaygrounds = () => {
  const playgrounds = document.querySelectorAll("[data-compiler]");

  log("Found playgrounds:", playgrounds.length);

  playgrounds.forEach(initialisePlayground);
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initialisePlaygrounds, {
    once: true,
  });
} else {
  initialisePlaygrounds();
}
