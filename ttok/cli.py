import click
import json
import sys
import tiktoken


@click.command()
@click.version_option()
@click.argument("prompt", nargs=-1)
@click.option("-i", "--input", "input", type=click.File("r"))
@click.option(
    "-t", "--truncate", "truncate", type=int, help="Truncate to this many tokens"
)
@click.option("--split", is_flag=True, help="Split text based on truncate argument")
@click.option(
    "-0", "--null", is_flag=True, help="Output split text with null byte delimiters"
)
@click.option("-m", "--model", default="gpt-3.5-turbo", help="Which model to use")
@click.option("output_tokens", "--tokens", is_flag=True, help="Output token integers")
def cli(prompt, input, truncate, split, null, model, output_tokens):
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
    if split and not truncate:
        raise click.ClickException("Cannot use --split without --truncate")
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

    if split:
        if null:
            # Filter out null byte tokens
            null_token = encoding.encode("\0")[0]
            tokens = [t for t in tokens if t != null_token]
        token_chunks = list(chunks(tokens, truncate))
        if null:
            click.echo(
                "\0".join(encoding.decode(chunk) for chunk in token_chunks) + "\0"
            )
        else:
            if output_tokens:
                click.echo(json.dumps(token_chunks, indent=2))
            else:
                click.echo(
                    json.dumps(
                        [encoding.decode(chunk) for chunk in token_chunks], indent=2
                    )
                )
        return

    if truncate:
        tokens = tokens[:truncate]

    if output_tokens:
        click.echo(" ".join(str(t) for t in tokens))
    elif truncate:
        click.echo(encoding.decode(tokens), nl=False)
    else:
        click.echo(len(tokens))


def chunks(sequence, n):
    for i in range(0, len(sequence), n):
        yield sequence[i : i + n]
