import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BIG_FIVE_META, DARK_TRIAD_META, ZODIAC_META } from "@/lib/personality";
import type { SessionData } from "@/types";

export function SidebarSummary({ session }: { session: SessionData }) {
  return (
    <div className="space-y-4">
      <Card className="bg-gradient-to-br from-ink to-stone-800 text-paper">
        <CardContent className="space-y-3">
          <p className="text-xs uppercase tracking-[0.28em] text-stone-300">個人資料</p>
          <h3 className="font-display text-3xl">
            {session.user_name || "尚未命名"}
          </h3>
          <div className="flex flex-wrap gap-2">
            {session.mbti ? <Badge className="bg-white/15 text-white">{session.mbti}</Badge> : null}
            {session.zodiac ? (
              <Badge className="bg-white/15 text-white">
                {ZODIAC_META[session.zodiac]?.icon ?? "⭐"} {session.zodiac}
              </Badge>
            ) : null}
          </div>
        </CardContent>
      </Card>

      {session.bigfive_scores ? (
        <Card>
          <CardContent className="space-y-4">
            <h3 className="font-display text-2xl text-ink">五大人格</h3>
            {BIG_FIVE_META.map(({ key, label }) => (
              <div key={key} className="flex items-center justify-between text-sm">
                <span className="text-stone-600">{label}</span>
                <span className="font-medium text-ink">
                  {session.bigfive_scores?.[key].toFixed(1)}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      ) : null}

      {session.dark_triad_scores ? (
        <Card>
          <CardContent className="space-y-4">
            <h3 className="font-display text-2xl text-ink">黑暗三角</h3>
            {DARK_TRIAD_META.map(({ key, label }) => (
              <div key={key} className="flex items-center justify-between text-sm">
                <span className="text-stone-600">{label}</span>
                <span className="font-medium text-ink">
                  {session.dark_triad_scores?.[key].toFixed(1)}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
