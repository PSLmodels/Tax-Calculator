# Tax-Calculator Agents

There are currently two AI-assisted agents that can facilitate
model-development work and model-use work.  Both are optional.

Both require Claude Code and an Anthropic subscription to its LLMs
(like Sonnet and Opus).  The cheapest Pro subscription is likely to be
sufficient for most needs.  There are plans to experiment with using
Claude Code with free LLMs, but that work is in the future.

### Model-Development Agent

Move to the top-level Tax-Calculator repository folder (the one
containing `setup.py`) and activate the taxcalc-dev conda environment
(`conda activate taxcalc-dev`).  Then on the `local-enhancements` git
branch (`git switch local-enhancements` if it already exists, or `git
checkout -b local-enhancements` if it does not), execute this command:
```
(taxcalc-dev) Tax-Calculator> claude --model opus --effort medium
```
The model-development agent can do a wide variety of things for a
developer.  In particular, it has been supplied with a detailed
workflow for making a local, and therefore, private **structural
enhancement** (that is, adding parameters, variables, logic, and
tests) so that the local version of the model can simulate a reform
that the public version of the model cannot analyze.

It is important to use the phrase _structural enhancement_ in the
agent prompt.  And it is helpful if you set Claude's `auto mode` to
on.

Here are several examples:
 - [PR 3116](https://github.com/PSLmodels/Tax-Calculator/pull/3116) (Aug 2026)
 - [PR 3194](https://github.com/PSLmodels/Tax-Calculator/pull/3194) (Oct 2026)

After commiting the changes on the `local-enhancements` branch,
execute `make package` and then use the new local version of the model
via either the Python API, the CLI, or the Tax-Calculator Assistant
(see below).

### Model-Use Agent

The Tax-Calculator Assistant (TCA) is an agent the allows full use of
the model via an English conversation.  Details are [here](tca/README.md).
