import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import { SEO } from "@/components/SEO";
import { supabase } from "@/integrations/supabase/client";


const items = [
  { id: "PROJ-124", title: "Checkout error handling", hint: "Add acceptance criteria (Given/When/Then)", type: "Needs Detail" },
  { id: "PROJ-207", title: "Login timeout bug", hint: "Possible duplicate of PROJ-198", type: "Duplicate?" },
  { id: "PROJ-233", title: "Legacy cleanup", hint: "Stale 180 days. Consider archive.", type: "Low Value" },
];

export default function Backlog() {
  const apply = () => toast({ title: "Applied to tracker", description: "Edits queued (demo)." });
  const createIssue = async (it: { id: string; title: string; hint: string }) => {
    const { data, error } = await supabase.functions.invoke("jira-create-issue", {
      body: {
        summary: `${it.id}: ${it.title}`,
        description: it.hint,
        issueType: "Task",
      },
    });
    if (error) return toast({ title: "Jira create failed", description: error.message, variant: "destructive" });
    toast({ title: "Jira issue created", description: `Key: ${data?.key || ""}` });
  };


  return (
    <>
      <SEO title="Backlog – AI Scrum Master" description="Groom backlog with AI suggestions: clarify, dedupe, and prioritize faster." />
      <div className="container space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Backlog Refinement</CardTitle>
            <CardDescription>AI suggestions for clarity, duplicates, and prioritization</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {items.map((it) => (
              <div key={it.id} className="rounded-md border p-3">
                <div className="flex items-center justify-between">
                  <div className="text-sm font-medium">{it.id} — {it.title}</div>
                  <div className="flex items-center gap-2">
                    <span className="rounded-full bg-secondary px-2 py-0.5 text-xs">{it.type}</span>
                    <Button size="sm" variant="outline" onClick={() => createIssue(it)}>Create in Jira</Button>
                  </div>
                </div>
                <div className="text-sm text-muted-foreground">{it.hint}</div>
              </div>
            ))}
            <div className="pt-2">
              <Button onClick={apply}>Apply Selected</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
