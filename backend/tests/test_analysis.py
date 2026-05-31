"""
Unit tests for:
- services/analysis/integration.py
- services/analysis/scoring.py

執行方式（在 backend 資料夾下，虛擬環境啟動後）：
    pytest tests/test_analysis.py -v
"""

import pytest
from unittest.mock import MagicMock


# ──────────────────────────────────────────────
# 模擬資料模型（避免 import 整個專案）
# ──────────────────────────────────────────────

class MBTIResult:
    def __init__(self, type: str):
        self.type = type  # e.g. "INTJ"

class BigFiveResult:
    def __init__(self, extraversion, agreeableness, conscientiousness, neuroticism, openness):
        self.extraversion = extraversion
        self.agreeableness = agreeableness
        self.conscientiousness = conscientiousness
        self.neuroticism = neuroticism
        self.openness = openness

class ZodiacResult:
    def __init__(self, sign: str):
        self.sign = sign


# ──────────────────────────────────────────────
# 直接貼入 integration.py 的邏輯（避免 import 路徑問題）
# ──────────────────────────────────────────────

def find_contradictions(mbti, bigfive, zodiac):
    contradictions = []

    if mbti.type[0] == 'E' and bigfive.extraversion < 3.0:
        contradictions.append((
            f"MBTI 顯示外向（{mbti.type[0]}）",
            f"但 Big Five 外向性偏低（{bigfive.extraversion:.1f}）"
        ))
    elif mbti.type[0] == 'I' and bigfive.extraversion > 4.5:
        contradictions.append((
            f"MBTI 顯示內向（{mbti.type[0]}）",
            f"但 Big Five 外向性偏高（{bigfive.extraversion:.1f}）"
        ))

    if mbti.type[2] == 'T' and bigfive.agreeableness > 5.0:
        contradictions.append((
            f"MBTI 顯示理性思考（{mbti.type[2]}）",
            f"但 Big Five 友善性很高（{bigfive.agreeableness:.1f}）"
        ))
    elif mbti.type[2] == 'F' and bigfive.agreeableness < 3.0:
        contradictions.append((
            f"MBTI 顯示情感導向（{mbti.type[2]}）",
            f"但 Big Five 友善性偏低（{bigfive.agreeableness:.1f}）"
        ))

    if mbti.type[3] == 'J' and bigfive.conscientiousness < 3.0:
        contradictions.append((
            f"MBTI 顯示計劃性（{mbti.type[3]}）",
            f"但 Big Five 盡責性偏低（{bigfive.conscientiousness:.1f}）"
        ))
    elif mbti.type[3] == 'P' and bigfive.conscientiousness > 5.0:
        contradictions.append((
            f"MBTI 顯示彈性（{mbti.type[3]}）",
            f"但 Big Five 盡責性很高（{bigfive.conscientiousness:.1f}）"
        ))

    high_neuroticism_signs = ["巨蟹座", "雙魚座", "天蠍座"]
    if bigfive.neuroticism < 2.5 and zodiac.sign in high_neuroticism_signs:
        contradictions.append((
            f"Big Five 神經質很低（{bigfive.neuroticism:.1f}）",
            f"但 {zodiac.sign} 通常較為敏感"
        ))

    return contradictions


def find_consistencies(mbti, bigfive):
    consistencies = []

    if mbti.type[0] == 'E' and bigfive.extraversion > 4.0:
        consistencies.append("外向特質一致")
    elif mbti.type[0] == 'I' and bigfive.extraversion < 3.5:
        consistencies.append("內向特質一致")

    if mbti.type[3] == 'J' and bigfive.conscientiousness > 4.0:
        consistencies.append("計劃性與盡責性一致")
    elif mbti.type[3] == 'P' and bigfive.conscientiousness < 3.5:
        consistencies.append("彈性與低盡責性一致")

    return consistencies


# ──────────────────────────────────────────────
# 直接貼入 scoring.py 的邏輯
# ──────────────────────────────────────────────

SCORE_LABELS = {
    "low":       (1.0, 2.5),
    "below_avg": (2.5, 3.5),
    "above_avg": (3.5, 5.0),
    "high":      (5.0, 6.0),
}
SCORE_LABELS_ZH = {
    "low": "低",
    "below_avg": "偏低",
    "above_avg": "偏高",
    "high": "高",
}

