"""Use snakemake benchmark data and plot them"""

# std import
import typing

import altair  # type: ignore

# pip import
import pandas  # type: ignore


def dynamic_scatter_plot(
    df: pandas.DataFrame, x: str, y: str, group: typing.Optional[str] = None
) -> altair.Chart:
    """Generate an altair dynamic scatter plot

    Args:
        x (str): data show on x axis
        y (str): data show on y axis
        group (str): dataframe column use to group data (optional)

    Returns:
        chart (altair.Chart): scatter plot
    """

    chart = (
        altair.Chart(df)
        .mark_circle(size=10)
        .encode(
            x=x,
            y=y,
        )
        .properties(width=800, height=600)
        .interactive()
    )

    if group is not None:
        selection = altair.selection_multi(fields=[group], bind="legend")

        chart = chart.encode(
            color=group,
            opacity=altair.condition(selection, altair.value(1), altair.value(0.1)),
        ).add_selection(selection)

    return chart
