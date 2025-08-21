import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, BarChart, Bar } from "recharts";
import { SEO } from "@/components/SEO";

const velocity = [
  { sprint: "S1", pts: 24 },
  { sprint: "S2", pts: 28 },
  { sprint: "S3", pts: 30 },
  { sprint: "S4", pts: 27 },
  { sprint: "S5", pts: 31 },
];

const burndown = [
  { day: "Mon", remaining: 40, ideal: 40 },
  { day: "Tue", remaining: 35, ideal: 32 },
  { day: "Wed", remaining: 31, ideal: 24 },
  { day: "Thu", remaining: 26, ideal: 16 },
  { day: "Fri", remaining: 18, ideal: 8 },
  { day: "Sat", remaining: 12, ideal: 4 },
  { day: "Sun", remaining: 8, ideal: 0 },
];

export default function Reports() {
  return (
    <>
      <SEO title="Reports – AI Scrum Master" description="Velocity trends, burndown, and AI commentary for stakeholders." />
      <div className="container grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Velocity Trend</CardTitle>
            <CardDescription>Last five sprints</CardDescription>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer>
              <BarChart data={velocity} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
                <XAxis dataKey="sprint" stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" width={30} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ fill: "hsl(var(--muted) / 0.2)" }} contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))" }} />
                <Bar dataKey="pts" fill={`hsl(var(--brand))`} radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Burndown (Current)</CardTitle>
            <CardDescription>Ideal vs actual</CardDescription>
          </CardHeader>
          <CardContent className="h-64">
            <ResponsiveContainer>
              <LineChart data={burndown} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
                <XAxis dataKey="day" stroke="hsl(var(--muted-foreground))" tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" width={30} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ stroke: "hsl(var(--border))" }} contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))" }} />
                <Line type="monotone" dataKey="ideal" stroke="hsl(var(--muted-foreground))" strokeDasharray="4 4" dot={false} />
                <Line type="monotone" dataKey="remaining" stroke={`hsl(var(--brand))`} strokeWidth={2.5} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
