import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";

const picks = [
  { id: "PROJ-310", title: "Checkout: basic flow", pts: 8 },
  { id: "PROJ-287", title: "Cart UI", pts: 5 },
  { id: "PROJ-299", title: "Payment API integration", pts: 8 },
];

export default function SprintPlanningCard() {
  const total = picks.reduce((a, b) => a + b.pts, 0);

  const handleCreate = () =>
    toast({ title: "Sprint created", description: "Applied to tracker (demo)." });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Sprint Planning</CardTitle>
        <CardDescription>Capacity-aware recommendations</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="rounded-md border p-3">
          <div className="text-sm font-medium">Draft Sprint Goal</div>
          <p className="text-sm text-muted-foreground">
            Deliver the core checkout experience: cart UI, payment integration, and basic flow.
          </p>
        </div>
        <div className="space-y-2">
          {picks.map((p) => (
            <div key={p.id} className="flex items-center justify-between rounded-md border p-3 text-sm">
              <div className="font-medium">{p.id}</div>
              <div className="flex-1 px-3 text-muted-foreground">{p.title}</div>
              <div className="rounded-full bg-secondary px-2 py-0.5 text-xs">{p.pts} pts</div>
            </div>
          ))}
          <div className="flex justify-end text-sm text-muted-foreground">Total: {total} pts</div>
        </div>
      </CardContent>
      <CardFooter className="justify-between">
        <Button variant="outline">Adjust Selection</Button>
        <Button onClick={handleCreate}>Create Sprint</Button>
      </CardFooter>
    </Card>
  );
}
