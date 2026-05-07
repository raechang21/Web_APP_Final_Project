import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { PageShell, SectionHero } from "@/components/layout/PageShell";

export default function NotFound() {
  return (
    <PageShell>
      <SectionHero
        eyebrow="404"
        title="這個路由在 React 版裡還不存在。"
        description="如果你是從舊 Flask 模板跳過來，代表還有某個路由或 redirect 沒完全替換乾淨。"
        actions={
          <Link to="/">
            <Button>回到 Welcome</Button>
          </Link>
        }
      />
    </PageShell>
  );
}
