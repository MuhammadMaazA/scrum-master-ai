import { Button } from "@/components/ui/button";
import { SignatureAura } from "@/components/SignatureAura";
import { Sparkles, Slack, Github, KanbanSquare } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";

export default function Hero() {
  const handleGenerate = () =>
    toast({ title: "Standup", description: "Draft summary generated (demo)." });

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
    <section className="relative overflow-hidden rounded-2xl border bg-gradient-to-b from-background to-[hsl(var(--muted))] p-8 md:p-12">
      <SignatureAura />
      <div className="relative z-10 max-w-3xl">
        <div className="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs text-muted-foreground">
          <Sparkles className="h-3.5 w-3.5" />
          Human-in-the-loop AI for Agile teams
        </div>
        <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
          AI Scrum Master Dashboard
        </h1>
        <p className="mt-3 text-muted-foreground">
          Automate standups, backlog grooming, sprint planning and burndown insights — with human oversight.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Button variant="hero" onClick={handleGenerate}>
            Try Standup Summary
          </Button>
          <Button variant="outline" onClick={connectSlack}>
            <Slack className="mr-2 h-4 w-4" /> Connect Slack
          </Button>
          <Button variant="outline" onClick={connectJira}>
            <KanbanSquare className="mr-2 h-4 w-4" /> Connect Jira/Trello
          </Button>
          <Button variant="ghost" asChild>
            <a href="https://github.com" target="_blank" rel="noreferrer">
              <Github className="mr-2 h-4 w-4" /> View on GitHub
            </a>
          </Button>
        </div>
      </div>
    </section>
  );
}
