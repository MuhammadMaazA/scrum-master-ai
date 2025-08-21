import { useState, useMemo, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "@/hooks/use-toast";
import { SEO } from "@/components/SEO";
import { supabase } from "@/integrations/supabase/client";

const initial = [
  { id: 1, name: "Alice" },
  { id: 2, name: "Bob" },
  { id: 3, name: "Carlos" },
  { id: 4, name: "Dana" },
];

export default function Standups() {
  const [people] = useState(initial);
  const [currentIdx, setCurrentIdx] = useState<number | null>(null);
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [assignee, setAssignee] = useState("");
  const [channels, setChannels] = useState<{ id: string; name: string; is_private?: boolean }[]>([]);
  const [loadingChannels, setLoadingChannels] = useState(false);
  const [channel, setChannel] = useState<string>(() => localStorage.getItem("slackChannel") || "test");

  const current = useMemo(() => (currentIdx !== null ? people[currentIdx] : null), [currentIdx, people]);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        setLoadingChannels(true);
        const { data, error } = await supabase.functions.invoke("slack-channels");
        if (error) {
          console.error("slack-channels error", error);
        } else if (mounted) {
          setChannels(data?.channels || []);
        }
      } catch (e) {
        console.error("slack-channels exception", e);
      } finally {
        setLoadingChannels(false);
      }
    };
    load();
    return () => {
      mounted = false;
    };
  }, []);

  const start = () => {
    setCurrentIdx(0);
    toast({ title: "Standup", description: `Round-robin started. ${people[0].name}, your turn.` });
  };
  const next = () => {
    if (currentIdx === null) return;
    const nextIdx = (currentIdx + 1) % people.length;
    setCurrentIdx(nextIdx);
    toast({ title: "Standup", description: `${people[nextIdx].name}, your turn to update.` });
  };

  const createFollowUp = () => {
    setOpen(false);
    toast({ title: "Follow-up created", description: `“${title}” assigned to ${assignee || "Unassigned"} (demo).` });
    setTitle("");
    setAssignee("");
  };

  const handleShare = async () => {
    const text = [
      "Daily Standup",
      "Yesterday: Payment module finished; DB bug resolved.",
      "Today: Cart UI begins; API integration in progress.",
      "Blockers: Awaiting checkout UX assets.",
    ].join("\n- ");

    const { data, error } = await supabase.functions.invoke("slack-post", {
      body: { channel, text: `- ${text}` },
    });

    if (error) {
      return toast({ title: "Slack post failed", description: error.message, variant: "destructive" });
    }
    toast({ title: "Shared to Slack", description: `Posted to #${channel} (ts: ${data?.ts || "ok"})` });
  };
  return (
    <>
      <SEO title="Standups – AI Scrum Master" description="Coordinate daily standups with round-robin prompts and create follow-up tickets." />
      <div className="container space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Round-robin Facilitator</CardTitle>
            <CardDescription>Ping teammates in order to keep standups on time.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {people.map((p, i) => (
                <span
                  key={p.id}
                  className={`rounded-full border px-3 py-1 text-sm ${currentIdx === i ? "bg-primary text-primary-foreground" : ""}`}
                >
                  {p.name}
                </span>
              ))}
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Button variant="hero" onClick={start}>Start</Button>
              <Button variant="outline" onClick={next}>Next</Button>
              <div className="flex items-center gap-2">
                <Label className="text-sm">Channel</Label>
                <Select value={channel} onValueChange={(val) => { setChannel(val); localStorage.setItem("slackChannel", val); }}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder={loadingChannels ? "Loading..." : "Select channel"} />
                  </SelectTrigger>
                  <SelectContent className="z-50">
                    {channels.map((c) => (
                      <SelectItem key={c.id} value={c.name}>
                        {c.name}{c.is_private ? " (private)" : ""}
                      </SelectItem>
                    ))}
                    {!channels.length && <SelectItem value="test">test</SelectItem>}
                  </SelectContent>
                </Select>
              </div>
              <Button onClick={handleShare}>Share to Slack (#{channel})</Button>
              <Dialog open={open} onOpenChange={setOpen}>
                <DialogTrigger asChild>
                  <Button>Create follow-up</Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Create follow-up ticket</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-3 py-2">
                    <div className="space-y-1">
                      <Label htmlFor="title">Title</Label>
                      <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Design needed for checkout page" />
                    </div>
                    <div className="space-y-1">
                      <Label htmlFor="assignee">Assignee</Label>
                      <Input id="assignee" value={assignee} onChange={(e) => setAssignee(e.target.value)} placeholder="@designer" />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button onClick={createFollowUp}>Create (demo)</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
            {current && <p className="text-sm text-muted-foreground">Current speaker: {current.name}</p>}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
