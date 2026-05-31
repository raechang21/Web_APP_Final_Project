"""
Unit tests for:
- services/chat_memory.py
- services/user_repo.py

執行方式（在 backend 資料夾下，虛擬環境啟動後）：
    pytest tests/test_memory_and_repo.py -v
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker, relationship


# ──────────────────────────────────────────────
# 模擬資料庫模型
# ──────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    user_name = Column(String, primary_key=True)
    mbti = Column(String, nullable=True)
    bigfive_scores = Column(JSON, nullable=True)
    zodiac = Column(String, nullable=True)
    dark_triad_scores = Column(JSON, nullable=True)
    deep_analysis = Column(String, nullable=True)


class UserMemory(Base):
    __tablename__ = "user_memory"
    user_name = Column(String, primary_key=True)
    memory_json = Column(JSON, nullable=True)


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, nullable=False)
    started_at = Column(String, nullable=True)
    ended_at = Column(String, nullable=True)
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(String, nullable=True)
    conversation = relationship("Conversation", back_populates="messages")


# ──────────────────────────────────────────────
# 貼入 chat_memory.py 的邏輯
# ──────────────────────────────────────────────

from typing import Any

def _upsert_user_chat(db, *, user_name, **fields):
    user = db.get(User, user_name)
    if user is None:
        user = User(user_name=user_name)
        db.add(user)
    for key, value in fields.items():
        if value is not None:
            setattr(user, key, value)
    return user

def load_memory_chat(db, user_name):
    mem = db.get(UserMemory, user_name)
    return mem.memory_json if mem else None

def save_chat_memory(db, *, user_name, chat_messages, mbti, bigfive_scores, zodiac, dark_triad_scores):
    if not user_name:
        return
    _upsert_user_chat(db, user_name=user_name, mbti=mbti, bigfive_scores=bigfive_scores,
                      zodiac=zodiac, dark_triad_scores=dark_triad_scores)
    mem = db.get(UserMemory, user_name)
    existing = mem.memory_json if mem else {}
    key_topics = [
        m["content"] for m in chat_messages
        if m.get("role") == "user" and len(m.get("content", "")) > 5
    ]
    summaries = list(existing.get("conversation_summaries", []))
    if key_topics:
        summaries.append({"date": datetime.now(timezone.utc).isoformat(), "topics": key_topics[:3]})
        summaries = summaries[-3:]
    memory_data = {
        "user_name": user_name, "mbti": mbti, "bigfive_scores": bigfive_scores,
        "zodiac": zodiac, "dark_triad_scores": dark_triad_scores,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_conversations": existing.get("total_conversations", 0) + 1,
        "conversation_summaries": summaries,
        "key_topics": key_topics[:5],
    }
    if mem is None:
        db.add(UserMemory(user_name=user_name, memory_json=memory_data))
    else:
        mem.memory_json = memory_data
    db.commit()

def save_conversation(db, *, user_name, messages):
    if not user_name or not messages:
        return None
    _upsert_user_chat(db, user_name=user_name)
    conv = Conversation(user_name=user_name, started_at=datetime.now(timezone.utc).isoformat())
    db.add(conv)
    db.flush()
    for m in messages:
        ts = m.get("timestamp")
        try:
            created = datetime.fromisoformat(ts) if ts else datetime.now(timezone.utc)
        except ValueError:
            created = datetime.now(timezone.utc)
        db.add(Message(
            conversation_id=conv.id, role=m.get("role", "user"),
            content=m.get("content", ""), created_at=created.isoformat(),
        ))
    conv.ended_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    return conv

def list_conversations(db, user_name):
    rows = db.query(Conversation).filter_by(user_name=user_name).order_by(Conversation.started_at.desc()).all()
    out = []
    for c in rows:
        first = c.messages[0].content if c.messages else ""
        out.append({"id": c.id, "timestamp": c.started_at, "message_count": len(c.messages), "preview": first[:50]})
    return out

def latest_conversation_messages(db, user_name):
    conv = db.query(Conversation).filter_by(user_name=user_name).order_by(Conversation.started_at.desc()).first()
    if not conv:
        return []
    return [{"role": m.role, "content": m.content, "timestamp": m.created_at} for m in conv.messages]

def delete_conversation(db, *, user_name, conversation_id):
    conv = db.query(Conversation).filter_by(id=conversation_id, user_name=user_name).first()
    if not conv:
        return False
    db.delete(conv)
    db.commit()
    return True

def delete_all_conversations(db, *, user_name):
    convs = db.query(Conversation).filter_by(user_name=user_name).all()
    count = len(convs)
    for c in convs:
        db.delete(c)
    db.commit()
    return count


# ──────────────────────────────────────────────
# 貼入 user_repo.py 的邏輯
# ──────────────────────────────────────────────

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def upsert_user_repo(db, *, user_name, mbti=None, bigfive_scores=None, zodiac=None, dark_triad_scores=None, deep_analysis=None):
    user = db.get(User, user_name)
    if user is None:
        user = User(user_name=user_name)
        db.add(user)
    user.mbti = mbti
    user.bigfive_scores = bigfive_scores
    user.zodiac = zodiac
    user.dark_triad_scores = dark_triad_scores
    if deep_analysis is not None:
        user.deep_analysis = deep_analysis
    return user

def save_user_profile(db, *, user_name, mbti=None, bigfive_scores=None, zodiac=None, dark_triad_scores=None, deep_analysis=None):
    if not user_name:
        return
    upsert_user_repo(db, user_name=user_name, mbti=mbti, bigfive_scores=bigfive_scores,
                     zodiac=zodiac, dark_triad_scores=dark_triad_scores, deep_analysis=deep_analysis)
    memory = db.get(UserMemory, user_name)
    existing = memory.memory_json if memory else {}
    saved_deep_analysis = deep_analysis if deep_analysis is not None else existing.get("deep_analysis")
    memory_data = {
        **existing, "user_name": user_name, "mbti": mbti, "bigfive_scores": bigfive_scores,
        "zodiac": zodiac, "dark_triad_scores": dark_triad_scores,
        "deep_analysis": saved_deep_analysis, "last_updated": _now_iso(),
    }
    if memory is None:
        db.add(UserMemory(user_name=user_name, memory_json=memory_data))
    else:
        memory.memory_json = memory_data
    db.commit()

def reset_user_profile(db, *, user_name):
    if not user_name:
        return
    user = db.get(User, user_name)
    if user is None:
        user = User(user_name=user_name)
        db.add(user)
    else:
        user.mbti = None
        user.bigfive_scores = None
        user.zodiac = None
        user.dark_triad_scores = None
        user.deep_analysis = None
    memory = db.get(UserMemory, user_name)
    memory_data = {
        "user_name": user_name, "mbti": None, "bigfive_scores": None,
        "zodiac": None, "dark_triad_scores": None, "deep_analysis": None,
        "last_updated": _now_iso(),
    }
    if memory is None:
        db.add(UserMemory(user_name=user_name, memory_json=memory_data))
    else:
        memory.memory_json = memory_data
    db.commit()


# ──────────────────────────────────────────────
# 測試用 fixture
# ──────────────────────────────────────────────

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    engine.dispose()


# ══════════════════════════════════════════════
# 測試：chat_memory.py
# ══════════════════════════════════════════════

class TestUpsertUser:

    def test_creates_new_user(self, db):
        """不存在的使用者應被建立"""
        user = _upsert_user_chat(db, user_name="alice")
        db.flush()
        assert db.get(User, "alice") is not None

    def test_updates_existing_user(self, db):
        """已存在的使用者應被更新"""
        _upsert_user_chat(db, user_name="alice")
        db.flush()
        _upsert_user_chat(db, user_name="alice", mbti="INTJ")
        db.flush()
        user = db.get(User, "alice")
        assert user.mbti == "INTJ"

    def test_none_fields_not_overwritten(self, db):
        """傳入 None 的欄位不應覆蓋已有的值"""
        _upsert_user_chat(db, user_name="alice", mbti="INTJ")
        db.flush()
        _upsert_user_chat(db, user_name="alice", mbti=None)
        db.flush()
        user = db.get(User, "alice")
        assert user.mbti == "INTJ"


class TestLoadMemoryChat:

    def test_returns_none_for_unknown_user(self, db):
        assert load_memory_chat(db, "nobody") is None

    def test_returns_memory_json_for_known_user(self, db):
        db.add(UserMemory(user_name="bob", memory_json={"mbti": "ENFP"}))
        db.commit()
        result = load_memory_chat(db, "bob")
        assert result == {"mbti": "ENFP"}


class TestSaveChatMemory:

    def test_creates_memory_for_new_user(self, db):
        save_chat_memory(db, user_name="alice", chat_messages=[], mbti="INTJ",
                         bigfive_scores=None, zodiac=None, dark_triad_scores=None)
        mem = db.get(UserMemory, "alice")
        assert mem is not None
        assert mem.memory_json["mbti"] == "INTJ"

    def test_increments_total_conversations(self, db):
        save_chat_memory(db, user_name="alice", chat_messages=[], mbti=None,
                         bigfive_scores=None, zodiac=None, dark_triad_scores=None)
        save_chat_memory(db, user_name="alice", chat_messages=[], mbti=None,
                         bigfive_scores=None, zodiac=None, dark_triad_scores=None)
        mem = db.get(UserMemory, "alice")
        assert mem.memory_json["total_conversations"] == 2

    def test_key_topics_extracted_from_user_messages(self, db):
        messages = [
            {"role": "user", "content": "我想了解我的性格"},
            {"role": "assistant", "content": "好的"},
        ]
        save_chat_memory(db, user_name="alice", chat_messages=messages, mbti=None,
                         bigfive_scores=None, zodiac=None, dark_triad_scores=None)
        mem = db.get(UserMemory, "alice")
        assert "我想了解我的性格" in mem.memory_json["key_topics"]

    def test_short_messages_excluded_from_key_topics(self, db):
        messages = [{"role": "user", "content": "hi"}]
        save_chat_memory(db, user_name="alice", chat_messages=messages, mbti=None,
                         bigfive_scores=None, zodiac=None, dark_triad_scores=None)
        mem = db.get(UserMemory, "alice")
        assert "hi" not in mem.memory_json["key_topics"]

    def test_empty_username_does_nothing(self, db):
        save_chat_memory(db, user_name="", chat_messages=[], mbti=None,
                         bigfive_scores=None, zodiac=None, dark_triad_scores=None)
        assert db.get(UserMemory, "") is None


class TestSaveConversation:

    def test_saves_conversation_with_messages(self, db):
        messages = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"},
        ]
        conv = save_conversation(db, user_name="alice", messages=messages)
        assert conv is not None
        assert len(conv.messages) == 2

    def test_returns_none_for_empty_messages(self, db):
        result = save_conversation(db, user_name="alice", messages=[])
        assert result is None

    def test_returns_none_for_empty_username(self, db):
        result = save_conversation(db, user_name="", messages=[{"role": "user", "content": "hi"}])
        assert result is None

    def test_invalid_timestamp_uses_default(self, db):
        messages = [{"role": "user", "content": "hi", "timestamp": "not-a-date"}]
        conv = save_conversation(db, user_name="alice", messages=messages)
        assert conv is not None


class TestListConversations:

    def test_returns_empty_for_unknown_user(self, db):
        assert list_conversations(db, "nobody") == []

    def test_returns_conversations_in_order(self, db):
        save_conversation(db, user_name="alice", messages=[{"role": "user", "content": "第一則"}])
        save_conversation(db, user_name="alice", messages=[{"role": "user", "content": "第二則"}])
        result = list_conversations(db, "alice")
        assert len(result) == 2

    def test_preview_is_truncated_to_50_chars(self, db):
        long_content = "A" * 100
        save_conversation(db, user_name="alice", messages=[{"role": "user", "content": long_content}])
        result = list_conversations(db, "alice")
        assert len(result[0]["preview"]) <= 50


class TestDeleteConversation:

    def test_deletes_existing_conversation(self, db):
        conv = save_conversation(db, user_name="alice", messages=[{"role": "user", "content": "hi there"}])
        result = delete_conversation(db, user_name="alice", conversation_id=conv.id)
        assert result == True

    def test_returns_false_for_nonexistent_conversation(self, db):
        result = delete_conversation(db, user_name="alice", conversation_id=9999)
        assert result == False

    def test_cannot_delete_other_users_conversation(self, db):
        conv = save_conversation(db, user_name="alice", messages=[{"role": "user", "content": "hi there"}])
        result = delete_conversation(db, user_name="bob", conversation_id=conv.id)
        assert result == False


class TestDeleteAllConversations:

    def test_deletes_all_conversations(self, db):
        save_conversation(db, user_name="alice", messages=[{"role": "user", "content": "第一則"}])
        save_conversation(db, user_name="alice", messages=[{"role": "user", "content": "第二則"}])
        count = delete_all_conversations(db, user_name="alice")
        assert count == 2
        assert list_conversations(db, "alice") == []

    def test_returns_zero_for_unknown_user(self, db):
        count = delete_all_conversations(db, user_name="nobody")
        assert count == 0


# ══════════════════════════════════════════════
# 測試：user_repo.py
# ══════════════════════════════════════════════

class TestUpsertUserRepo:

    def test_creates_new_user(self, db):
        upsert_user_repo(db, user_name="carol")
        db.flush()
        assert db.get(User, "carol") is not None

    def test_overwrites_fields_on_update(self, db):
        upsert_user_repo(db, user_name="carol", mbti="INTJ")
        db.flush()
        upsert_user_repo(db, user_name="carol", mbti="ENFP")
        db.flush()
        user = db.get(User, "carol")
        assert user.mbti == "ENFP"

    def test_deep_analysis_not_updated_when_none(self, db):
        upsert_user_repo(db, user_name="carol", deep_analysis="原始分析")
        db.flush()
        upsert_user_repo(db, user_name="carol", deep_analysis=None)
        db.flush()
        user = db.get(User, "carol")
        assert user.deep_analysis == "原始分析"


class TestSaveUserProfile:

    def test_saves_profile_to_memory(self, db):
        save_user_profile(db, user_name="carol", mbti="INTJ", zodiac="摩羯座")
        mem = db.get(UserMemory, "carol")
        assert mem.memory_json["mbti"] == "INTJ"
        assert mem.memory_json["zodiac"] == "摩羯座"

    def test_preserves_existing_deep_analysis_when_not_provided(self, db):
        save_user_profile(db, user_name="carol", deep_analysis="舊分析")
        save_user_profile(db, user_name="carol", mbti="INTJ")  # 沒有傳 deep_analysis
        mem = db.get(UserMemory, "carol")
        assert mem.memory_json["deep_analysis"] == "舊分析"

    def test_updates_deep_analysis_when_provided(self, db):
        save_user_profile(db, user_name="carol", deep_analysis="舊分析")
        save_user_profile(db, user_name="carol", deep_analysis="新分析")
        mem = db.get(UserMemory, "carol")
        assert mem.memory_json["deep_analysis"] == "新分析"

    def test_empty_username_does_nothing(self, db):
        save_user_profile(db, user_name="")
        assert db.get(UserMemory, "") is None


class TestResetUserProfile:

    def test_clears_all_fields(self, db):
        save_user_profile(db, user_name="carol", mbti="INTJ", zodiac="摩羯座")
        reset_user_profile(db, user_name="carol")
        user = db.get(User, "carol")
        assert user.mbti is None
        assert user.zodiac is None

    def test_memory_json_fields_set_to_none(self, db):
        save_user_profile(db, user_name="carol", mbti="INTJ")
        reset_user_profile(db, user_name="carol")
        mem = db.get(UserMemory, "carol")
        assert mem.memory_json["mbti"] is None
        assert mem.memory_json["bigfive_scores"] is None

    def test_reset_nonexistent_user_creates_record(self, db):
        """不存在的使用者 reset 後應該建立空記錄"""
        reset_user_profile(db, user_name="newuser")
        mem = db.get(UserMemory, "newuser")
        assert mem is not None

    def test_empty_username_does_nothing(self, db):
        reset_user_profile(db, user_name="")
        assert db.get(User, "") is None

"""
result: passed
how to run: \backend> pytest tests/test_memory_and_repo.py -v
output:
==================================== test session starts ====================================
platform win32 -- Python 3.14.4, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\ASUS\Downloads\wep app\Web_APP_Final_Project\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\ASUS\Downloads\wep app\Web_APP_Final_Project\backend
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

===================================== warnings summary ======================================
tests\test_analysis.py:382
  C:\Users\ASUS\Downloads\wep app\Web_APP_Final_Project\backend\tests\test_analysis.py:382: SyntaxWarning: "\W" is an invalid escape sequence. Such sequences will not work in the future. Did you mean "\\W"? A raw string is also an option.
    platform win32 -- Python 3.14.4, pytest-9.0.3, pluggy-1.6.0 -- \Web_APP_Final_Project\backend\.venv\Scripts\python.exe

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=============================== 28 passed, 1 warning in 0.21s ===============================
"""