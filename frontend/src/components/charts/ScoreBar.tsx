import { Progress } from "@/components/ui/progress";
import { clampPercent } from "@/lib/utils";

export function ScoreBar({
  label,
  score,
  indicatorClassName,
}: {
  label: string;
  score: number;
  indicatorClassName?: string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-ink">{label}</span>
        <span className="text-stone-500">{score.toFixed(1)} / 6.0</span>
      </div>
      <Progress value={clampPercent(score)} indicatorClassName={indicatorClassName} />
    </div>
  );
}
