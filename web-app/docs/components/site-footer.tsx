import Link from "next/link";
import { Separator } from "@/components/ui/separator";

const footerLinks = {
  documentation: [
    { name: "Getting Started", href: "/getting-started" },
    { name: "Architecture", href: "/architecture" },
    { name: "Features", href: "/features" },
    { name: "Configuration", href: "/configuration" },
  ],
  resources: [
    { name: "FAQ", href: "/faq" },
    { name: "GitHub", href: "https://github.com/avisangle/reddit_agent", external: true },
  ],
};

export function SiteFooter() {
  return (
    <footer className="border-t bg-muted/30">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="col-span-2 md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xl font-bold">Reddit Agent</span>
            </div>
            <p className="text-sm text-muted-foreground max-w-md">
              A compliance-first, AI-powered Reddit engagement bot with quality scoring,
              intelligent selection, and human-in-the-loop approval.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Documentation</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              {footerLinks.documentation.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="hover:text-foreground transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              {footerLinks.resources.map((link) => (
                <li key={link.href}>
                  {link.external ? (
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-foreground transition-colors"
                    >
                      {link.name}
                    </a>
                  ) : (
                    <Link
                      href={link.href}
                      className="hover:text-foreground transition-colors"
                    >
                      {link.name}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>
        <Separator className="my-8" />
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
          <p>Reddit Agent v2.5 · Built with LangGraph + Gemini 2.5 Flash</p>
          <p>MIT License</p>
        </div>
      </div>
    </footer>
  );
}
