((*- extends 'article.tplx' -*))

% See http://blog.juliusschulz.de/blog/ultimate-ipython-notebook#templates
% for some useful tips

%===============================================================================
% Document class
%===============================================================================

((* block docclass *))
\documentclass[11pt, twoside, a4paper]{article}
((* endblock docclass *))

%===============================================================================
% Packages
%===============================================================================

((* block packages *))
\usepackage[T1]{fontenc}
\usepackage{graphicx}
\usepackage[breakable]{tcolorbox}
% We will generate all images so they have a width \maxwidth. This means
% that they will get their normal width if they fit onto the page, but
% are scaled down if they would overflow the margins.
\makeatletter
\def\maxwidth{\ifdim\Gin@nat@width>\linewidth\linewidth
\else\Gin@nat@width\fi}
\makeatother
\let\Oldincludegraphics\includegraphics

% propose delete%
% Ensure that by default, figures have no caption (until we provide a
% proper Figure object with a Caption API and a way to capture that
% in the conversion process - todo).
% \usepackage{caption}
% \DeclareCaptionLabelFormat{empty}{}
%\captionsetup{format=empty,aboveskip=0pt,belowskip=0pt}
% end - propose delete%

% float figure settings%
\usepackage{float}
\floatplacement{figure}{H}  % used to force figures for placement in text

\usepackage{adjustbox} % Used to constrain images to a maximum size
\usepackage{xcolor} % Allow colors to be defined
\usepackage{enumerate} % Needed for markdown enumerations to work
\usepackage{geometry} % Used to adjust the document margins
\usepackage{amsmath} % Equations
\usepackage{amssymb} % Equations
\usepackage{textcomp} % defines textquotesingle
% Hack from http://tex.stackexchange.com/a/47451/13684:
\AtBeginDocument{%
    \def\PYZsq{\textquotesingle}% Upright quotes in Pygmentized code
}
\usepackage{upquote} % Upright quotes for verbatim code
\usepackage{eurosym} % defines \euro
\usepackage[mathletters]{ucs} % Extended unicode (utf-8) support
\usepackage[utf8x]{inputenc} % Allow utf-8 characters in the tex document
\usepackage{fancyvrb} % verbatim replacement that allows latex
\usepackage{grffile} % extends the file name processing of package graphics
                     % to support a larger range
% The hyperref package gives us a pdf with properly built
% internal navigation ('pdf bookmarks' for the table of contents,
% internal cross-reference links, web links for URLs, etc.)
\usepackage{hyperref}
\usepackage{longtable} % longtable support required by pandoc >1.10
\usepackage{booktabs}  % table support for pandoc > 1.12.2
\usepackage[inline]{enumitem} % IRkernel/repr support (it uses the enumerate* environment)
\usepackage[normalem]{ulem} % ulem is needed to support strikethroughs (\sout)
                            % normalem makes italics be italics, not underlines
\usepackage{braket}
\usepackage{mathrsfs}   
\usepackage{natbib}    
\usepackage[document]{ragged2e}    
\usepackage{fontspec, unicode-math}    
\usepackage[greek,english]{babel}
\usepackage{xunicode}   
\usepackage{letltxmacro}
\setmonofont{LiberationMono}
\newcommand{\argmax}{\operatornamewithlimits{argmax}}
\newcommand{\argmin}{\operatornamewithlimits{argmin}}
\DeclareMathOperator{\col}{col}
\setlength{\parskip}{1.5ex plus0.5ex minus0.5ex}
\setlength{\parindent}{0pt}

