import type {
  BigFiveScores,
  DarkTriadScores,
  MbtiType,
} from "@/types";

export const FLOW_STEPS = [
  { label: "Welcome", path: "/" },
  { label: "MBTI", path: "/mbti" },
  { label: "Big Five", path: "/bigfive" },
  { label: "Zodiac", path: "/zodiac" },
  { label: "Dark Triad", path: "/dark-triad-intro" },
  { label: "Results", path: "/results" },
];


export const MBTI_GROUPS: Array<{
  title: string;
  tone: string;
  types: Array<{ type: MbtiType; label: string; image: string }>;
}> = [
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
      { type: "INFP", label: "調停者", image: "/mbti/INFP.png"},
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


export const BIG_FIVE_META: Array<{
  key: keyof BigFiveScores;
  label: string;
  color: string;
}> = [
  { key: "openness", label: "開放性", color: "bg-coral" },
  { key: "conscientiousness", label: "盡責性", color: "bg-sage" },
  { key: "extraversion", label: "外向性", color: "bg-amber" },
  { key: "agreeableness", label: "友善性", color: "bg-accent" },
  { key: "neuroticism", label: "神經質", color: "bg-lavender" },
];

export const DARK_TRIAD_META: Array<{
  key: keyof DarkTriadScores;
  label: string;
  color: string;
}> = [
  { key: "machiavellianism", label: "馬基維利主義", color: "bg-lavender" },
  { key: "narcissism", label: "自戀", color: "bg-coral" },
  { key: "psychopathy", label: "精神病態", color: "bg-zinc-500" },
];

export const ZODIAC_META: Record<
  string,
  { icon: string; dateRange: string; element: string; trait: string }
> = {
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

export const BIG_FIVE_OPTIONS = [
  { value: 1, emoji: "🙅", label: "完全不像我" },
  { value: 2, emoji: "😕", label: "不太像我" },
  { value: 3, emoji: "😐", label: "有點不像我" },
  { value: 4, emoji: "🙂", label: "有點像我" },
  { value: 5, emoji: "😄", label: "蠻像我的" },
  { value: 6, emoji: "🤩", label: "超級像我" },
];

export const CHATBOT_PROMPTS = [
  "我的 Big Five 裡最突出的特質是什麼？",
  "你覺得我的 MBTI 和 Big Five 哪裡最一致？",
  "我的性格比較適合什麼工作節奏？",
  "如果我最近很焦慮，該怎麼利用自己的特質調整？",
];
