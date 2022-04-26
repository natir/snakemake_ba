"""Use snakemake benchmark data and plot them"""

# std import

import altair  # type: ignore

# pip import
import pandas  # type: ignore


def dynamic_scatter_plot(
    df: pandas.DataFrame, x: str, y: str, group: str
) -> altair.Chart:
    """Generate a dynamic scatter plot for x and y and group"""

    selection = altair.selection_multi(fields=[group], bind="legend")

    chart = (
        altair.Chart(df)
        .mark_circle(size=10)
        .encode(
            x=x,
            y=y,
            color=group,
            opacity=altair.condition(selection, altair.value(1), altair.value(0.1)),
        )
        .add_selection(selection)
        .properties(width=800, height=600)
        .interactive()
    )

    return chart