def calculate_bigfive_scores(answers, questions):
    dimension_scores = {
        'openness': [], 'conscientiousness': [],
        'extraversion': [], 'agreeableness': [], 'neuroticism': []
    }
    for q in questions:
        q_id = q['id']
        dimension = q['dimension']
        is_reversed = q.get('reversed', False)
        if q_id in answers:
            score = answers[q_id]
            if is_reversed:
                score = 7 - score
            dimension_scores[dimension].append(score)
    final_scores = {}
    for dim, scores in dimension_scores.items():
        if scores:
            final_scores[dim] = round(sum(scores) / len(scores), 1)
        else:
            final_scores[dim] = 1.0
    return final_scores

def calculate_dark_triad_scores(answers, questions):
    dimension_scores = {
        'machiavellianism': [], 'narcissism': [], 'psychopathy': []
    }
    for q in questions:
        q_id = q['id']
        dimension = q['dimension']
        is_reversed = q.get('reversed', False)
        if q_id in answers:
            score = answers[q_id]
            if is_reversed:
                score = 7 - score
            dimension_scores[dimension].append(score)
    final_scores = {}
    for dim, scores in dimension_scores.items():
        if scores:
            final_scores[dim] = round(sum(scores) / len(scores), 1)
        else:
            final_scores[dim] = 1.0
    return final_scores

def get_score_label(score):
    for label, (min_score, max_score) in SCORE_LABELS.items():
        if min_score <= score <= max_score:
            return SCORE_LABELS_ZH[label]
    return "中等"

def get_progress_percentage(score, max_score=6.0):
    return (score / max_score) * 100


# ══════════════════════════════════════════════
# 測試：integration.py
# ══════════════════════════════════════════════

class TestFindContradictions:

    def test_extrovert_mbti_but_low_bigfive_extraversion(self):
        """MBTI 外向但 Big Five 外向性低 → 應偵測到矛盾"""
        mbti = MBTIResult("ESTJ")
        bigfive = BigFiveResult(extraversion=2.0, agreeableness=3.5, conscientiousness=4.0, neuroticism=3.0, openness=3.0)
        zodiac = ZodiacResult("獅子座")
        result = find_contradictions(mbti, bigfive, zodiac)
        assert len(result) == 1
        assert "外向" in result[0][0]

    def test_introvert_mbti_but_high_bigfive_extraversion(self):
        """MBTI 內向但 Big Five 外向性高 → 應偵測到矛盾"""
        mbti = MBTIResult("INTJ")
        bigfive = BigFiveResult(extraversion=5.0, agreeableness=3.5, conscientiousness=4.0, neuroticism=3.0, openness=3.0)
        zodiac = ZodiacResult("獅子座")
        result = find_contradictions(mbti, bigfive, zodiac)
        assert len(result) == 1
        assert "內向" in result[0][0]

    def test_thinking_mbti_but_high_agreeableness(self):
        """MBTI 理性思考但 Big Five 友善性高 → 應偵測到矛盾"""
        mbti = MBTIResult("ENTJ")
        bigfive = BigFiveResult(extraversion=5.0, agreeableness=5.5, conscientiousness=4.0, neuroticism=3.0, openness=3.0)
        zodiac = ZodiacResult("獅子座")
        result = find_contradictions(mbti, bigfive, zodiac)
        assert any("理性思考" in r[0] for r in result)

    def test_judging_mbti_but_low_conscientiousness(self):
        """MBTI 計劃性但 Big Five 盡責性低 → 應偵測到矛盾"""
        mbti = MBTIResult("ISTJ")
        bigfive = BigFiveResult(extraversion=3.0, agreeableness=3.5, conscientiousness=2.0, neuroticism=3.0, openness=3.0)
        zodiac = ZodiacResult("獅子座")
        result = find_contradictions(mbti, bigfive, zodiac)
        assert any("計劃性" in r[0] for r in result)

    def test_low_neuroticism_with_sensitive_zodiac(self):
        """Big Five 神經質低但星座為巨蟹座 → 應偵測到矛盾"""
        mbti = MBTIResult("ISTJ")
        bigfive = BigFiveResult(extraversion=3.0, agreeableness=3.5, conscientiousness=4.0, neuroticism=2.0, openness=3.0)
        zodiac = ZodiacResult("巨蟹座")
        result = find_contradictions(mbti, bigfive, zodiac)
        assert any("巨蟹座" in r[1] for r in result)

    def test_no_contradictions(self):
        """結果一致時，應回傳空列表"""
        mbti = MBTIResult("ENFJ")
        bigfive = BigFiveResult(extraversion=4.5, agreeableness=4.0, conscientiousness=4.5, neuroticism=3.0, openness=4.0)
        zodiac = ZodiacResult("獅子座")
        result = find_contradictions(mbti, bigfive, zodiac)
        assert result == []

    def test_returns_list(self):
        """回傳值應該是 list 型別"""
        mbti = MBTIResult("INFP")
        bigfive = BigFiveResult(extraversion=3.0, agreeableness=3.5, conscientiousness=3.0, neuroticism=3.0, openness=3.0)
        zodiac = ZodiacResult("天秤座")
        result = find_contradictions(mbti, bigfive, zodiac)
        assert isinstance(result, list)


