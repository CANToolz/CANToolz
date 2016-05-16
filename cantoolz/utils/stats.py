

def max_dx_edge(series: iter) -> int:
    prev = None
    max_diff = 0
    diff_edge = 0

    for i in sorted(series):
        if prev is not None and i - prev > max_diff:
            max_diff = i - prev
            diff_edge = prev

        prev = i

    return diff_edge