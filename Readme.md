[![publish_docs](https://github.com/natir/snakemake_ba/actions/workflows/docs.yml/badge.svg)](https://natir.github.io/snakemake_ba/)
[![tests](https://github.com/natir/snakemake_ba/actions/workflows/ci.yml/badge.svg)](https://github.com/natir/snakemake_ba/actions/workflows/ci.yml)

# Snakemake Benchmark Analyzer

A python package to found and merge benchmark file associate to a snakemake rules in a `pandas.DataFrame`.

## Install

```
pip install --user git+https://github.com/natir/snakemake_ba.git
```

## Usage

```
import snakemake_ba

data = snakemake_ba.parser.stats_of_rules(pathlib.Path("/path/to/snakemake/working/directory"),
                                          "snakemake/benchmark/string/{with}_{wildcards,\d+}_{support}.txt")

chart = snakemake_ba.plot.dynamic_scatter_plot(data, x='s', y='max_rss', group='support')

char.save("plot.html")
```

Wildcards value is add in column with wildcards name, wildcards with regex are support.