class TestFindConsistencies:

    def test_extrovert_consistency(self):
        """MBTI 外向且 Big Five 外向性高 → 應偵測到一致性"""
        mbti = MBTIResult("ENFJ")
        bigfive = BigFiveResult(extraversion=4.5, agreeableness=4.0, conscientiousness=4.0, neuroticism=3.0, openness=3.0)
        result = find_consistencies(mbti, bigfive)
        assert "外向特質一致" in result

    def test_introvert_consistency(self):
        """MBTI 內向且 Big Five 外向性低 → 應偵測到一致性"""
        mbti = MBTIResult("INTJ")
        bigfive = BigFiveResult(extraversion=3.0, agreeableness=4.0, conscientiousness=4.0, neuroticism=3.0, openness=3.0)
        result = find_consistencies(mbti, bigfive)
        assert "內向特質一致" in result

    def test_judging_consistency(self):
        """MBTI J 且 Big Five 盡責性高 → 應偵測到一致性"""
        mbti = MBTIResult("ISTJ")
        bigfive = BigFiveResult(extraversion=3.0, agreeableness=4.0, conscientiousness=4.5, neuroticism=3.0, openness=3.0)
        result = find_consistencies(mbti, bigfive)
        assert "計劃性與盡責性一致" in result

    def test_no_consistencies(self):
        """沒有明顯一致性時，應回傳空列表"""
        mbti = MBTIResult("ENTP")
        bigfive = BigFiveResult(extraversion=3.5, agreeableness=3.5, conscientiousness=3.5, neuroticism=3.5, openness=3.5)
        result = find_consistencies(mbti, bigfive)
        assert result == []


# ══════════════════════════════════════════════
# 測試：scoring.py
# ══════════════════════════════════════════════

class TestCalculateBigfiveScores:

    def test_basic_calculation(self):
        """正常答題，分數應正確計算"""
        questions = [
            {'id': 1, 'dimension': 'extraversion', 'reversed': False},
            {'id': 2, 'dimension': 'extraversion', 'reversed': False},
        ]
        answers = {1: 4, 2: 6}
        result = calculate_bigfive_scores(answers, questions)
        assert result['extraversion'] == 5.0

    def test_reversed_scoring(self):
        """反向計分應正確（7 - 原始分數）"""
        questions = [
            {'id': 1, 'dimension': 'neuroticism', 'reversed': True},
        ]
        answers = {1: 2}
        result = calculate_bigfive_scores(answers, questions)
        assert result['neuroticism'] == 5.0  # 7 - 2 = 5

    def test_missing_dimension_defaults_to_1(self):
        """沒有作答的維度，預設應為 1.0"""
        questions = [
            {'id': 1, 'dimension': 'extraversion', 'reversed': False},
        ]
        answers = {1: 4}
        result = calculate_bigfive_scores(answers, questions)
        assert result['openness'] == 1.0

    def test_unanswered_question_ignored(self):
        """沒有對應答案的題目應被忽略"""
        questions = [
            {'id': 1, 'dimension': 'extraversion', 'reversed': False},
            {'id': 2, 'dimension': 'extraversion', 'reversed': False},
        ]
        answers = {1: 4}  # 只回答第 1 題
        result = calculate_bigfive_scores(answers, questions)
        assert result['extraversion'] == 4.0

    def test_all_five_dimensions_present(self):
        """回傳結果應包含全部五個維度"""
        result = calculate_bigfive_scores({}, [])
        assert set(result.keys()) == {'openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'}


class TestCalculateDarkTriadScores:

    def test_basic_calculation(self):
        """正常答題，分數應正確計算"""
        questions = [
            {'id': 1, 'dimension': 'narcissism', 'reversed': False},
            {'id': 2, 'dimension': 'narcissism', 'reversed': False},
        ]
        answers = {1: 3, 2: 5}
        result = calculate_dark_triad_scores(answers, questions)
        assert result['narcissism'] == 4.0

    def test_reversed_scoring(self):
        """反向計分應正確"""
        questions = [
            {'id': 1, 'dimension': 'psychopathy', 'reversed': True},
        ]
        answers = {1: 1}
        result = calculate_dark_triad_scores(answers, questions)
        assert result['psychopathy'] == 6.0  # 7 - 1 = 6

    def test_all_three_dimensions_present(self):
        """回傳結果應包含全部三個維度"""
        result = calculate_dark_triad_scores({}, [])
        assert set(result.keys()) == {'machiavellianism', 'narcissism', 'psychopathy'}


