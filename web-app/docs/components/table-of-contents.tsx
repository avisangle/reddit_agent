"use client";

import { useEffect, useState, useCallback } from "react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { List } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

interface TocItem {
  id: string;
  text: string;
  level: number;
}

interface TableOfContentsProps {
  className?: string;
}

export function TableOfContents({ className }: TableOfContentsProps) {
  const [headings, setHeadings] = useState<TocItem[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const pathname = usePathname();

  const collectHeadings = useCallback(() => {
    // Small delay to ensure DOM is fully rendered
    setTimeout(() => {
      const items: TocItem[] = [];
      const seen = new Set<string>();

      // Query only h1 and h2 elements with IDs (skip h3 to keep list short)
      const elements = document.querySelectorAll("h1[id], h2[id]");
      
      elements.forEach((element) => {
        const id = element.id;
        if (id && !seen.has(id)) {
          seen.add(id);
          items.push({
            id,
            text: element.textContent?.trim() || "",
            level: element.tagName === "H1" ? 1 : 2,
          });
        }
      });

      setHeadings(items);
    }, 100);
  }, []);

  // Re-collect headings when pathname changes
  useEffect(() => {
    collectHeadings();
  }, [pathname, collectHeadings]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        });
      },
      { rootMargin: "-80px 0px -80% 0px" }
    );

    headings.forEach((heading) => {
      const element = document.getElementById(heading.id);
      if (element) observer.observe(element);
    });

    return () => observer.disconnect();
  }, [headings]);

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      const yOffset = -80;
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
      window.scrollTo({ top: y, behavior: "smooth" });
    }
  };

  if (headings.length === 0) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className={cn("gap-2", className)}>
          <List className="h-4 w-4" />
          <span className="hidden sm:inline">On this page</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64 max-h-80 overflow-y-auto">
        {headings.map((heading) => (
          <DropdownMenuItem
            key={heading.id}
            onClick={() => scrollToSection(heading.id)}
            className={cn(
              "cursor-pointer",
              activeId === heading.id && "bg-accent"
            )}
          >
            <span className="truncate">{heading.text}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function SidebarTableOfContents({ className }: TableOfContentsProps) {
  const [headings, setHeadings] = useState<TocItem[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const pathname = usePathname();

  const collectHeadings = useCallback(() => {
    setTimeout(() => {
      const items: TocItem[] = [];
      const seen = new Set<string>();

      // Query only h1 and h2 elements with IDs (skip h3 to keep list short)
      const elements = document.querySelectorAll("h1[id], h2[id]");
      
      elements.forEach((element) => {
        const id = element.id;
        if (id && !seen.has(id)) {
          seen.add(id);
          items.push({
            id,
            text: element.textContent?.trim() || "",
            level: element.tagName === "H1" ? 1 : 2,
          });
        }
      });

      setHeadings(items);
    }, 100);
  }, []);

  useEffect(() => {
    collectHeadings();
  }, [pathname, collectHeadings]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        });
      },
      { rootMargin: "-80px 0px -80% 0px" }
    );

    headings.forEach((heading) => {
      const element = document.getElementById(heading.id);
      if (element) observer.observe(element);
    });

    return () => observer.disconnect();
  }, [headings]);

  if (headings.length === 0) return null;

  return (
    <nav className={cn("space-y-1", className)}>
      <p className="font-medium text-sm mb-3">On this page</p>
      {headings.map((heading) => (
        <a
          key={heading.id}
          href={`#${heading.id}`}
          className={cn(
            "block text-sm py-1 transition-colors hover:text-foreground",
            activeId === heading.id
              ? "text-foreground font-medium"
              : "text-muted-foreground"
          )}
        >
          {heading.text}
        </a>
      ))}
    </nav>
  );
}
