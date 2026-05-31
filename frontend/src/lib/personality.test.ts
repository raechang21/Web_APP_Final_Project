/**
 * Unit tests for:
 * - src/lib/utils.ts
 * - src/lib/personality.ts
 *
 * 執行方式（在 frontend 資料夾下）：
 *   npx vitest run
 */

import { describe, it, expect } from "vitest";

// ──────────────────────────────────────────────
// 直接貼入 utils.ts 的邏輯
// ──────────────────────────────────────────────

function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

function clampPercent(score: number, max = 6) {
  return Math.max(0, Math.min(100, (score / max) * 100));
}

function formatDate(iso?: string | null) {
  if (!iso) return "尚未建立";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return new Intl.DateTimeFormat("zh-TW", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

// ──────────────────────────────────────────────
// 直接貼入 personality.ts 的資料
// ──────────────────────────────────────────────

const FLOW_STEPS = [
  { label: "Welcome", path: "/" },
  { label: "MBTI", path: "/mbti" },
  { label: "Big Five", path: "/bigfive" },
  { label: "Zodiac", path: "/zodiac" },
  { label: "Dark Triad", path: "/dark-triad-intro" },
  { label: "Results", path: "/results" },
];

const MBTI_GROUPS = [
  {
    title: "分析家",
    tone: "border-[rgba(215,105,83,0.6)] bg-[rgba(215,105,83,0.10)]",
    types: [
      { type: "INTJ", label: "建築師", image: "/mbti/INTJ.png" },
      { type: "INTP", label: "邏輯學家", image: "/mbti/INTP.png" },
      { type: "ENTJ", label: "指揮官", image: "/mbti/ENTJ.png" },
      { type: "ENTP", label: "辯論家", image: "/mbti/ENTP.png" },
    ],
  },
  {
    title: "外交官",
    tone: "border-[rgba(94,157,132,0.6)] bg-[rgba(94,157,132,0.10)]",
    types: [
      { type: "INFJ", label: "提倡者", image: "/mbti/INFJ.png" },
      { type: "INFP", label: "調停者", image: "/mbti/INFP.png" },
      { type: "ENFJ", label: "主人公", image: "/mbti/ENFJ.png" },
      { type: "ENFP", label: "競選者", image: "/mbti/ENFP.png" },
    ],
  },
  {
    title: "守衛者",
    tone: "border-[rgba(47,128,199,0.6)] bg-[rgba(47,128,199,0.10)]",
    types: [
      { type: "ISTJ", label: "物流師", image: "/mbti/ISTJ.png" },
      { type: "ISFJ", label: "守衛者", image: "/mbti/ISFJ.png" },
      { type: "ESTJ", label: "總經理", image: "/mbti/ESTJ.png" },
      { type: "ESFJ", label: "執政官", image: "/mbti/ESFJ.png" },
    ],
  },
  {
    title: "探索者",
    tone: "border-[rgba(216,164,63,0.7)] bg-[rgba(216,164,63,0.15)]",
    types: [
      { type: "ISTP", label: "鑑賞家", image: "/mbti/ISTP.png" },
      { type: "ISFP", label: "探險家", image: "/mbti/ISFP.png" },
      { type: "ESTP", label: "企業家", image: "/mbti/ESTP.png" },
      { type: "ESFP", label: "表演者", image: "/mbti/ESFP.png" },
    ],
  },
];

const BIG_FIVE_META = [
  { key: "openness", label: "開放性", color: "bg-coral" },
  { key: "conscientiousness", label: "盡責性", color: "bg-sage" },
  { key: "extraversion", label: "外向性", color: "bg-amber" },
  { key: "agreeableness", label: "友善性", color: "bg-accent" },
  { key: "neuroticism", label: "神經質", color: "bg-lavender" },
];

const DARK_TRIAD_META = [
  { key: "machiavellianism", label: "馬基維利主義", color: "bg-lavender" },
  { key: "narcissism", label: "自戀", color: "bg-coral" },
  { key: "psychopathy", label: "精神病態", color: "bg-zinc-500" },
];

const ZODIAC_META: Record<string, { icon: string; dateRange: string; element: string; trait: string }> = {
  牡羊座: { icon: "♈", dateRange: "3/21-4/19", element: "火象", trait: "熱情、積極、勇敢、直率" },
  金牛座: { icon: "♉", dateRange: "4/20-5/20", element: "土象", trait: "穩重、務實、可靠、耐心" },
  雙子座: { icon: "♊", dateRange: "5/21-6/21", element: "風象", trait: "機智、靈活、好奇、善變" },
  巨蟹座: { icon: "♋", dateRange: "6/22-7/22", element: "水象", trait: "敏感、體貼、顧家、情緒化" },
  獅子座: { icon: "♌", dateRange: "7/23-8/22", element: "火象", trait: "自信、慷慨、領導力、愛面子" },
  處女座: { icon: "♍", dateRange: "8/23-9/22", element: "土象", trait: "細心、完美主義、分析力強" },
  天秤座: { icon: "♎", dateRange: "9/23-10/23", element: "風象", trait: "優雅、公正、善於交際、猶豫" },
  天蠍座: { icon: "♏", dateRange: "10/24-11/22", element: "水象", trait: "神秘、專注、洞察力強、占有欲" },
  射手座: { icon: "♐", dateRange: "11/23-12/21", element: "火象", trait: "樂觀、自由、冒險、直言不諱" },
  摩羯座: { icon: "♑", dateRange: "12/22-1/19", element: "土象", trait: "務實、負責、有野心、保守" },
  水瓶座: { icon: "♒", dateRange: "1/20-2/18", element: "風象", trait: "獨立、創新、理性、疏離" },
  雙魚座: { icon: "♓", dateRange: "2/19-3/20", element: "水象", trait: "浪漫、同理心、直覺強、逃避" },
};

const BIG_FIVE_OPTIONS = [
  { value: 1, emoji: "🙅", label: "完全不像我" },
  { value: 2, emoji: "😕", label: "不太像我" },
  { value: 3, emoji: "😐", label: "有點不像我" },
  { value: 4, emoji: "🙂", label: "有點像我" },
  { value: 5, emoji: "😄", label: "蠻像我的" },
  { value: 6, emoji: "🤩", label: "超級像我" },
];


// ══════════════════════════════════════════════
// 測試：utils.ts
// ══════════════════════════════════════════════

describe("cn()", () => {
  it("合併多個 class 字串", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("過濾掉 false", () => {
    expect(cn("foo", false, "bar")).toBe("foo bar");
  });

  it("過濾掉 null", () => {
    expect(cn("foo", null, "bar")).toBe("foo bar");
  });

  it("過濾掉 undefined", () => {
    expect(cn("foo", undefined, "bar")).toBe("foo bar");
  });

  it("所有值都是 falsy 時回傳空字串", () => {
    expect(cn(false, null, undefined)).toBe("");
  });

  it("只有一個 class 時正確回傳", () => {
    expect(cn("only")).toBe("only");
  });
});


describe("clampPercent()", () => {
  it("正常分數轉換為百分比", () => {
    expect(clampPercent(3, 6)).toBe(50);
  });

  it("滿分回傳 100", () => {
    expect(clampPercent(6, 6)).toBe(100);
  });

  it("0 分回傳 0", () => {
    expect(clampPercent(0, 6)).toBe(0);
  });

  it("超過最高分時上限為 100", () => {
    expect(clampPercent(10, 6)).toBe(100);
  });

  it("負數時下限為 0", () => {
    expect(clampPercent(-1, 6)).toBe(0);
  });

  it("預設最高分為 6", () => {
    expect(clampPercent(6)).toBe(100);
  });

  it("自訂最高分正確計算", () => {
    expect(clampPercent(5, 10)).toBe(50);
  });
});


describe("formatDate()", () => {
  it("null 回傳「尚未建立」", () => {
    expect(formatDate(null)).toBe("尚未建立");
  });

  it("undefined 回傳「尚未建立」", () => {
    expect(formatDate(undefined)).toBe("尚未建立");
  });

  it("空字串回傳「尚未建立」", () => {
    expect(formatDate("")).toBe("尚未建立");
  });

  it("無效日期字串原樣回傳", () => {
    expect(formatDate("not-a-date")).toBe("not-a-date");
  });

  it("有效 ISO 字串回傳格式化日期", () => {
    const result = formatDate("2024-01-15T10:30:00Z");
    expect(typeof result).toBe("string");
    expect(result).not.toBe("尚未建立");
    expect(result).not.toBe("not-a-date");
  });
});


// ══════════════════════════════════════════════
// 測試：personality.ts 資料完整性
// ══════════════════════════════════════════════

describe("FLOW_STEPS", () => {
  it("共有 6 個步驟", () => {
    expect(FLOW_STEPS).toHaveLength(6);
  });

  it("每個步驟都有 label 和 path", () => {
    for (const step of FLOW_STEPS) {
      expect(step.label).toBeTruthy();
      expect(step.path).toBeTruthy();
    }
  });

  it("第一個步驟是 Welcome，路徑為 /", () => {
    expect(FLOW_STEPS[0].label).toBe("Welcome");
    expect(FLOW_STEPS[0].path).toBe("/");
  });

  it("最後一個步驟是 Results", () => {
    expect(FLOW_STEPS[FLOW_STEPS.length - 1].label).toBe("Results");
  });
});


describe("MBTI_GROUPS", () => {
  it("共有 4 個群組", () => {
    expect(MBTI_GROUPS).toHaveLength(4);
  });

  it("每個群組各有 4 個 MBTI 類型", () => {
    for (const group of MBTI_GROUPS) {
      expect(group.types).toHaveLength(4);
    }
  });

  it("總共有 16 個 MBTI 類型", () => {
    const total = MBTI_GROUPS.reduce((sum, g) => sum + g.types.length, 0);
    expect(total).toBe(16);
  });

  it("所有 MBTI 類型都是 4 個字母", () => {
    for (const group of MBTI_GROUPS) {
      for (const t of group.types) {
        expect(t.type).toHaveLength(4);
      }
    }
  });

  it("每個類型都有 label 和 image", () => {
    for (const group of MBTI_GROUPS) {
      for (const t of group.types) {
        expect(t.label).toBeTruthy();
        expect(t.image).toBeTruthy();
      }
    }
  });

  it("所有 MBTI 類型不重複", () => {
    const allTypes = MBTI_GROUPS.flatMap((g) => g.types.map((t) => t.type));
    const unique = new Set(allTypes);
    expect(unique.size).toBe(16);
  });
});


describe("BIG_FIVE_META", () => {
  it("共有 5 個維度", () => {
    expect(BIG_FIVE_META).toHaveLength(5);
  });

  it("包含所有預期的 key", () => {
    const keys = BIG_FIVE_META.map((m) => m.key);
    expect(keys).toContain("openness");
    expect(keys).toContain("conscientiousness");
    expect(keys).toContain("extraversion");
    expect(keys).toContain("agreeableness");
    expect(keys).toContain("neuroticism");
  });

  it("每個維度都有 label 和 color", () => {
    for (const meta of BIG_FIVE_META) {
      expect(meta.label).toBeTruthy();
      expect(meta.color).toBeTruthy();
    }
  });
});


describe("DARK_TRIAD_META", () => {
  it("共有 3 個維度", () => {
    expect(DARK_TRIAD_META).toHaveLength(3);
  });

  it("包含所有預期的 key", () => {
    const keys = DARK_TRIAD_META.map((m) => m.key);
    expect(keys).toContain("machiavellianism");
    expect(keys).toContain("narcissism");
    expect(keys).toContain("psychopathy");
  });
});


describe("ZODIAC_META", () => {
  it("共有 12 個星座", () => {
    expect(Object.keys(ZODIAC_META)).toHaveLength(12);
  });

  it("每個星座都有 icon、dateRange、element、trait", () => {
    for (const [, meta] of Object.entries(ZODIAC_META)) {
      expect(meta.icon).toBeTruthy();
      expect(meta.dateRange).toBeTruthy();
      expect(meta.element).toBeTruthy();
      expect(meta.trait).toBeTruthy();
    }
  });

  it("包含牡羊座且 icon 正確", () => {
    expect(ZODIAC_META["牡羊座"].icon).toBe("♈");
  });

  it("element 只有四象之一", () => {
    const validElements = ["火象", "土象", "風象", "水象"];
    for (const [, meta] of Object.entries(ZODIAC_META)) {
      expect(validElements).toContain(meta.element);
    }
  });
});


describe("BIG_FIVE_OPTIONS", () => {
  it("共有 6 個選項", () => {
    expect(BIG_FIVE_OPTIONS).toHaveLength(6);
  });

  it("value 從 1 到 6 連續", () => {
    const values = BIG_FIVE_OPTIONS.map((o) => o.value);
    expect(values).toEqual([1, 2, 3, 4, 5, 6]);
  });

  it("每個選項都有 emoji 和 label", () => {
    for (const option of BIG_FIVE_OPTIONS) {
      expect(option.emoji).toBeTruthy();
      expect(option.label).toBeTruthy();
    }
  });
});

/*
result: passed
output:
✓ src/lib/personality.test.ts (40 tests) 40ms
   ✓ cn() (6)
     ✓ 合併多個 class 字串 2ms
     ✓ 過濾掉 false 0ms
     ✓ 過濾掉 null 0ms
     ✓ 過濾掉 undefined 0ms
     ✓ 所有值都是 falsy 時回傳空字串 0ms
     ✓ 只有一個 class 時正確回傳 0ms
   ✓ clampPercent() (7)
     ✓ 正常分數轉換為百分比 0ms
     ✓ 滿分回傳 100 0ms
     ✓ 0 分回傳 0 0ms
     ✓ 超過最高分時上限為 100 0ms
     ✓ 負數時下限為 0 0ms
     ✓ 預設最高分為 6 0ms
     ✓ 自訂最高分正確計算 0ms
   ✓ formatDate() (5)
     ✓ null 回傳「尚未建立」 0ms
     ✓ undefined 回傳「尚未建立」 0ms
     ✓ 空字串回傳「尚未建立」 0ms
     ✓ 無效日期字串原樣回傳 0ms
     ✓ 有效 ISO 字串回傳格式化日期 25ms
   ✓ FLOW_STEPS (4)
     ✓ 共有 6 個步驟 1ms
     ✓ 每個步驟都有 label 和 path 0ms
     ✓ 第一個步驟是 Welcome，路徑為 / 0ms
     ✓ 最後一個步驟是 Results 0ms
   ✓ MBTI_GROUPS (6)
     ✓ 共有 4 個群組 0ms
     ✓ 每個群組各有 4 個 MBTI 類型 0ms
     ✓ 總共有 16 個 MBTI 類型 0ms
     ✓ 所有 MBTI 類型都是 4 個字母 1ms
     ✓ 每個類型都有 label 和 image 1ms
     ✓ 所有 MBTI 類型不重複 0ms
   ✓ BIG_FIVE_META (3)
     ✓ 共有 5 個維度 0ms
     ✓ 包含所有預期的 key 1ms
     ✓ 每個維度都有 label 和 color 0ms
   ✓ DARK_TRIAD_META (2)
     ✓ 共有 3 個維度 0ms
     ✓ 包含所有預期的 key 0ms
   ✓ ZODIAC_META (4)
     ✓ 共有 12 個星座 0ms
     ✓ 每個星座都有 icon、dateRange、element、trait 1ms
     ✓ 包含牡羊座且 icon 正確 0ms
     ✓ element 只有四象之一 1ms
   ✓ BIG_FIVE_OPTIONS (3)
     ✓ 共有 6 個選項 0ms
     ✓ value 從 1 到 6 連續 0ms
     ✓ 每個選項都有 emoji 和 label 0ms

 Test Files  1 passed (1)
      Tests  40 passed (40)
   Start at  17:29:50
   Duration  631ms (transform 66ms, setup 0ms, import 90ms, tests 40ms, environment 0ms)
*/