import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Check, Clock, AlertTriangle, X, Zap, Star, TrendingUp } from "lucide-react"

export function BadgeShowcase() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight mb-2">Badges</h2>
        <p className="text-muted-foreground text-lg">
          Displays a badge or a component that looks like a badge.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Variants</CardTitle>
            <CardDescription>Different badge styles for various purposes</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Badge>Default</Badge>
            <Badge variant="secondary">Secondary</Badge>
            <Badge variant="destructive">Destructive</Badge>
            <Badge variant="outline">Outline</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>With Icons</CardTitle>
            <CardDescription>Badges with icons for enhanced meaning</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Badge className="gap-1">
              <Check className="h-3 w-3" />
              Success
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Clock className="h-3 w-3" />
              Pending
            </Badge>
            <Badge variant="destructive" className="gap-1">
              <X className="h-3 w-3" />
              Failed
            </Badge>
            <Badge variant="outline" className="gap-1">
              <AlertTriangle className="h-3 w-3" />
              Warning
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status Indicators</CardTitle>
            <CardDescription>Common use cases for status display</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Badge className="gap-1">
              <Zap className="h-3 w-3" />
              New
            </Badge>
            <Badge variant="secondary" className="gap-1">
              <Star className="h-3 w-3" />
              Featured
            </Badge>
            <Badge variant="outline" className="gap-1">
              <TrendingUp className="h-3 w-3" />
              Trending
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Interactive Badges</CardTitle>
            <CardDescription>Badges as links or buttons</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Badge asChild>
              <a href="#">Clickable Badge</a>
            </Badge>
            <Badge variant="secondary" asChild>
              <a href="#">Link Badge</a>
            </Badge>
            <Badge variant="outline" asChild>
              <a href="#">Outline Link</a>
            </Badge>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
