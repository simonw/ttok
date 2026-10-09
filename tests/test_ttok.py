from click.testing import CliRunner
from ttok.cli import cli
import pytest
import tiktoken


@pytest.mark.parametrize(
    "args,model,expected_length,expected_tokens",
    (
        (["one"], None, 1, "690"),
        (["one", "two"], None, 2, "690 1920"),
        (["boo", "hello", "there", "this", "is"], None, 5, "119137 40617 1354 495 382"),
        (["私は学生です"], None, 3, "158341 52770 15121"),
        (["私は学生です"], "gpt-5", 3, "158341 52770 15121"),
        (["私は学生です"], "gpt-3.5-turbo", 5, "86127 15682 48864 21990 38641"),
        (
            ["boo", "hello", "there", "this", "is"],
            "gpt2",
            6,
            "2127 78 23748 612 428 318",
        ),
    ),
)
def test_ttok_count_and_tokens(args, model, expected_length, expected_tokens):
    runner = CliRunner()
    model_args = ["-m", model] if model else []
    result = runner.invoke(cli, args + model_args)
    assert result.exit_code == 0
    assert int(result.output.strip()) == expected_length
    # Now with --encode
    result2 = runner.invoke(cli, args + model_args + ["--encode"])
    assert result2.exit_code == 0
    assert result2.output.strip() == expected_tokens

    # And try round-tripping it through --decode/--encode
    as_text = runner.invoke(cli, model_args + ["--decode"], input=expected_tokens)
    assert as_text.exit_code == 0
    assert as_text.output.strip() == " ".join(args)
    as_tokens_again = runner.invoke(
        cli, model_args + ["--encode"], input=as_text.output.strip()
    )
    assert as_tokens_again.exit_code == 0
    assert as_tokens_again.output.strip() == expected_tokens


@pytest.mark.parametrize(
    "args,expected",
    (
        (["hello", "world", "--encode"], "24912 2375"),
        (["24912", "2375", "--decode"], "hello world"),
        (["hello", "world", "--encode", "--tokens"], "[b'hello', b' world']"),
        (["24912", "2375", "--decode", "--tokens"], "[b'hello', b' world']"),
        (["hello", "world", "--tokens"], "[b'hello', b' world']"),
        # $ ttok --encode --tokens 私は学生です
        # [b'\xe7\xa7\x81\xe3\x81\xaf', b'\xe5\xad\xa6\xe7\x94\x9f', b'\xe3\x81\xa7\xe3\x81\x99']
        (
            ["--encode", "--tokens", "私は学生です"],
            "[b'\\xe7\\xa7\\x81\\xe3\\x81\\xaf', b'\\xe5\\xad\\xa6\\xe7\\x94\\x9f', b'\\xe3\\x81\\xa7\\xe3\\x81\\x99']",
        ),
        # $ ttok --encode 私は学生です
        # 158341 52770 15121
        (
            ["--encode", "私は学生です"],
            "158341 52770 15121",
        ),
        # $ ttok --decode 158341 52770 15121
        # 私は学生です
        (
            [b"158341", b"52770", b"15121", "--decode", "--tokens"],
            "[b'\\xe7\\xa7\\x81\\xe3\\x81\\xaf', b'\\xe5\\xad\\xa6\\xe7\\x94\\x9f', b'\\xe3\\x81\\xa7\\xe3\\x81\\x99']",
        ),
    ),
)
def test_ttok_decode_encode_tokens(args, expected):
    runner = CliRunner()
    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    assert result.output.strip() == expected


@pytest.mark.parametrize(
    "args,expected_text,expected_tokens",
    (
        (["私は学生です"], "私は学生", "158341 52770"),
        (["私は学生です", "-m", "gpt-5"], "私は学生", "158341 52770"),
        (["私は学生です", "-m", "gpt-3.5-turbo"], "私は", "86127 15682"),
        (["boo", "hello", "there", "-m", "gpt2"], "boo", "2127 78"),
    ),
)
def test_ttok_truncate(args, expected_text, expected_tokens):
    runner = CliRunner()
    result = runner.invoke(cli, args + ["-t", "2"])
    assert result.exit_code == 0
    assert result.output == expected_text
    encoded = runner.invoke(cli, args + ["-t", "2", "--encode"])
    assert encoded.exit_code == 0
    assert encoded.output.strip() == expected_tokens


@pytest.mark.parametrize("use_stdin", (True, False))
@pytest.mark.parametrize("use_extra_args", (True, False))
def test_ttok_file(use_stdin, use_extra_args, tmp_path):
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
        input_path = tmp_path / "input.txt"
        input_path.write_text(file_input, encoding="utf-8")
        args.extend(["-i", str(input_path)])

    runner = CliRunner()
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
    assert result.output.strip() == "199999"


def test_ttok_special_tokens_count_and_truncate():
    # https://github.com/simonw/ttok/issues/17
    runner = CliRunner()
    # Counting without --allow-special raises an error
    result = runner.invoke(cli, ["hello <|endoftext|> world"])
    assert result.exit_code != 0
    assert "Use --allow-special to allow special tokens" in result.output
    # Counting with --allow-special works
    result = runner.invoke(cli, ["hello <|endoftext|> world", "--allow-special"])
    assert result.exit_code == 0
    assert result.output.strip() == "4"
    # Truncating with --allow-special works
    result = runner.invoke(
        cli, ["hello <|endoftext|> world", "--allow-special", "-t", "3"]
    )
    assert result.exit_code == 0
    assert result.output == "hello <|endoftext|>"


def test_ttok_list_models():
    # https://github.com/simonw/ttok/issues/18
    runner = CliRunner()
    result = runner.invoke(cli, ["--list-models"])
    assert result.exit_code == 0
    lines = result.output.strip().split("\n")
    assert lines == [
        f"{model} ({encoding})"
        for model, encoding in tiktoken.model.MODEL_TO_ENCODING.items()
    ]
    assert "gpt-4o (o200k_base)" in lines
