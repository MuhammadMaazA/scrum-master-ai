import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";


const suggestions = [
  {
    id: "PROJ-124",
    note: "Missing acceptance criteria. Suggested: Given/When/Then for checkout error handling.",
  },
  { id: "PROJ-207", note: "Possible duplicate of PROJ-198 (login timeout)." },
  { id: "PROJ-233", note: "Low value; stale for 180 days. Consider archive." },
];

export default function BacklogCard() {
  const handleApply = () =>
    toast({ title: "Applied to tracker", description: "Changes queued (demo)." });

  const handleCreate = async (s: { id: string; note: string }) => {
    const { data, error } = await supabase.functions.invoke("jira-create-issue", {
      body: {
        summary: `${s.id}: Backlog suggestion` ,
        description: s.note,
        issueType: "Task",
      },
    });

    if (error) {
      return toast({ title: "Jira create failed", description: error.message, variant: "destructive" });
    }
    toast({ title: "Jira issue created", description: `Key: ${data?.key || ""}` });
  };


  return (
    <Card>
      <CardHeader>
        <CardTitle>Backlog Grooming</CardTitle>
        <CardDescription>AI suggestions for clarity and priority</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {suggestions.map((s) => (
          <div key={s.id} className="rounded-md border p-3">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium">{s.id}</div>
              <Button size="sm" variant="outline" onClick={() => handleCreate(s)}>Create in Jira</Button>
            </div>
            <div className="text-sm text-muted-foreground">{s.note}</div>
          </div>
        ))}
      </CardContent>
      <CardFooter>
        <Button onClick={handleApply}>Apply Selected</Button>
      </CardFooter>
    </Card>
  );
}
