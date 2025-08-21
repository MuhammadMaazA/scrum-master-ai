import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slack, KanbanSquare } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { SEO } from "@/components/SEO";
import { supabase } from "@/integrations/supabase/client";

export default function Settings() {
  const connectSlack = async () => {
    const { data, error } = await supabase.functions.invoke("slack-check");
    if (error) return toast({ title: "Slack connection failed", description: error.message, variant: "destructive" });
    toast({ title: "Slack connected", description: `Workspace: ${data?.team} – User: ${data?.user}` });
  };

  const connectJira = async () => {
    const { data, error } = await supabase.functions.invoke("jira-check");
    if (error) return toast({ title: "Jira connection failed", description: error.message, variant: "destructive" });
    toast({ title: "Jira connected", description: `Hello ${data?.displayName}` });
  };

  return (
    <>
      <SEO title="Settings – AI Scrum Master" description="Manage integrations, schedules, and AI tone preferences." />
      <div className="container grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Integrations</CardTitle>
            <CardDescription>Connect the tools you use daily</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <Button variant="outline" onClick={connectSlack}><Slack className="mr-2 h-4 w-4" /> Connect Slack</Button>
            <Button variant="outline" onClick={connectJira}><KanbanSquare className="mr-2 h-4 w-4" /> Connect Jira/Trello</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Preferences</CardTitle>
            <CardDescription>Tone and summary depth</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            Coming soon: choose tone (formal, concise) and summary length.
          </CardContent>
        </Card>
      </div>
    </>
  );
}
