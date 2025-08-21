import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";


export default function StandupCard() {
  const handleGenerate = () =>
    toast({ title: "Standup", description: "Generated summary (demo)." });

  const handleShare = async () => {
    const text = [
      "Daily Standup",
      "Yesterday: Payment module finished; DB bug resolved.",
      "Today: Cart UI begins; API integration in progress.",
      "Blockers: Awaiting checkout UX assets.",
    ].join("\n- ");

    const { data, error } = await supabase.functions.invoke("slack-post", {
      body: { channel: "test", text: `- ${text}` },
    });

    if (error) {
      return toast({ title: "Slack post failed", description: error.message, variant: "destructive" });
    }
    toast({ title: "Shared to Slack", description: `Posted to #test (ts: ${data?.ts || "ok"})` });
  };


  return (
    <Card>
      <CardHeader>
        <CardTitle>Daily Standup</CardTitle>
        <CardDescription>Summaries, blockers, and next steps</CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="list-disc space-y-1 pl-5 text-sm">
          <li>Yesterday: Payment module finished; DB bug resolved.</li>
          <li>Today: Cart UI begins; API integration in progress.</li>
          <li>Blockers: Awaiting checkout UX assets.</li>
        </ul>
      </CardContent>
      <CardFooter className="justify-between">
        <Button variant="outline" onClick={handleGenerate}>Generate Summary</Button>
        <Button onClick={handleShare}>Share to Slack (#test)</Button>
      </CardFooter>

    </Card>
  );
}
