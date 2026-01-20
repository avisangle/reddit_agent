import { Layers } from "lucide-react"
import { Separator } from "@/components/ui/separator"

export function Footer() {
  return (
    <footer className="border-t bg-muted/30">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <Layers className="h-4 w-4 text-primary-foreground" />
              </div>
              <span className="font-semibold">Design System</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Beautiful, accessible components for modern web applications.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Components</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#buttons" className="hover:text-foreground transition-colors">Buttons</a></li>
              <li><a href="#cards" className="hover:text-foreground transition-colors">Cards</a></li>
              <li><a href="#forms" className="hover:text-foreground transition-colors">Forms</a></li>
              <li><a href="#table" className="hover:text-foreground transition-colors">Tables</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-foreground transition-colors">Documentation</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">GitHub</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Figma</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Changelog</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Community</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-foreground transition-colors">Discord</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Twitter</a></li>
              <li><a href="#" className="hover:text-foreground transition-colors">Contributing</a></li>
            </ul>
          </div>
        </div>
        <Separator className="my-8" />
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
          <p>Built with shadcn/ui, Radix UI, and Tailwind CSS.</p>
          <p>MIT License</p>
        </div>
      </div>
    </footer>
  )
}