\usepackage{letltxmacro}
% https://tex.stackexchange.com/q/88001/5764
\LetLtxMacro\oldttfamily\ttfamily
\DeclareRobustCommand{\ttfamily}{\oldttfamily\csname ttsize\endcsname}
\newcommand{\setttsize}[1]{\def\ttsize{#1}}%

\DeclareTextFontCommand{\texttt}{\ttfamily}

% renew commands %
% Set max figure width to be 80% of text width, for now hardcoded.
\renewcommand{\includegraphics}[1]{\begin{center}\Oldincludegraphics[width=.8\maxwidth]{#1}\end{center}}
\renewcommand \caption [2][]{} % removes captions from all figures
((* endblock packages *))

% Colors for the hyperref package
\definecolor{urlcolor}{rgb}{0,.145,.698}
\definecolor{linkcolor}{rgb}{.71,0.21,0.01}
\definecolor{citecolor}{rgb}{.12,.54,.11}

% ANSI colors
\definecolor{ansi-black}{HTML}{3E424D}
\definecolor{ansi-black-intense}{HTML}{282C36}
\definecolor{ansi-red}{HTML}{E75C58}
\definecolor{ansi-red-intense}{HTML}{B22B31}
\definecolor{ansi-green}{HTML}{00A250}
\definecolor{ansi-green-intense}{HTML}{007427}
\definecolor{ansi-yellow}{HTML}{DDB62B}
\definecolor{ansi-yellow-intense}{HTML}{B27D12}
\definecolor{ansi-blue}{HTML}{208FFB}
\definecolor{ansi-blue-intense}{HTML}{0065CA}
\definecolor{ansi-magenta}{HTML}{D160C4}
\definecolor{ansi-magenta-intense}{HTML}{A03196}
\definecolor{ansi-cyan}{HTML}{60C6C8}
\definecolor{ansi-cyan-intense}{HTML}{258F8F}
\definecolor{ansi-white}{HTML}{C5C1B4}
\definecolor{ansi-white-intense}{HTML}{A1A6B2}
\definecolor{ansi-default-inverse-fg}{HTML}{FFFFFF}
\definecolor{ansi-default-inverse-bg}{HTML}{000000}


% commands and environments needed by pandoc snippets
% extracted from the output of `pandoc -s`
\providecommand{\tightlist}{%
    \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\DefineVerbatimEnvironment{Highlighting}{Verbatim}{commandchars=\\\{\}}
% Add ',fontsize=\small' for more characters per line
\newenvironment{Shaded}{}{}
\newcommand{\KeywordTok}[1]{\textcolor[rgb]{0.00,0.44,0.13}{\textbf{{#1}}}}
\newcommand{\DataTypeTok}[1]{\textcolor[rgb]{0.56,0.13,0.00}{{#1}}}
\newcommand{\DecValTok}[1]{\textcolor[rgb]{0.25,0.63,0.44}{{#1}}}
\newcommand{\BaseNTok}[1]{\textcolor[rgb]{0.25,0.63,0.44}{{#1}}}
\newcommand{\FloatTok}[1]{\textcolor[rgb]{0.25,0.63,0.44}{{#1}}}
\newcommand{\CharTok}[1]{\textcolor[rgb]{0.25,0.44,0.63}{{#1}}}
\newcommand{\StringTok}[1]{\textcolor[rgb]{0.25,0.44,0.63}{{#1}}}
\newcommand{\CommentTok}[1]{\textcolor[rgb]{0.38,0.63,0.69}{\textit{{#1}}}}
\newcommand{\OtherTok}[1]{\textcolor[rgb]{0.00,0.44,0.13}{{#1}}}
\newcommand{\AlertTok}[1]{\textcolor[rgb]{1.00,0.00,0.00}{\textbf{{#1}}}}
\newcommand{\FunctionTok}[1]{\textcolor[rgb]{0.02,0.16,0.49}{{#1}}}
\newcommand{\RegionMarkerTok}[1]{{#1}}
\newcommand{\ErrorTok}[1]{\textcolor[rgb]{1.00,0.00,0.00}{\textbf{{#1}}}}
\newcommand{\NormalTok}[1]{{#1}}

% Additional commands for more recent versions of Pandoc
\newcommand{\ConstantTok}[1]{\textcolor[rgb]{0.53,0.00,0.00}{{#1}}}
\newcommand{\SpecialCharTok}[1]{\textcolor[rgb]{0.25,0.44,0.63}{{#1}}}
\newcommand{\VerbatimStringTok}[1]{\textcolor[rgb]{0.25,0.44,0.63}{{#1}}}
\newcommand{\SpecialStringTok}[1]{\textcolor[rgb]{0.73,0.40,0.53}{{#1}}}
\newcommand{\ImportTok}[1]{{#1}}
\newcommand{\DocumentationTok}[1]{\textcolor[rgb]{0.73,0.13,0.13}{\textit{{#1}}}}
\newcommand{\AnnotationTok}[1]{\textcolor[rgb]{0.38,0.63,0.69}{\textbf{\textit{{#1}}}}}
\newcommand{\CommentVarTok}[1]{\textcolor[rgb]{0.38,0.63,0.69}{\textbf{\textit{{#1}}}}}
\newcommand{\VariableTok}[1]{\textcolor[rgb]{0.10,0.09,0.49}{{#1}}}
\newcommand{\ControlFlowTok}[1]{\textcolor[rgb]{0.00,0.44,0.13}{\textbf{{#1}}}}
\newcommand{\OperatorTok}[1]{\textcolor[rgb]{0.40,0.40,0.40}{{#1}}}
\newcommand{\BuiltInTok}[1]{{#1}}
\newcommand{\ExtensionTok}[1]{{#1}}
\newcommand{\PreprocessorTok}[1]{\textcolor[rgb]{0.74,0.48,0.00}{{#1}}}
\newcommand{\AttributeTok}[1]{\textcolor[rgb]{0.49,0.56,0.16}{{#1}}}
\newcommand{\InformationTok}[1]{\textcolor[rgb]{0.38,0.63,0.69}{\textbf{\textit{{#1}}}}}
\newcommand{\WarningTok}[1]{\textcolor[rgb]{0.38,0.63,0.69}{\textbf{\textit{{#1}}}}}


% Define a nice break command that doesn't care if a line doesn't already
% exist.
\def\br{\hspace*{\fill} \\* }
% Math Jax compatibility definitions
\def\gt{>}
\def\lt{<}
\let\Oldtex\TeX
\let\Oldlatex\LaTeX
\renewcommand{\TeX}{\textrm{\Oldtex}}
\renewcommand{\LaTeX}{\textrm{\Oldlatex}

%===============================================================================
% Title Page
%===============================================================================

((* block maketitle *))
\setttsize{\footnotesize}

\title{((( nb.metadata.get("latex_metadata", {}).get("title", "") | escape_latex )))}

((*- if nb.metadata.get("latex_metadata", {}).get("author", ""): -*))
\author{((( nb.metadata["latex_metadata"]["author"] )))}
((*- endif *))

((*- if nb.metadata.get("latex_metadata", {}).get("affiliation", ""): -*))
\affiliation{((( nb.metadata["latex_metadata"]["affiliation"] )))}
((*- endif *))

\date{\today}
\maketitle

((*- if nb.metadata.get("latex_metadata", {}).get("logo", ""): -*))
\begin{center}
   \adjustimage{max size={0.6\linewidth}{0.6\paperheight}}{((( nb.metadata["latex_metadata"]["logo"] )))}
\end{center}
((*- endif -*))

((* endblock maketitle *))


%===============================================================================
% Input
%===============================================================================

% Input cells can be hidden using the "Hide input" and "Hide input all"
% nbextensions (which set the hide_input metadata flags)

((* block input scoped *))
((( cell.metadata.get("hide_input", "") )))
((*- if cell.metadata.hide_input or nb.metadata.hide_input or cell.metadata.get("hide_input", ""): -*))
((*- else -*))
   ((( custom_add_prompt(cell.source | wrap_text(88) | highlight_code(strip_verbatim=True), cell, 'In ', 'incolor', 'plain') )))
((*- endif *))
((* endblock input *))


%===============================================================================
% Output
%===============================================================================

((* block output_group -*))
((*- if cell.metadata.hide_output: -*))
((*- else -*))
    ((( super() )))
((*- endif -*))
((* endblock output_group *))

((* block execute_result scoped *))
    ((*- for type in output.data | filter_data_type -*))
        ((*- if type in ['text/plain']*))
            ((( custom_add_prompt(output.data['text/plain'] | wrap_text(88) | escape_latex | ansi2latex, cell, 'Out', 'outcolor', 'plain') )))
        ((*- elif type in ['text/latex']*))
            ((( custom_add_prompt(output.data['text/latex'] | wrap_text(88) | ansi2latex, cell, 'Out', 'outcolor', 'latex') )))
        ((* else -*))
            ((( " " )))
            ((( draw_prompt(cell, 'Out', 'outcolor','') )))((( super() )))
        ((*- endif -*))
    ((*- endfor -*))
((* endblock execute_result *))

% Display stream ouput with coloring
((* block stream *))
\begin{Verbatim}[commandchars=\\\{\}, fontsize=\footnotesize]
    ((( output.text | wrap_text(86) | escape_latex | ansi2latex )))
\end{Verbatim}
%((* endblock stream *))

%==============================================================================
% Define macro custom_add_prompt() (derived from add_prompt() macro in style_ipython.tplx)
%==============================================================================

((* macro custom_add_prompt(text, cell, prompt, prompt_color, type) -*))
    ((*- if cell.execution_count is defined -*))
    ((*- set execution_count = "" ~ (cell.execution_count | replace(None, " ")) -*))
    ((*- else -*))
    ((*- set execution_count = "" -*))
    ((*- endif -*))
    ((*- set indention =  " " * (execution_count | length + 7) -*))
\begin{Verbatim}[mathescape, commandchars=\\\{\}, fontsize=\small, xleftmargin=-3.9em]
((( text.replace('$$','').replace('$','') | add_prompts(first='{\color{' ~ prompt_color ~ '}' ~ prompt ~ '[{\\color{' ~ prompt_color ~ '}' ~ execution_count ~ '}]:} ', cont=indention) )))
\end{Verbatim}
((*- endmacro *))

%==============================================================================
% Support Macros
%==============================================================================

% Name: draw_prompt
% Purpose: Renders an output/input prompt
((* macro draw_prompt(cell, prompt, prompt_color, extra_space) -*))
    ((*- if cell.execution_count is defined -*))
    ((*- set execution_count = "" ~ (cell.execution_count | replace(None, " ")) -*))
    ((*- else -*))((*- set execution_count = " " -*))((*- endif *))

    ((*- if (resources.global_content_filter.include_output_prompt and prompt == 'Out')
         or (resources.global_content_filter.include_input_prompt  and prompt == 'In' ) *))
\prompt{(((prompt)))}{(((prompt_color)))}{(((execution_count)))}{(((extra_space)))}
    ((*- endif -*))
((*- endmacro *))


%==============================================================================
% Bibliography
%==============================================================================

% Insert citations in markdown as e.g.
%    <cite data-cite="DevoretS2013">[DevoretS2013]</cite>
% requires file references.bib in current directory (or the file set as "bib" in the latex_metadata)


((* block bibliography *))
((*- if nb.metadata.get("latex_metadata", {}).get("bib_include", ""): -*))
% Add a bibliography block to the postdoc
\bibliographystyle{plain}
\bibliography{((( nb.metadata.get("latex_metadata", {}).get("bib", "references") )))}
((*- endif -*))
((* endblock bibliography *))
