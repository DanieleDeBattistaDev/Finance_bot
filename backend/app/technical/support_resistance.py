import pandas as pd


def _cluster(levels: list[float], tolerance: float = 0.005) -> list[float]:
    """Merge price levels within `tolerance` % of each other."""
    if not levels:
        return []
    sorted_lvls = sorted(levels)
    clusters: list[list[float]] = [[sorted_lvls[0]]]
    for lvl in sorted_lvls[1:]:
        if (lvl - clusters[-1][0]) / clusters[-1][0] <= tolerance:
            clusters[-1].append(lvl)
        else:
            clusters.append([lvl])
    return [round(sum(c) / len(c), 6) for c in clusters]


def find_levels(
    df: pd.DataFrame,
    window: int = 10,
    num_levels: int = 5,
) -> tuple[list[float], list[float]]:
    """
    Returns (support_levels, resistance_levels) as price lists,
    clustered and limited to the `num_levels` most recent significant levels.
    """
    highs = df["High"]
    lows = df["Low"]
    n = len(df)

    raw_resistance: list[float] = []
    raw_support: list[float] = []

    for i in range(window, n - window):
        window_highs = highs.iloc[i - window : i + window + 1]
        if highs.iloc[i] == window_highs.max():
            raw_resistance.append(float(highs.iloc[i]))

        window_lows = lows.iloc[i - window : i + window + 1]
        if lows.iloc[i] == window_lows.min():
            raw_support.append(float(lows.iloc[i]))

    support = _cluster(raw_support)[-num_levels:]
    resistance = _cluster(raw_resistance)[-num_levels:]

    return support, resistance
