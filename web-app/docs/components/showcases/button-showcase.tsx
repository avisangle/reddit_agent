import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2, Mail, Download, Plus, Trash2, Settings } from "lucide-react"

export function ButtonShowcase() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight mb-2">Buttons</h2>
        <p className="text-muted-foreground text-lg">
          Displays a button or a component that looks like a button.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Variants</CardTitle>
            <CardDescription>Different button styles for various contexts</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Button>Default</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="link">Link</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Sizes</CardTitle>
            <CardDescription>Buttons come in different sizes</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap items-center gap-3">
            <Button size="lg">Large</Button>
            <Button size="default">Default</Button>
            <Button size="sm">Small</Button>
            <Button size="icon"><Plus /></Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>With Icons</CardTitle>
            <CardDescription>Buttons with leading or trailing icons</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Button>
              <Mail />
              Login with Email
            </Button>
            <Button variant="secondary">
              <Download />
              Download
            </Button>
            <Button variant="outline">
              <Settings />
              Settings
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>States</CardTitle>
            <CardDescription>Loading and disabled states</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-3">
            <Button disabled>
              <Loader2 className="animate-spin" />
              Loading
            </Button>
            <Button disabled>Disabled</Button>
            <Button variant="destructive">
              <Trash2 />
              Delete
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
