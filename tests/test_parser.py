"""Parser test"""

# std import
import pathlib
import re
import tempfile

# pip import
import pandas

# project import
import snakemake_ba


def test__wildcard_to_regex():
    """Wildcard to regex test"""

    (
        path_filter,
        wildcard_value_re,
        wildcard_name,
    ) = snakemake_ba.parser.__wildcard_to_regex(
        "{baseline,prout}other,stuff/complex{other}.txt"
    )

    assert wildcard_name == ["baseline", "other"]
    assert wildcard_value_re == re.compile(
        "(?P<baseline>prout)other,stuff/complex(?P<other>.+).txt"
    )
    assert path_filter == "*other,stuff/complex*.txt"


def test__recurse_scan():
    """recurse_scan test"""

    origin = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)

    origin_path = origin.name

    sub1 = [
        tempfile.TemporaryDirectory(dir=origin_path, ignore_cleanup_errors=True)
        for _ in range(10)
    ]

    files = [
        tempfile.NamedTemporaryFile(dir=sub1[i].name, delete=False) for i in range(10)
    ]

    content = set(snakemake_ba.parser.__recurse_scan(pathlib.Path(origin_path)))

    assert content == {pathlib.Path(f.name) for f in files}

    origin.cleanup()


def test_path_generator():
    """path_generator test"""

    origin = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)

    origin_path = origin.name

    sub1 = [
        tempfile.TemporaryDirectory(dir=origin_path, ignore_cleanup_errors=True)
        for _ in range(10)
    ]

    files = [
        tempfile.NamedTemporaryFile(
            prefix="prefix_", suffix="_suffix", dir=sub1[i].name, delete=False
        )
        for i in range(10)
    ]

    content = set(
        snakemake_ba.parser.path_generator(pathlib.Path(origin_path), "prefix_*_suffix")
    )

    assert content == {pathlib.Path(f.name) for f in files}


def test_stats_generator():
    """stats_generator test"""

    col_name = ["A", "b", "c", "D", "e", "f", "g", "h:m:s"]
    temp_file = tempfile.NamedTemporaryFile(mode="w")

    print("\t".join(col_name), file=temp_file)
    for i in range(10):
        print("\t".join([str(float(i)) for i in range(len(col_name))]), file=temp_file)

    temp_file.flush()

    data = {
        (name, value)
        for d in snakemake_ba.parser.stats_generator(pathlib.Path(temp_file.name))
        for (name, value) in d.items()
    }

    col_name.pop()  # remove h:m:s col_name
    assert data == {
        (name, float(i)) for _ in range(10) for (i, name) in enumerate(col_name)
    }


def test_stats_of_rules():
    """stats_of_rules test"""

    origin = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)

    origin_path = origin.name

    file1 = tempfile.NamedTemporaryFile(
        mode="w", dir=origin_path, suffix="__10__20__", delete=False
    )
    file2 = tempfile.NamedTemporaryFile(
        mode="w", dir=origin_path, suffix="__11__21__", delete=False
    )

    col_name = ["A", "b", "c", "D", "e", "f", "g", "h:m:s"]
    print("\t".join(col_name), file=file1)
    for i in range(5):
        print("\t".join([str(float(i)) for i in range(len(col_name))]), file=file1)
    file1.flush()

    print("\t".join(col_name), file=file2)
    for i in range(5):
        print("\t".join([str(float(i)) for i in range(len(col_name))]), file=file2)
    file2.flush()

    df = snakemake_ba.parser.stats_of_rules(
        pathlib.Path(origin_path), "{basepath}__{ten}__{twenty}__"
    )

    pandas.set_option("display.max_columns", None)
    print(df.to_dict())

    true_df = {
        "ten": {
            0: "11",
            1: "11",
            2: "11",
            3: "11",
            4: "11",
            5: "10",
            6: "10",
            7: "10",
            8: "10",
            9: "10",
        },
        "twenty": {
            0: "21",
            1: "21",
            2: "21",
            3: "21",
            4: "21",
            5: "20",
            6: "20",
            7: "20",
            8: "20",
            9: "20",
        },
        "A": {
            0: 0.0,
            1: 0.0,
            2: 0.0,
            3: 0.0,
            4: 0.0,
            5: 0.0,
            6: 0.0,
            7: 0.0,
            8: 0.0,
            9: 0.0,
        },
        "b": {
            0: 1.0,
            1: 1.0,
            2: 1.0,
            3: 1.0,
            4: 1.0,
            5: 1.0,
            6: 1.0,
            7: 1.0,
            8: 1.0,
            9: 1.0,
        },
        "c": {
            0: 2.0,
            1: 2.0,
            2: 2.0,
            3: 2.0,
            4: 2.0,
            5: 2.0,
            6: 2.0,
            7: 2.0,
            8: 2.0,
            9: 2.0,
        },
        "D": {
            0: 3.0,
            1: 3.0,
            2: 3.0,
            3: 3.0,
            4: 3.0,
            5: 3.0,
            6: 3.0,
            7: 3.0,
            8: 3.0,
            9: 3.0,
        },
        "e": {
            0: 4.0,
            1: 4.0,
            2: 4.0,
            3: 4.0,
            4: 4.0,
            5: 4.0,
            6: 4.0,
            7: 4.0,
            8: 4.0,
            9: 4.0,
        },
        "f": {
            0: 5.0,
            1: 5.0,
            2: 5.0,
            3: 5.0,
            4: 5.0,
            5: 5.0,
            6: 5.0,
            7: 5.0,
            8: 5.0,
            9: 5.0,
        },
        "g": {
            0: 6.0,
            1: 6.0,
            2: 6.0,
            3: 6.0,
            4: 6.0,
            5: 6.0,
            6: 6.0,
            7: 6.0,
            8: 6.0,
            9: 6.0,
        },
    }

    df_dict = df.to_dict()

    assert set(df_dict["ten"]) == set(true_df["ten"])
    assert set(df_dict["twenty"]) == set(true_df["twenty"])
    assert set(df_dict["A"]) == set(true_df["A"])
    assert set(df_dict["b"]) == set(true_df["b"])
    assert set(df_dict["c"]) == set(true_df["c"])
    assert set(df_dict["D"]) == set(true_df["D"])
    assert set(df_dict["e"]) == set(true_df["e"])
    assert set(df_dict["f"]) == set(true_df["f"])
    assert set(df_dict["g"]) == set(true_df["g"])
