"""Found and parse snakemake benchmark file"""

# std import
import csv
import os
import pathlib  # type: ignore
import re
import typing

# pip import
import pandas  # type: ignore


def stats_of_rules(
    working_dir: pathlib.Path, snakemake_bench_patern: str
) -> pandas.DataFrame:
    """Aggregate statistic about a snakemake rules in a [pandas.DataFrame][]

    Args:
        working_dir (pathlib.Path):
            working directory where the studied snakemake was executed
        snakemake_bench_patern (str): string set in `benchmark` section

    Returns:
        data: a DataFrame with benchmark data and wildcard values
    """

    df = pandas.DataFrame()

    (path_filter, wildcard_value_re, wildcard_name) = __wildcard_to_regex(
        snakemake_bench_patern
    )

    for path in path_generator(working_dir, path_filter):
        record: typing.Dict[str, typing.Any] = dict()
        record["path"] = str(path)
        if match := wildcard_value_re.search(str(path)):
            record.update(match.groupdict())
        else:
            record.update({name: "" for name in wildcard_name})

        record_clone = record.copy()
        for stat in stats_generator(path):
            record.update(stat)
            temp_df = pandas.DataFrame(record, index=[1])
            df = pandas.concat([df, temp_df], ignore_index=True, axis=0)
            record = record_clone.copy()

    return df


def stats_generator(
    file_path: pathlib.Path,
) -> typing.Iterator[typing.Dict[str, float]]:
    """Read a benchmark snakemake file and generate a dict contains statistics

    `h:m:s` column are ignored

    Args:
        file_path (pathlib.Path): path of snakemake benchmark file

    Yields:
        stats: each key of snakemake benchmark is associate with value
    """

    with open(file_path) as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for record in reader:
            del record["h:m:s"]
            fix_record = {k: float(v) for k, v in record.items()}
            yield fix_record


def path_generator(target: pathlib.Path, patern: str) -> typing.Iterator[pathlib.Path]:
    """Generate all file match patern in target and subdirectory

    Args:
        target (pathlib.Path): origin of file scan
        patern (str): filename must match this partern (see pathlib.Path.match)

    Yields:
        path: path to file child of target and match pattern
    """

    for path in __recurse_scan(target):
        if path.match(f"*{patern}"):
            yield path


def __recurse_scan(target: pathlib.Path) -> typing.Iterator[pathlib.Path]:
    """Recursive generator of all file child of `target` parameter

    Args:
        target (pathlib.Path): origin of file scan

    Yields:
        path: path to file child of target
    """

    with os.scandir(target) as scan:
        for entry in scan:
            if entry.is_file():
                yield pathlib.Path(entry.path)
            else:
                yield from __recurse_scan(pathlib.Path(entry.path))


def __wildcard_to_regex(
    snakemake_bench_pattern: str,
) -> typing.Tuple[str, re.Pattern, typing.List[str]]:
    """Analyse a snakemake benchmark string to generate usefull stuff

    Args:
        snakemake_bench_pattern (str): argument string of snakemake benchmark section

    Returns:
        tuple: A tuple with, pathlib.Path.match pattern string,
               re.Pattern to extract wildcards information of benchmark path,
               list of wildcards name
    """

    wildcard_re = re.compile(r"{(?P<name>[^},]+),?(?P<regex>[^}]+)?}")

    wildcard_name = [
        match.group("name") for match in wildcard_re.finditer(snakemake_bench_pattern)
    ]

    def substitute(match: re.Match):
        if match.group("regex") is None:
            return f"(?P<{match.group('name')}>.+)"
        else:
            return f"(?P<{match.group('name')}>{match.group('regex')})"

    wildcard_value_re = re.compile(wildcard_re.sub(substitute, snakemake_bench_pattern))

    return (
        wildcard_re.sub("*", snakemake_bench_pattern),
        wildcard_value_re,
        wildcard_name,
    )
