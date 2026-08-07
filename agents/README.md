# Tax-Calculator Agents

There are currently two AI-assisted agents that can facilitate
model-development work and model-use work.

Both require Claude Code and an Anthropic subscription to its LLMs
(like Sonnet and Opus).  The cheapest Pro subscription is likely to be
sufficient for most needs.  There are plans to experiment with using
Claude Code with free LLMs, but that work is in the future.

### Model-Development Agent

In the top-level Tax-Calculator repository folder with the taxcalc-dev
conda environment activated, execute this command:
```
(taxcalc-dev) Tax-Calculator> claude --model opus --effort medium
```
The model-development agent can do a wide variety of things for a
developer.  In particular, it has been supplied with a detailed
workflow for making a local **structural enhancement** (that is,
adding parameters, variables, logic, and tests) so that the model can
simulate a reform that the public version of the model cannot analyze.
Here is an [example](https://github.com/PSLmodels/Tax-Calculator/pull/3116).

### Model-Use Agent

The Tax-Calculator Assistant (TCA) is an agent the allows full use of
the model via an English conversation.  Details are [here](tca/README.md).
