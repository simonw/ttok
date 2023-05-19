import click
import sys
import tiktoken
from itertools import zip_longest


@click.command()
@click.version_option()
@click.argument("prompt", nargs=-1)
@click.option("-i", "--input", "input", type=click.File("r"))
@click.option(
    "-t", "--truncate", "truncate", type=int, help="Truncate to this many tokens"
)
@click.option("-s", "--split", "split_file", type=click.Path(), help="Split input into multiple files")
@click.option("-m", "--model", default="gpt-3.5-turbo", help="Which model to use")
@click.option("output_tokens", "--tokens", is_flag=True, help="Output token integers")
def cli(prompt, input, truncate, split_file, model, output_tokens):
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

    if split_file and truncate:
        # Ensure the truncate value is valid
        if truncate <= 0:
            raise click.ClickException(f"Invalid truncate value: {truncate}")
        # Split the tokens into groups of the specified size
        chunks = grouper(tokens, truncate)
        # Write each chunk to a separate file
        for i, chunk in enumerate(chunks):
            with open(f"{split_file}.part{i}", "w") as f:
                chunk = [token for token in chunk if token is not None]
                decoded_chunk = encoding.decode(chunk)
                f.write(decoded_chunk)
        return  # Exit the function early, we don't need to do anything else in this case

    if truncate:
        tokens = tokens[:truncate]

    if output_tokens:
        click.echo(" ".join(str(t) for t in tokens))
    elif truncate:
        click.echo(encoding.decode(tokens), nl=False)
    else:
        click.echo(len(tokens))

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)
