import { Link } from "@tanstack/react-router";
import { Menu } from "lucide-react";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

import { navItems } from "./nav-items";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";

const SIDEBAR_WIDTH = "13.5rem";

function Brand() {
  return (
    <div className="px-4 pb-4 pt-5">
      <Link to="/" className="block">
        <div className="text-sm font-semibold tracking-[0.18em] text-foreground">SPORTZA</div>
        <div className="mt-0.5 text-[11px] leading-tight text-muted-foreground">
          Performance research
        </div>
      </Link>
    </div>
  );
}

function NavLinks({ onNavigate }: { onNavigate?: (() => void) | undefined }) {
  return (
    <nav aria-label="Primary" className="flex flex-col gap-0.5 px-2">
      {navItems.map((item) => (
        <Link
          key={item.to}
          to={item.to}
          {...(item.exact ? { activeOptions: { exact: true } } : {})}
          activeProps={{
            className: "bg-primary text-primary-foreground",
          }}
          inactiveProps={{
            className: "text-muted-foreground hover:bg-accent hover:text-foreground",
          }}
          className="flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-[13px] transition-colors"
          onClick={onNavigate}
        >
          <item.icon className="size-4 shrink-0" aria-hidden />
          <span>{item.label}</span>
        </Link>
      ))}
    </nav>
  );
}

function SidebarBody({ onNavigate }: { onNavigate?: (() => void) | undefined }) {
  return (
    <div className="flex h-full flex-col">
      <Brand />
      <div className="mx-4 border-t border-border" />
      <div className="flex-1 overflow-y-auto py-3">
        <NavLinks onNavigate={onNavigate} />
      </div>
      <div className="px-4 pb-4 text-[11px] leading-relaxed text-muted-foreground">
        Non-medical training analytics. Not a diagnostic tool.
      </div>
    </div>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Skip link for keyboard users */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-sm focus:text-primary-foreground"
      >
        Skip to content
      </a>

      {/* Desktop sidebar */}
      <div
        className="peer hidden lg:block"
        style={{ "--sidebar-width": SIDEBAR_WIDTH } as React.CSSProperties}
      >
        <div className="w-[var(--sidebar-width)] bg-transparent" />
        <aside className="fixed inset-y-0 left-0 z-10 w-[var(--sidebar-width)] border-r border-sidebar-border bg-sidebar">
          <SidebarBody />
        </aside>
      </div>

      <div className="lg:pl-[var(--sidebar-width)]">
        {/* Mobile top bar */}
        <header className="sticky top-0 z-20 flex h-12 items-center gap-2 border-b border-border bg-background/95 px-3 backdrop-blur lg:hidden">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="size-8" aria-label="Open navigation">
                <Menu className="size-4" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64 bg-sidebar p-0">
              <SheetHeader className="sr-only">
                <SheetTitle>Navigation</SheetTitle>
              </SheetHeader>
              <SidebarBody />
            </SheetContent>
          </Sheet>
          <Link to="/" className="text-sm font-semibold tracking-[0.18em]">
            SPORTZA
          </Link>
        </header>

        <main id="main-content" className="min-h-[calc(100vh-3rem)] lg:min-h-screen">
          {children}
        </main>
      </div>
    </div>
  );
}
