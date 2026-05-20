from ...config import (
    BIG_FIVE_DIMENSIONS,
    DARK_TRIAD_DIMENSIONS, 
    COLORS, 
    SCALE_MIN, 
    SCALE_MAX, 
)


def _ordered_scores(scores: dict[str, float], keys: tuple[str, ...]) -> list[float]:
    return [scores[key] for key in keys]


def build_big_five_radar_chart(scores: dict[str, float]) -> dict:
    dimension_keys = tuple(BIG_FIVE_DIMENSIONS.keys())
    
    return {
        "data": [
            {
                "type": "scatterpolar", 
                "r": _ordered_scores(scores, dimension_keys), 
                "theta": list(BIG_FIVE_DIMENSIONS.values()), 
                "fill": "toself", 
                "fillcolor": COLORS["primary"], 
                "opacity": 0.6, 
                "line": {"color": COLORS["accent"], "width": 2}, 
                "name": "Big Five", 
            }
        ], 
        "layout": {
            "polar": {
                "radialaxis": {
                    "visible": True, 
                    "range": [SCALE_MIN, SCALE_MAX], 
                    "tickvals": list(range(SCALE_MIN, SCALE_MAX + 1)), 
                    "gridcolor": "lightgray", 
                }, 
                "angularaxis": {
                    "gridcolor": "lightgray", 
                }, 
            }, 
            "showlegend": False, 
            "height": 400, 
            "margin": {"1": 80, "r": 80, "t": 40, "b": 40}, 
            "paper_bgcolor": "rgba(0,0,0,0)", 
            "plot_bgcolor": "rgba(0,0,0,0)", 
        }, 
    }
    

def build_big_five_score_bars(scores: dict[str, float]) -> dict:
    dimension_keys = tuple(BIG_FIVE_DIMENSIONS.keys())
    
    return {
        "dimensions": list(BIG_FIVE_DIMENSIONS.values()),
        "scores": _ordered_scores(scores, dimension_keys),
        "colors": [COLORS[key] for key in dimension_keys],
    }
    

def build_dark_triad_score_bars(scores: dict[str, float]) -> dict:
    dimension_keys = tuple(DARK_TRIAD_DIMENSIONS.keys())

    return {
        "dimensions": list(DARK_TRIAD_DIMENSIONS.values()),
        "scores": _ordered_scores(scores, dimension_keys),
        "colors": ["#6B46C1", "#DC2626", "#374151"],
    }
