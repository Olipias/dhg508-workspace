#!/usr/bin/env python3
"""Generate the Overleaf main.tex from draft.md; regenerate the evidence table separately."""
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
CITES = {
    "chapman": r"\autocite[opening discussion]{chapman2012}",
    "mccall": r"\autocite[part I]{mccall2012}",
    "wang": r"\autocite[257--58, 266, 273]{wang2013}",
    "met": r"\autocite[Artwork Details]{met}",
    "unesco": r"\autocite[About the object]{unesco}",
}
ESC = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape_tex(text: str) -> str:
    return "".join(ESC.get(c, c) for c in text)


def format_code(code_str: str) -> str:
    escaped = escape_tex(code_str)
    escaped = escaped.replace(r"\_", r"\_\allowbreak{}").replace("/", r"/\allowbreak{}")
    return r"\texttt{" + escaped + "}"


def format_inline(text: str) -> str:
    tokens = re.split(r"(\[\^[a-z]+\]|`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)", text)
    out = []
    for tok in tokens:
        if not tok:
            continue
        if re.fullmatch(r"\[\^[a-z]+\]", tok):
            out.append(CITES[tok[2:-1]])
        elif tok.startswith("`") and tok.endswith("`"):
            out.append(format_code(tok[1:-1]))
        elif tok.startswith("**") and tok.endswith("**"):
            out.append(r"\textbf{" + format_inline(tok[2:-2]) + "}")
        elif tok.startswith("*") and tok.endswith("*"):
            out.append(r"\emph{" + format_inline(tok[1:-1]) + "}")
        else:
            out.append(escape_tex(tok))
    return "".join(out)


def render_block(paragraph: str) -> str:
    lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
    if all(re.match(r"^\d+\.\s+", line) for line in lines):
        items = [re.sub(r"^\d+\.\s+", "", line) for line in lines]
        rendered = ["\\begin{enumerate}"]
        for item in items:
            rendered.append("  \\item " + format_inline(item))
        rendered.append("\\end{enumerate}")
        return "\n".join(rendered)
    return format_inline(" ".join(lines))


source = (HERE / "draft.md").read_text(encoding="utf-8")
body = source[source.index("### Abstract"):source.index("[^met]:")]
sections = re.split(r"^## (\d+)\. (.+)$", body, flags=re.M)
abstract = sections[0].replace("### Abstract", "").strip()
parts = [
    r"\begin{abstract}",
    r"\noindent",
    render_block(abstract),
    r"\end{abstract}",
]

for index in range(1, len(sections), 3):
    number, heading, content = sections[index:index + 3]
    parts.append(r"\section{" + format_inline(heading) + "}")
    for paragraph in content.strip().split("\n\n"):
        parts.append(render_block(paragraph) + "\n")
    if number == "3":
        parts.append(r"""\begin{figure}[!htbp]
  \centering
  \includegraphics[width=0.92\textwidth]{schematic.png}
  \caption{Source review, scene control, deterministic simulation, and native verification modules.}
  \label{fig:schematic}
\end{figure}
""")
    if number == "4":
        parts.append(r"""\begin{table}[!htbp]
  \centering
  \scriptsize
  \setlength{\tabcolsep}{3.5pt}
  \renewcommand{\arraystretch}{1.22}
  \input{evidence-table.tex}
  \caption{Claims and design elements with locators, evidence tiers (据 documented, 推断 inferred, 设 invented), and limits.}
  \label{tab:evidence}
\end{table}
""")

preamble = r"""% ============================================================================
% DHG508 Final Design Paper & Post-Mortem (Overleaf Source)
% Lingnan University — Critical Digital History
%
% OVERLEAF SETUP:
%   1. Upload overleaf-final.zip (or overleaf-draft.zip) to Overleaf
%   2. Menu (top left) -> Compiler -> XeLaTeX
%   3. Click Recompile
% ============================================================================

\documentclass[11pt,a4paper]{article}

\usepackage{fontspec}
\IfFontExistsTF{Times New Roman}
  {\setmainfont{Times New Roman}}
  {\setmainfont{texgyretermes}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic]}

\usepackage{xeCJK}
\IfFontExistsTF{Noto Serif CJK SC}
  {\setCJKmainfont{Noto Serif CJK SC}\setCJKmonofont{Noto Serif CJK SC}}
  {\IfFontExistsTF{Songti SC}
    {\setCJKmainfont{Songti SC}\setCJKmonofont{Songti SC}}
    {\IfFontExistsTF{SimSun}
      {\setCJKmainfont{SimSun}\setCJKmonofont{SimSun}}
      {\setCJKmainfont{FandolSong-Regular.otf}\setCJKmonofont{FandolSong-Regular.otf}}}}

\usepackage[a4paper, margin=0.8in]{geometry}
\usepackage{setspace}
\usepackage{booktabs}
\usepackage{array}
\usepackage{graphicx}
\usepackage{csquotes}
\usepackage{microtype}

% Chicago Manual of Style 18th ed., Notes-Bibliography (BibLaTeX + Biber)
\usepackage[notes, backend=biber, autolang=other, isbn=false]{biblatex-chicago}
\addbibresource{references.bib}

\renewcommand{\footnotesize}{\fontsize{9}{11}\selectfont}
\usepackage{xurl}
\usepackage[hidelinks]{hyperref}
\setlength{\emergencystretch}{2.5em}
\setlength{\parskip}{0.14em}
\setstretch{1.01}

\title{\textbf{Playing with Uncertain Provenance}\\[0.25em]
\large Evidence Boundaries, Deterministic Rehearsal, and the Design of \emph{Thief Simulator}}
\author{Yutong Li\\Lingnan University $\cdot$ DHG508 Critical Digital History\\
\small Release Build: \texttt{v0.26.16} (Desktop Windows / Linux / macOS) $\cdot$ Repo: \url{https://github.com/Olipias/thief-sim}}
\date{25 November 2026}

\begin{document}
\maketitle
"""

ending = r"""\singlespacing
\printbibliography[title={Bibliography}]

\end{document}
"""

(HERE / "main.tex").write_text(
    "% Generated from draft.md by build_draft.py.\n" + preamble + "\n".join(parts) + ending,
    encoding="utf-8",
)
words = len(re.findall(r"\b[\w]+(?:[’-][\w]+)*\b", body))
print(f"Generated main.tex; body including abstract and headings: {words} words")
