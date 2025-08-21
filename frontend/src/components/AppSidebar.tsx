import { NavLink } from "react-router-dom";
import { LayoutDashboard, MessagesSquare, KanbanSquare, CalendarCheck2, BarChart3, Settings as SettingsIcon, Bot } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
} from "@/components/ui/sidebar";
import type { LucideIcon } from "lucide-react";

const items: { title: string; url: string; icon: LucideIcon }[] = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Standups", url: "/standups", icon: MessagesSquare },
  { title: "Backlog", url: "/backlog", icon: KanbanSquare },
  { title: "Planning", url: "/planning", icon: CalendarCheck2 },
  { title: "Reports", url: "/reports", icon: BarChart3 },
  { title: "Settings", url: "/settings", icon: SettingsIcon },
];

export function AppSidebar() {
  return (
    <Sidebar collapsible="icon" variant="sidebar">
      <SidebarHeader className="border-b border-sidebar-border p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
            <Bot className="h-4 w-4 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-sidebar-foreground">ScrumMaster AI</span>
            <span className="text-xs text-sidebar-foreground/60">Agile Assistant</span>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent className="gap-0">
        <SidebarGroup className="py-2">
          <SidebarGroupLabel className="px-2 py-2 text-xs font-semibold text-sidebar-foreground/70">
            Navigation
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-1 px-2">
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild className="w-full">
                    <NavLink
                      to={item.url}
                      end
                      className={({ isActive }) =>
                        `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                          isActive
                            ? "bg-sidebar-accent text-sidebar-accent-foreground"
                            : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                        }`
                      }
                    >
                      <item.icon className="h-4 w-4 shrink-0" />
                      <span className="truncate">{item.title}</span>
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
