import click
import re
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
@click.option(
    "encode_tokens", "--encode", is_flag=True, help="Output token integers"
)
@click.option(
    "decode_tokens", "--decode", is_flag=True, help="Convert token integers to text"
)
@click.option("as_tokens", "--tokens", is_flag=True, help="Output full tokens")
@click.option("--allow-special", is_flag=True, help="Do not error on special tokens")
def cli(
    prompt,
    input,
    truncate,
    model,
    encode_tokens,
    decode_tokens,
    as_tokens,
    allow_special,
):
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

    To view token integers:

        cat input.txt | ttok --encode

    To convert tokens back to text:

        ttok 9906 1917 --decode

    To see the details of the tokens:

        ttok "hello world" --tokens

    Outputs:

        [b'hello', b' world']
    """
    if decode_tokens and encode_tokens:
        raise click.ClickException("Cannot use --decode with --encode")
    if allow_special and not (encode_tokens or as_tokens):
        raise click.ClickException(
            "Cannot use --allow-special without --encode or --tokens"
        )
    if as_tokens and not decode_tokens and not encode_tokens:
        encode_tokens = True
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

    if decode_tokens:
        tokens = [int(token) for token in re.findall(r"\d+", text)]
        if as_tokens:
            click.echo(encoding.decode_tokens_bytes(tokens))
        else:
            click.echo(encoding.decode(tokens))
        return

    # Tokenize it
    kwargs = {}
    if allow_special:
        kwargs["allowed_special"] = "all"
    try:
        tokens = encoding.encode(text, **kwargs)
    except ValueError as ex:
        ex_str = str(ex)
        if "disallowed special token" in ex_str and not allow_special:
            # Just the first line, then add a hint
            ex_str = (
                ex_str.split("\n")[0]
                + "\n\nUse --allow-special to allow special tokens"
            )
        raise click.ClickException(ex_str)
    if truncate:
        tokens = tokens[:truncate]

    if encode_tokens:
        if as_tokens:
            click.echo(encoding.decode_tokens_bytes(tokens))
        else:
            click.echo(" ".join(str(t) for t in tokens))
    elif truncate:
        click.echo(encoding.decode(tokens), nl=False)
    else:
        click.echo(len(tokens))
