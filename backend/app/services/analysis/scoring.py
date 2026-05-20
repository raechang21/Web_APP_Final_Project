from ...config import (
    BIG_FIVE_DIMENSION_KEYS, 
    DARK_TRIAD_DIMENSION_KEYS, 
    SCALE_MIN, 
    SCALE_MAX, 
    SCORE_LABELS, 
    SCORE_LABELS_ZH
)


def _reverse_score(score: int) -> int:
    return SCALE_MAX + SCALE_MIN - score


def _calculate_dimension_scores(
    answers: dict[int, int], 
    questions: list[dict], 
    dimensions: tuple[str, ...],
) -> dict[str, float]:
    dimensions_scores: dict[str, list[int]] = {dimension: [] for dimension in dimensions}
    
    for question in questions: 
        question_id = question["id"]
        dimension = question["dimension"]
        is_reversed = question.get("reverse", question.get("reversed", False))
        
        if question_id not in answers:
            continue
        
        score = answers[question_id]
        if is_reversed:
            score = _reverse_score(score)
            
        if dimension in dimensions_scores:
            dimensions_scores[dimension].append(score)
            
    final_scores: dict[str, float] = {}
    for dimension, scores in dimensions_scores.items():
        if scores:
            final_scores[dimension] = round(sum(scores) / len(scores), 1)
        else:
            final_scores[dimension] = float(SCALE_MIN)
    
    return final_scores


def calculate_big_five_scores(
    answers: dict[int, int], 
    questions: list[dict]
) -> dict[str, float]:
    return _calculate_dimension_scores(
        answers = answers, 
        questions = questions, 
        dimensions = BIG_FIVE_DIMENSION_KEYS, 
    )
    

def calculate_dark_triad_scores(
    answers: dict[int, int], 
    questions: list[dict]
) -> dict[str, float]:
    return _calculate_dimension_scores(
        answers = answers, 
        questions = questions, 
        dimensions = DARK_TRIAD_DIMENSION_KEYS, 
    )
    

def get_score_label(score: float) -> str:
    for label, (min_score, max_score) in SCORE_LABELS.items():
        if min_score <= score <= max_score:
            return SCORE_LABELS_ZH[label]
    
    return SCORE_LABELS_ZH["below_average"]
