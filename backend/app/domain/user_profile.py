from dataclasses import dataclass, field
from datetime import datetime, timezone

from .test_results import MBTIResult, BigFiveResult, ZodiacResult
from .dark_triad_result import DarkTriadResult


@dataclass
class UserProfile:
    mbti: MBTIResult | None = None
    bigfive: BigFiveResult | None = None
    zodiac: ZodiacResult | None = None
    dark_triad: DarkTriadResult | None = None
    test_date: field(default_factory = utcnow)

    def utcnow() -> datetime:
        return datetime.now(timezone.utc)

    def is_complete(self) -> bool:
        return self.mbti is not None and self.bigfive is not None and self.zodiac is not None
    
    def to_dict(self) -> dict:
        return {
            'mbti': self.mbti.type if self.mbti else None,
            'bigfive': self.bigfive.to_dict() if self.bigfive else None,
            'zodiac': self.zodiac.sign if self.zodiac else None,
            'dark_triad': self.dark_triad.to_dict() if self.dark_triad else None,
            'test_date': self.test_date.isoformat()
        }
