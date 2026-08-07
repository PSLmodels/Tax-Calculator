# Tax-Calculator Assistant, TCA

TCA is an AI agent that enables conversational use of Tax-Calculator's CLI.
A useful question to ask at first-use of TCA is: What can you do?

TCA currently requires Claude Code and an Anthropic subscription to its
LLMs (like Sonnet and Opus).  The cheapest Pro subscription is likely
to be sufficient for most needs.  There are plans to experiment with
using Claude Code with free LLMs, but that work is in the future.

In order to use TCA, you must be running MacOS or Linux, and have
cloned the Tax-Calculator repository.  If on Windows, you can use
Microsoft's free [Windows Subsystem for
Linux](https://learn.microsoft.com/en-us/windows/wsl/) to install the
free Ubuntu Linux operating system, within which you can clone the
Tax-Calculator repository.

TCA is used from the terminal prompt.  Every time a terminal window is
opened for TCA work, execute the "conda activate taxcalc-dev" command
in order to get access to the CLI tool, `tc`.  You can check that `tc`
is available by executing the "tc --version" command.  If the `tc`
command is not found, move to the top-level folder of the
Tax-Calculator repository code tree (the one containng `Makefile`) and
execute the "make package" command to create the `tc` command.

TCA is used in a folder **outside** the Tax-Calculator repository
tree.  If you have already installed TCA in such a TCA-work folder,
move to that TCA-work folder and execute the "./tca-exec" command.

If you have not already created such a TCA-work folder, move to the
`agents/tca` folder in the Tax-Calculator repository tree and execute
the following command (where, for illustration, we assume your new
TCA-work folder name is `~/TCA/myproject`):
```
(taxcalc-dev) tca> ./install.sh ~/TCA/myproject
```

Follow the instructions written to the terminal screen.

If the install test fails or you have other problems using TCA, please
raise an issue [here](https://github.com/PSLmodels/Tax-Calculator/issues).
