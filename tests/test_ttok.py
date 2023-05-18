from click.testing import CliRunner
from ttok.cli import cli
import pytest


@pytest.mark.parametrize(
    "args,expected,expected_tokens",
    (
        (["one"], "1\n", "606"),
        (["one", "two"], "2\n", "606 1403"),
        (["boo", "hello", "there", "this", "is"], "5\n", "34093 24748 1070 420 374"),
        (
            ["boo", "hello", "there", "this", "is", "-m", "gpt2"],
            "6\n",
            "2127 78 23748 612 428 318",
        ),
    ),
)
def test_ttok_count_and_tokens(args, expected, expected_tokens):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, args)
        assert result.exit_code == 0
        assert result.output == expected
        # Now with --tokens
        result2 = runner.invoke(cli, args + ["--tokens"])
        assert result2.exit_code == 0
        assert result2.output.strip() == expected_tokens


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
