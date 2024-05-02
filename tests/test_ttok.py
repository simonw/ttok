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


@pytest.mark.parametrize(
    "args,expected",
    (
        (["hello", "world", "--encode"], "15339 1917"),
        (["15339", "1917", "--decode"], "hello world"),
        (["hello", "world", "--encode", "--tokens"], "[b'hello', b' world']"),
        (["15339", "1917", "--decode", "--tokens"], "[b'hello', b' world']"),
        (["hello", "world", "--tokens"], "[b'hello', b' world']"),
        # $ ttok --encode --tokens 私は学生です
        # [b'\xe7\xa7\x81', b'\xe3\x81\xaf', b'\xe5\xad\xa6', b'\xe7\x94\x9f', b'\xe3\x81\xa7\xe3\x81\x99']
        (
            ["--encode", "--tokens", "私は学生です"],
            "[b'\\xe7\\xa7\\x81', b'\\xe3\\x81\\xaf', b'\\xe5\\xad\\xa6', b'\\xe7\\x94\\x9f', b'\\xe3\\x81\\xa7\\xe3\\x81\\x99']",
        ),
        # $ ttok --encode 私は学生です
        # 86127 15682 48864 21990 38641
        (
            ["--encode", "私は学生です"],
            "86127 15682 48864 21990 38641",
        ),
        # $ ttok --decode 86127 15682 48864 21990 38641
        # 私は学生です
        (
            [b"86127", b"15682", b"48864", b"21990", b"38641", "--decode", "--tokens"],
            "[b'\\xe7\\xa7\\x81', b'\\xe3\\x81\\xaf', b'\\xe5\\xad\\xa6', b'\\xe7\\x94\\x9f', b'\\xe3\\x81\\xa7\\xe3\\x81\\x99']",
        ),
    ),
)
def test_ttok_decode_encode_tokens(args, expected):
    runner = CliRunner()
    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    assert result.output.strip() == expected


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


def test_ttok_special_tokens():
    # https://github.com/simonw/ttok/issues/13
    runner = CliRunner()
    # Without --allow-special raises an error
    result = runner.invoke(cli, ["<|endoftext|>", "--encode"])
    assert result.exit_code != 0
    assert "Use --allow-special to allow special tokens" in result.output
    # With --allow-special it works
    result = runner.invoke(cli, ["<|endoftext|>", "--encode", "--allow-special"])
    assert result.exit_code == 0
    assert result.output.strip() == "100257"
