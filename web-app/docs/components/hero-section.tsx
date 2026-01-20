import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ArrowRight, Sparkles } from "lucide-react"

export function HeroSection() {
  return (
    <section className="py-12 md:py-20">
      <div className="flex flex-col items-center text-center gap-6 max-w-3xl mx-auto">
        <Badge variant="secondary" className="gap-1">
          <Sparkles className="h-3 w-3" />
          Design System v1.0
        </Badge>
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-balance">
          Beautiful UI components built with{" "}
          <span className="text-primary">Radix UI</span> and{" "}
          <span className="text-primary">Tailwind CSS</span>
        </h1>
        <p className="text-lg md:text-xl text-muted-foreground max-w-2xl text-balance">
          A comprehensive collection of accessible, customizable, and production-ready
          components. Copy and paste into your apps and make them your own.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 mt-2">
          <Button size="lg" className="gap-2">
            Browse Components
            <ArrowRight className="h-4 w-4" />
          </Button>
          <Button size="lg" variant="outline">
            View Documentation
          </Button>
        </div>
      </div>
    </section>
  )
}
