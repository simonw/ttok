# ttok

[![PyPI](https://img.shields.io/pypi/v/ttok.svg)](https://pypi.org/project/ttok/)
[![Changelog](https://img.shields.io/github/v/release/simonw/ttok?include_prereleases&label=changelog)](https://github.com/simonw/ttok/releases)
[![Tests](https://github.com/simonw/ttok/workflows/Test/badge.svg)](https://github.com/simonw/ttok/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/ttok/blob/master/LICENSE)

Count and truncate text based on tokens

## Background

Large language models such as GPT-3.5 and GPT-4 work in terms of tokens.

This tool can count tokens, using OpenAI's [tiktoken](https://github.com/openai/tiktoken) library.

It can also truncate text to a specified number of tokens.

## Installation

Install this tool using `pip`:

    pip install ttok

## Counting tokens

Provide text as arguments to this tool to count tokens:

```bash
ttok Hello world
```
```
2
```
You can also pipe text into the tool:
```bash
echo -n "Hello world" -n | ttok
```
```
2
```
Here the `echo -n` option prevents echo from adding a newline - without that you would get a token count of 3.

To pipe in text and then append extra tokens from arguments, use the `-i -` option:

```bash
echo -n "Hello world" -n | ttok more text -i -
```
```
6
```
## Different models

By default, the tokenizer model for GPT-3.5 and GPT-4 is used.

To use the model for GPT-2 and GPT-3, add `--model gpt2`:

```bash
ttok boo Hello there this is -m gpt2
```
```
6
```
Compared to GPT-3.5:
```bash
ttok boo Hello there this is
```
```
5
```
Further model options are [documented here](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb).

## Truncating text

Use the `-t 10` or `--truncate 10` option to truncate text to a specified number of tokens:

```bash
ttok This is too many tokens -t 3
```
```
This is too
```

## Viewing tokens

The `--tokens` option can be used to view the integer token IDs for the incoming text:

```bash
ttok Hello world --tokens
```
```
9906 1917
```

## ttok --help

<!-- [[[cog
import cog
from ttok import cli
from click.testing import CliRunner
runner = CliRunner()
result = runner.invoke(cli.cli, ["--help"])
help = result.output.replace("Usage: cli", "Usage: ttok")
cog.out(
    "```\n{}\n```".format(help)
)
]]] -->
```
Usage: ttok [OPTIONS] [PROMPT]...

  Count and truncate text based on tokens

  To count tokens for text passed as arguments:

      ttok one two three

  To count tokens from stdin:

      cat input.txt | ttok

  To truncate to 100 tokens:

      cat input.txt | ttok -t 100

  To truncate to 100 tokens using the gpt2 model:

      cat input.txt | ttok -t 100 -m gpt2

  To view tokens:

      cat input.txt | ttok --tokens

Options:
  --version               Show the version and exit.
  -i, --input FILENAME
  -t, --truncate INTEGER  Truncate to this many tokens
  -m, --model TEXT        Which model to use
  --tokens                Output token integers
  --help                  Show this message and exit.

```
<!-- [[[end]]] -->

You can also run this command using:

```bash
python -m ttok --help
```

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

```bash
cd ttok
python -m venv venv
source venv/bin/activate
```

Now install the dependencies and test dependencies:

```bash
pip install -e '.[test]'
```

To run the tests:

```bash
pytest
```
