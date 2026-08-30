const TEAPOT_PYODIDE =
    "https://cdn.jsdelivr.net/pyodide/v0.27.7/full/"

const TEAPOT_SOURCE =
    "https://raw.githubusercontent.com/Sim20004/teapot-lang/main/src/teapot/"

const TEAPOT_MODULES = [
    "debug.py",
    "lexer.py",
    "parser.py",
    "semantic.py",
    "teapot_ast.py",
    "tokens.py",
    "web.py",
]


const escapeText = (value) => {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;")
}


const loadTeapotCompiler = async () => {
    if (window.teapotCompiler) {
        return window.teapotCompiler
    }

    if (!window.teapotCompilerLoading) {
        window.teapotCompilerLoading = (async () => {

            const script = document.createElement("script")
            script.src = `${TEAPOT_PYODIDE}pyodide.js`
            document.head.append(script)

            await new Promise((resolve, reject) => {
                script.addEventListener(
                    "load",
                    resolve,
                    { once: true }
                )

                script.addEventListener(
                    "error",
                    reject,
                    { once: true }
                )
            })


            const pyodide = await window.loadPyodide({
                indexURL: TEAPOT_PYODIDE,
            })


            pyodide.FS.mkdirTree(
                "/teapot/src/teapot"
            )

            pyodide.FS.writeFile(
                "/teapot/src/teapot/__init__.py",
                ""
            )


            await Promise.all(
                TEAPOT_MODULES.map(async (module) => {

                    const response = await fetch(
                        `${TEAPOT_SOURCE}${module}`
                    )

                    if (!response.ok) {
                        throw new Error(
                            `Could not load compiler module ${module} from GitHub`
                        )
                    }

                    pyodide.FS.writeFile(
                        `/teapot/src/teapot/${module}`,
                        await response.text()
                    )
                })
            )


            pyodide.runPython(
                "import sys; sys.path.insert(0, '/teapot/src')"
            )

            return pyodide
        })()
    }

    window.teapotCompiler =
        await window.teapotCompilerLoading

    return window.teapotCompiler
}


const renderValue = (value) => {
    if (value === null) {
        return "None"
    }

    if (typeof value === "boolean") {
        return value ? "true" : "false"
    }

    if (typeof value === "object") {
        return JSON.stringify(value)
    }

    return String(value)
}


const appendTree = (
    parent,
    value,
    label = null,
    depth = 0
) => {

    const item = document.createElement("li")

    const row = document.createElement("div")
    row.className = "ast-row"

    const title =
        label === null
            ? (value?.node ?? "Program")
            : label


    row.innerHTML =
        `<span class="ast-branch">` +
        `${depth ? "├─" : ""}` +
        `</span>` +
        `<strong>${escapeText(title)}</strong>`


    if (
        value === null ||
        typeof value !== "object"
    ) {

        row.insertAdjacentHTML(
            "beforeend",
            `<span class="ast-value">` +
            `${escapeText(renderValue(value))}` +
            `</span>`
        )

        item.append(row)
        parent.append(item)

        return
    }


    item.append(row)


    const children =
        document.createElement("ul")


    Object.entries(value).forEach(
        ([key, child]) => {

            if (Array.isArray(child)) {

                child.forEach(
                    (entry, index) => {

                        appendTree(
                            children,
                            entry,
                            `${key}[${index}]`,
                            depth + 1
                        )
                    }
                )

            } else {

                appendTree(
                    children,
                    child,
                    key,
                    depth + 1
                )
            }
        }
    )


    if (children.children.length) {
        item.append(children)
    }

    parent.append(item)
}


const renderTokens = (
    container,
    tokens
) => {

    container.replaceChildren()

    const table =
        document.createElement("table")

    table.innerHTML =
        `<thead>` +
        `<tr>` +
        `<th>#</th>` +
        `<th>Type</th>` +
        `<th>Value</th>` +
        `<th>Position</th>` +
        `</tr>` +
        `</thead>`


    const body =
        document.createElement("tbody")


    tokens.forEach(
        (token, index) => {

            const row =
                document.createElement("tr")


            row.innerHTML =
                `<td>${index + 1}</td>` +
                `<td>` +
                `<span class="token-type">` +
                `${escapeText(token.type)}` +
                `</span>` +
                `</td>` +
                `<td>` +
                `${escapeText(renderValue(token.value))}` +
                `</td>` +
                `<td>` +
                `${token.line}:${token.col}` +
                `</td>`


            body.append(row)
        }
    )


    table.append(body)
    container.append(table)
}


