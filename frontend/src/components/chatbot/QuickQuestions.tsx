import { Button } from "@/components/ui/button";

export function QuickQuestions({
  prompts,
  onSelect,
}: {
  prompts: string[];
  onSelect: (prompt: string) => void;
}) {
  return (
    <div className="space-y-3">
      {prompts.map((prompt) => (
        <Button
          key={prompt}
          className="w-full justify-start rounded-2xl px-4 py-4 text-left text-sm"
          variant="secondary"
          onClick={() => onSelect(prompt)}
        >
          {prompt}
        </Button>
      ))}
    </div>
  );
}