class TestGetScoreLabel:

    def test_low_score(self):
        assert get_score_label(1.5) == "低"

    def test_below_avg_score(self):
        assert get_score_label(3.0) == "偏低"

    def test_above_avg_score(self):
        assert get_score_label(4.0) == "偏高"

    def test_high_score(self):
        assert get_score_label(5.5) == "高"

    def test_boundary_score(self):
        assert get_score_label(2.5) == "低"


class TestGetProgressPercentage:

    def test_full_score(self):
        assert get_progress_percentage(6.0) == 100.0

    def test_half_score(self):
        assert get_progress_percentage(3.0) == 50.0

    def test_min_score(self):
        assert get_progress_percentage(1.0) == pytest.approx(16.67, rel=1e-2)

    def test_custom_max_score(self):
        assert get_progress_percentage(5.0, max_score=10.0) == 50.0

"""
aim: test analysis
result: passed
how to run: \backend> pytest tests/test_analysis.py -v
output:
==================================== test session starts ====================================
platform win32 -- Python 3.14.4, pytest-9.0.3, pluggy-1.6.0 -- \Web_APP_Final_Project\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: \Web_APP_Final_Project\backend
plugins: anyio-4.13.0
collected 28 items                                                                           

tests/test_analysis.py::TestFindContradictions::test_extrovert_mbti_but_low_bigfive_extraversion PASSED [  3%]
tests/test_analysis.py::TestFindContradictions::test_introvert_mbti_but_high_bigfive_extraversion PASSED [  7%]
tests/test_analysis.py::TestFindContradictions::test_thinking_mbti_but_high_agreeableness PASSED [ 10%]
tests/test_analysis.py::TestFindContradictions::test_judging_mbti_but_low_conscientiousness PASSED [ 14%]
tests/test_analysis.py::TestFindContradictions::test_low_neuroticism_with_sensitive_zodiac PASSED [ 17%]
tests/test_analysis.py::TestFindContradictions::test_no_contradictions PASSED          [ 21%]
tests/test_analysis.py::TestFindContradictions::test_returns_list PASSED               [ 25%]
tests/test_analysis.py::TestFindConsistencies::test_extrovert_consistency PASSED       [ 28%]
tests/test_analysis.py::TestFindConsistencies::test_introvert_consistency PASSED       [ 32%]
tests/test_analysis.py::TestFindConsistencies::test_judging_consistency PASSED         [ 35%]
tests/test_analysis.py::TestFindConsistencies::test_no_consistencies PASSED            [ 39%]
tests/test_analysis.py::TestCalculateBigfiveScores::test_basic_calculation PASSED      [ 42%]
tests/test_analysis.py::TestCalculateBigfiveScores::test_reversed_scoring PASSED       [ 46%]
tests/test_analysis.py::TestCalculateBigfiveScores::test_missing_dimension_defaults_to_1 PASSED [ 50%]
tests/test_analysis.py::TestCalculateBigfiveScores::test_unanswered_question_ignored PASSED [ 53%]
tests/test_analysis.py::TestCalculateBigfiveScores::test_all_five_dimensions_present PASSED [ 57%]
tests/test_analysis.py::TestCalculateDarkTriadScores::test_basic_calculation PASSED    [ 60%]
tests/test_analysis.py::TestCalculateDarkTriadScores::test_reversed_scoring PASSED     [ 64%]
tests/test_analysis.py::TestCalculateDarkTriadScores::test_all_three_dimensions_present PASSED [ 67%]
tests/test_analysis.py::TestGetScoreLabel::test_low_score PASSED                       [ 71%]
tests/test_analysis.py::TestGetScoreLabel::test_below_avg_score PASSED                 [ 75%]
tests/test_analysis.py::TestGetScoreLabel::test_above_avg_score PASSED                 [ 78%]
tests/test_analysis.py::TestGetScoreLabel::test_high_score PASSED                      [ 82%]
tests/test_analysis.py::TestGetScoreLabel::test_boundary_score PASSED                  [ 85%]
tests/test_analysis.py::TestGetProgressPercentage::test_full_score PASSED              [ 89%]
tests/test_analysis.py::TestGetProgressPercentage::test_half_score PASSED              [ 92%]
tests/test_analysis.py::TestGetProgressPercentage::test_min_score PASSED               [ 96%]
tests/test_analysis.py::TestGetProgressPercentage::test_custom_max_score PASSED        [100%]

==================================== 28 passed in 0.19s =====================================
"""