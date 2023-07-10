from click.testing import CliRunner
from ttok.cli import cli
import pytest


@pytest.mark.parametrize(
    "args,expected_length,expected_tokens",
    (
        (["one"], 1, "606"),
        (["one", "two"], 2, "606 1403"),
        (["boo", "hello", "there", "this", "is"], 5, "34093 24748 1070 420 374"),
        (
            ["boo", "hello", "there", "this", "is", "-m", "gpt2"],
            6,
            "2127 78 23748 612 428 318",
        ),
    ),
)
def test_ttok_count_and_tokens(args, expected_length, expected_tokens):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, args)
        assert result.exit_code == 0
        assert int(result.output.strip()) == expected_length
        # Now with --encode
        result2 = runner.invoke(cli, args + ["--encode"])
        assert result2.exit_code == 0
        assert result2.output.strip() == expected_tokens

        # And try round-tripping it through --decode/--encode
        as_text = runner.invoke(cli, ["--decode"], input=expected_tokens)
        assert as_text.exit_code == 0
        as_tokens_again = runner.invoke(cli, ["--encode"], input=as_text.output.strip())
        assert as_tokens_again.exit_code == 0
        assert as_tokens_again.output.strip() == expected_tokens


@pytest.mark.parametrize("use_stdin", (True, False))
@pytest.mark.parametrize("use_extra_args", (True, False))
def test_ttok_file(use_stdin, use_extra_args):
    file_input = "text from file"
    expected_count = 3
    args = []
    kwargs = {}
    if use_extra_args:
        args.extend(["one", "two"])
        expected_count += 2
    if use_stdin:
        kwargs["input"] = file_input
        if args:
            args.extend(["-i", "-"])
    else:
        args.extend(["-i", "input.txt"])

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("input.txt", "w") as f:
            f.write(file_input)
        result = runner.invoke(cli, args, **kwargs)
        assert result.exit_code == 0
        assert result.output.strip() == str(expected_count)
