import click
import sys
import tiktoken


@click.command()
@click.version_option()
@click.argument("prompt", nargs=-1)
@click.option("-i", "--input", "input", type=click.File("r"))
@click.option(
    "-t", "--truncate", "truncate", type=int, help="Truncate to this many tokens"
)
@click.option("-m", "--model", default="gpt-3.5-turbo", help="Which model to use")
@click.option("output_tokens", "--tokens", is_flag=True, help="Output token integers")
def cli(prompt, input, truncate, model, output_tokens):
    """
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
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError as e:
        raise click.ClickException(f"Invalid model: {model}") from e
    if not prompt and input is None:
        input = sys.stdin
    text = " ".join(prompt)
    if input is not None:
        input_text = input.read()
        if text:
            text = input_text + " " + text
        else:
            text = input_text
    # Tokenize it
    tokens = encoding.encode(text)
    if truncate:
        tokens = tokens[:truncate]

    if output_tokens:
        click.echo(" ".join(str(t) for t in tokens))
    elif truncate:
        click.echo(encoding.decode(tokens), nl=False)
    else:
        click.echo(len(tokens))