const renderSymbols = (
    container,
    symbols
) => {

    container.replaceChildren()

    const table =
        document.createElement("table")


    table.innerHTML =
        `<thead>` +
        `<tr>` +
        `<th>Name</th>` +
        `<th>Kind</th>` +
        `<th>Type</th>` +
        `<th>Scope</th>` +
        `</tr>` +
        `</thead>`


    const body =
        document.createElement("tbody")


    symbols.forEach(
        (symbol) => {

            const row =
                document.createElement("tr")


            row.innerHTML =
                `<td>${escapeText(symbol.name)}</td>` +
                `<td>${escapeText(symbol.kind)}</td>` +
                `<td>${escapeText(renderValue(symbol.type))}</td>` +
                `<td>${escapeText(symbol.scope)}</td>`


            body.append(row)
        }
    )


    table.append(body)
    container.append(table)
}


document
    .querySelectorAll("[data-compiler]")
    .forEach((compiler) => {

        const source =
            compiler.querySelector("textarea")

            source.addEventListener("keydown", (event) => {
            if (event.key !== "Tab") return

            event.preventDefault()

            const start = source.selectionStart
            const end = source.selectionEnd

        source.value =
            source.value.substring(0, start) +
            "    " +
            source.value.substring(end)

            source.selectionStart = start + 4
            source.selectionEnd = start + 4
        })

        const outputs =
            Object.fromEntries(
                [
                    ...compiler.querySelectorAll(
                        ".compiler-output"
                    )
                ].map(
                    (element) => [
                        element.dataset.output,
                        element
                    ]
                )
            )


        const stage =
            compiler.querySelector(
                ".compile-stage"
            )


        const button =
            compiler.querySelector(
                ".preview-button"
            )


        compiler
            .querySelectorAll(".compiler-tab")
            .forEach((tab) => {

                tab.addEventListener(
                    "click",
                    () => {

                        compiler
                            .querySelectorAll(
                                ".compiler-tab"
                            )
                            .forEach((item) => {

                                item.classList.toggle(
                                    "active",
                                    item === tab
                                )

                                item.setAttribute(
                                    "aria-selected",
                                    item === tab
                                        ? "true"
                                        : "false"
                                )
                            })


                        compiler
                            .querySelectorAll(
                                ".compiler-output"
                            )
                            .forEach((output) => {

                                output.hidden =
                                    output.dataset.output !==
                                    tab.dataset.view
                            })
                    }
                )
            })


        button.addEventListener(
            "click",
            async () => {

                button.disabled = true

                stage.textContent =
                    "loading compiler..."


                Object.values(outputs)
                    .forEach((output) => {

                        output.classList.remove(
                            "error"
                        )

                        output.replaceChildren()
                    })


                try {

                    const pyodide =
                        await loadTeapotCompiler()


                    stage.textContent =
                        "compiling..."


                    pyodide.globals.set(
                        "teapot_source",
                        source.value
                    )


                    const result =
                        await pyodide.runPythonAsync(
                            "import json; " +
                            "json.dumps(" +
                            "__import__(" +
                            "'teapot.web', " +
                            "fromlist=['compile_source']" +
                            ")" +
                            ".compile_source(" +
                            "teapot_source" +
                            ")" +
                            ")"
                        )


                    const data =
                        JSON.parse(result)


                    renderTokens(
                        outputs.tokens,
                        data.tokens
                    )


                    const tree =
                        document.createElement("ul")

                    tree.className =
                        "ast-tree"


                    appendTree(
                        tree,
                        data.ast
                    )


                    outputs.ast.replaceChildren(
                        tree
                    )


                    renderSymbols(
                        outputs.symbols,
                        data.symbols
                    )


                    stage.textContent =
                        `${data.memory_mode} / complete`

                } catch (error) {

                    outputs.tokens.classList.add(
                        "error"
                    )

                    outputs.tokens.textContent =
                        error.message


                    stage.textContent =
                        "failed"

                } finally {

                    button.disabled = false
                }
            }
        )
    })