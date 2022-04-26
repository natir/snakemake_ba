"""Parse snakemake benchmark file"""

# std import
import csv
import os
import pathlib  # type: ignore
import re
import typing

# pip import
import pandas  # type: ignore


def stats_generator(
    file_path: pathlib.Path,
) -> typing.Iterator[typing.Dict[str, float]]:
    """Read a benchmark snakemake file and generate a dict contains statistics"""

    with open(file_path) as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for record in reader:
            del record["h:m:s"]
            fix_record = {k: float(v) for k, v in record.items()}
            yield fix_record


def __recurse_scan(path: pathlib.Path) -> typing.Iterator[pathlib.Path]:
    """Generate all path child of `path` parameter"""

    with os.scandir(path) as scan:
        for entry in scan:
            if entry.is_file():
                yield pathlib.Path(entry.path)
            else:
                yield from __recurse_scan(pathlib.Path(entry.path))


def path_generator(
    working_dir: pathlib.Path, bench_patern: str
) -> typing.Iterator[pathlib.Path]:
    """Generate path matching with benchmark snakemake path"""

    for path in __recurse_scan(working_dir):
        if path.match(f"*{bench_patern}"):
            yield path


def __wildcard_to_regex(
    snakemake_bench_patern: str,
) -> typing.Tuple[str, re.Pattern, typing.List[str]]:
    """Replace snakemake wildcard by a classic regex"""

    wildcard_re = re.compile(r"{(?P<name>[^},]+),?(?P<regex>[^}]+)?}")

    wildcard_name = [
        match.group("name") for match in wildcard_re.finditer(snakemake_bench_patern)
    ]

    def substitute(match: re.Match):
        if match.group("regex") is None:
            return f"(?P<{match.group('name')}>.+)"
        else:
            return f"(?P<{match.group('name')}>{match.group('regex')})"

    wildcard_value_re = re.compile(wildcard_re.sub(substitute, snakemake_bench_patern))

    return (
        wildcard_re.sub("*", snakemake_bench_patern),
        wildcard_value_re,
        wildcard_name,
    )


def stats_of_rules(
    working_dir: pathlib.Path, snakemake_bench_patern: str
) -> pandas.DataFrame:
    """Get all bench statistic of a file"""

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
