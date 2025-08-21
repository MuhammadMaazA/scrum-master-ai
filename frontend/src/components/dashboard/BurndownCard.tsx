import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const sample = [
  { day: "Mon", remaining: 40, ideal: 40 },
  { day: "Tue", remaining: 35, ideal: 32 },
  { day: "Wed", remaining: 31, ideal: 24 },
  { day: "Thu", remaining: 26, ideal: 16 },
  { day: "Fri", remaining: 18, ideal: 8 },
  { day: "Sat", remaining: 12, ideal: 4 },
  { day: "Sun", remaining: 8, ideal: 0 },
];

export default function BurndownCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Burndown Chart</CardTitle>
        <CardDescription>Live sprint tracking with AI commentary</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-64 w-full">
          <ResponsiveContainer>
            <LineChart data={sample} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
              <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} />
              <YAxis stroke="hsl(var(--muted-foreground))" width={24} tickLine={false} axisLine={false} />
              <Tooltip cursor={{ stroke: "hsl(var(--border))" }} contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))" }} />
              <Line type="monotone" dataKey="ideal" stroke="hsl(var(--muted-foreground))" strokeDasharray="4 4" dot={false} />
              <Line type="monotone" dataKey="remaining" stroke={`hsl(var(--brand))`} strokeWidth={2.5} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          Insight: Burn rate slightly behind ideal. At current pace, ~20% may spill. Consider descoping or unblocking API integration.
        </p>
      </CardContent>
    </Card>
  );
}
