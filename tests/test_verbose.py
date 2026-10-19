from click.testing import CliRunner
import pytest

from ttok.cli import cli


@pytest.mark.parametrize(
    "args,input_text,stdout,stderr",
    (
        (
            ["one two three", "-t", "2"],
            None,
            "one two",
            "Truncated from 3 to 2 tokens.\n",
        ),
        (["one two", "-t", "2"], None, "one two", "No truncation: 2 tokens.\n"),
        (["one two", "-t", "3"], None, "one two", "No truncation: 2 tokens.\n"),
        (["-t", "2"], "", "", "No truncation: 0 tokens.\n"),
        (["-t", "2"], "one two three", "one two", "Truncated from 3 to 2 tokens.\n"),
        (
            ["three", "-i", "-", "-t", "2"],
            "one two",
            "one two",
            "Truncated from 3 to 2 tokens.\n",
        ),
        (
            ["私は学生です", "-t", "2"],
            None,
            "私は学生",
            "Truncated from 3 to 2 tokens.\n",
        ),
        (
            ["私は学生です", "-m", "gpt-3.5-turbo", "-t", "2"],
            None,
            "私は",
            "Truncated from 5 to 2 tokens.\n",
        ),
        (
            ["hello <|endoftext|> world", "--allow-special", "-t", "3"],
            None,
            "hello <|endoftext|>",
            "Truncated from 4 to 3 tokens.\n",
        ),
        (
            ["one two three", "-t", "2", "--encode"],
            None,
            "690 1920\n",
            "Truncated from 3 to 2 tokens.\n",
        ),
        (
            ["one two three", "-t", "2", "--tokens"],
            None,
            "[b'one', b' two']\n",
            "Truncated from 3 to 2 tokens.\n",
        ),
        # Negative limits retain the existing slicing behavior.
        (
            ["one two three", "-t", "-1"],
            None,
            "one two",
            "Truncated from 3 to 2 tokens.\n",
        ),
    ),
)
def test_verbose_truncation(args, input_text, stdout, stderr):
    runner = CliRunner()
    result = runner.invoke(cli, args + ["--verbose"], input=input_text)
    assert result.exit_code == 0
    assert result.stdout == stdout
    assert result.stderr == stderr

    quiet = runner.invoke(cli, args, input=input_text)
    assert quiet.exit_code == 0
    assert quiet.stdout == stdout
    assert quiet.stderr == ""


def test_verbose_file(tmp_path):
    source = tmp_path / "input.txt"
    source.write_text("one two three", encoding="utf-8")
    result = CliRunner().invoke(cli, ["-i", str(source), "-t", "2", "-v"])
    assert result.exit_code == 0
    assert result.stdout == "one two"
    assert result.stderr == "Truncated from 3 to 2 tokens.\n"


@pytest.mark.parametrize(
    "args",
    (
        ["one two"],
        ["one two", "--encode"],
        ["690 1920", "--decode", "-t", "1"],
        ["--list-models"],
        # Zero currently disables truncation; --verbose must not change that.
        ["one two", "-t", "0"],
        ["<|endoftext|>", "-t", "1"],
        ["one", "--encode", "--decode"],
    ),
)
def test_verbose_preserves_non_truncating_commands_and_errors(args):
    runner = CliRunner()
    quiet = runner.invoke(cli, args)
    verbose = runner.invoke(cli, args + ["--verbose"])
    assert verbose.exit_code == quiet.exit_code
    assert verbose.stdout == quiet.stdout
    assert verbose.stderr == quiet.stderr
