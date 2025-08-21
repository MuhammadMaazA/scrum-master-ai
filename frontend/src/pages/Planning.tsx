import { useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "@/hooks/use-toast";
import { SEO } from "@/components/SEO";

export default function Planning() {
  const [devs, setDevs] = useState(5);
  const [days, setDays] = useState(10);
  const [holidays, setHolidays] = useState(2);
  const [velocity, setVelocity] = useState(30);
  const capacity = useMemo(() => Math.max(0, devs * (days - holidays)), [devs, days, holidays]);

  const suggest = () => toast({ title: "Sprint plan", description: "Draft selection and goal generated (demo)." });
  const start = () => toast({ title: "Sprint started", description: "Selected issues moved (demo)." });

  return (
    <>
      <SEO title="Sprint Planning – AI Scrum Master" description="Capacity-aware sprint planning with AI recommendations and goals." />
      <div className="container grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Capacity</CardTitle>
            <CardDescription>Team availability and historical velocity</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="devs">Developers</Label>
              <Input id="devs" type="number" value={devs} onChange={(e) => setDevs(Number(e.target.value))} />
            </div>
            <div>
              <Label htmlFor="days">Sprint days</Label>
              <Input id="days" type="number" value={days} onChange={(e) => setDays(Number(e.target.value))} />
            </div>
            <div>
              <Label htmlFor="holidays">Holidays</Label>
              <Input id="holidays" type="number" value={holidays} onChange={(e) => setHolidays(Number(e.target.value))} />
            </div>
            <div>
              <Label htmlFor="velocity">Last sprint velocity (pts)</Label>
              <Input id="velocity" type="number" value={velocity} onChange={(e) => setVelocity(Number(e.target.value))} />
            </div>
            <div className="col-span-2 rounded-md border p-3 text-sm">
              Estimated capacity: <span className="font-medium">{capacity}</span> dev-days · Forecast velocity: <span className="font-medium">{velocity}</span> pts
            </div>
            <div className="col-span-2 flex gap-3">
              <Button variant="hero" onClick={suggest}>Suggest Sprint Plan</Button>
              <Button variant="outline" onClick={start}>Start Sprint</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Draft Plan</CardTitle>
            <CardDescription>Proposed sprint goal and selection</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="rounded-md border p-3">
              <div className="text-sm font-medium">Sprint Goal</div>
              <p className="text-sm text-muted-foreground">Implement core search functionality for the app.</p>
            </div>
            {[{ id: "PROJ-310", title: "Search API endpoints", pts: 8 }, { id: "PROJ-311", title: "Search UI", pts: 5 }, { id: "PROJ-312", title: "Indexing job", pts: 8 }].map(p => (
              <div key={p.id} className="flex items-center justify-between rounded-md border p-3 text-sm">
                <div className="font-medium">{p.id}</div>
                <div className="flex-1 px-3 text-muted-foreground">{p.title}</div>
                <div className="rounded-full bg-secondary px-2 py-0.5 text-xs">{p.pts} pts</div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
