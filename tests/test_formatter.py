from io import StringIO

import pytest
from unittest import mock

from snakefmt.formatter import Formatter
from snakefmt.parser.parser import Snakefile


def setup_formatter(snake: str):
    stream = StringIO(snake)
    smk = Snakefile(stream)
    return Formatter(smk)


def test_emptyInput_emptyOutput():
    formatter = setup_formatter("")

    actual = formatter.get_formatted()
    expected = ""

    assert actual == expected


class TestPythonFormatting:
    @mock.patch("snakefmt.formatter.Formatter.run_black_format_str", spec=True)
    def test_commented_snakemake_syntax_we_dont_format_but_black_does(
        self, mock_method
    ):
        """
        Tests this line triggers call to black formatting
        """
        formatter = setup_formatter("#configfile: 'foo.yaml'")

        actual = formatter.get_formatted()
        mock_method.assert_called_once()

    def test_python_code_with_multi_indent_passes(self):
        python_code = "if p:\n" "    for elem in p:\n" "        dothing(elem)\n"
        # test black gets called
        with mock.patch(
            "snakefmt.formatter.Formatter.run_black_format_str", spec=True
        ) as mock_m:
            formatter = setup_formatter(python_code)
            mock_m.assert_called_once()

        # test black formatting output (here, is identical)
        formatter = setup_formatter(python_code)
        actual = formatter.get_formatted()
        assert actual == python_code


class TestParamFormatting:
    def test_configfileLineWithSingleQuotes_returnsDoubleQuotes(self):
        formatter = setup_formatter("configfile: 'foo.yaml'")

        actual = formatter.get_formatted()
        expected = 'configfile: "foo.yaml"\n'

        assert actual == expected

    def test_simple_rule_one_input(self):
        stream = StringIO("rule a:\n" "\tinput: 'foo.txt'")
        smk = Snakefile(stream)
        formatter = Formatter(smk)

        actual = formatter.get_formatted()
        expected = "rule a:\n" "\tinput: \n" '\t\t"foo.txt", \n'

        assert actual == expected

    def test_lambda_function_as_parameter(self):
        stream = StringIO(
            """rule a: 
                input: lambda wildcards: foo(wildcards)"""
        )
        smk = Snakefile(stream)
        formatter = Formatter(smk)

        actual = formatter.get_formatted()
        expected = """rule a:
\tinput: 
\t\tlambda wildcards: foo(wildcards), \n"""

        assert actual == expected

    def test_lambda_function_with_multiple_input_params(self):
        stream = StringIO(
            "rule a:\n"
            "\tinput: 'foo.txt'\n"
            "\tresources:"
            "\t\tmem_mb = lambda wildcards, attempt: attempt * 1000"
        )
        smk = Snakefile(stream)
        formatter = Formatter(smk)

        actual = formatter.get_formatted()
        expected = """rule a:
\tinput: 
\t\t\"foo.txt\"
\tresources:
\t\tmem_mb = lambda wildcards, attempt: attempt * 1000, \n"""

        assert actual == expected
