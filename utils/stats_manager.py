# utils/stats_manager.py

def init_stats(keys):
    """Initialize stats accumulator for given keys."""
    return {k: {"sum": 0.0, "count": 0, "min": float("inf"), "max": float("-inf")} for k in keys}

def update_stats(stats, values):
    """Update stats accumulator with new values."""
    for k, v in values.items():
        if k not in stats:   # ignore keys we don't track
            continue
        stats[k]["sum"] += v
        stats[k]["count"] += 1
        if v < stats[k]["min"]:
            stats[k]["min"] = v
        if v > stats[k]["max"]:
            stats[k]["max"] = v

def finalize_stats(stats):
    """Compute avg, min, max from accumulated stats."""
    out = {}
    for k, s in stats.items():
        if s["count"] > 0:
            avg = s["sum"] / s["count"]
            out[k] = {
                "avg": round(avg, 2),
                "min": round(s["min"], 2),
                "max": round(s["max"], 2),
            }
        else:
            out[k] = {"avg": None, "min": None, "max": None}
    return out
