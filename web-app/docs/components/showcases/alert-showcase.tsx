import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { AlertCircle, CheckCircle2, Info, AlertTriangle, Terminal, Rocket } from "lucide-react"

export function AlertShowcase() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight mb-2">Alerts</h2>
        <p className="text-muted-foreground text-lg">
          Displays a callout for user attention.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Default Alert</CardTitle>
            <CardDescription>Standard alert for general information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertTitle>Heads up!</AlertTitle>
              <AlertDescription>
                You can add components to your app using the CLI.
              </AlertDescription>
            </Alert>

            <Alert>
              <Terminal className="h-4 w-4" />
              <AlertTitle>Terminal Command</AlertTitle>
              <AlertDescription>
                <code className="bg-muted px-1.5 py-0.5 rounded text-sm">
                  npx shadcn@latest add button
                </code>
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Destructive Alert</CardTitle>
            <CardDescription>Alert for errors and warnings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Error</AlertTitle>
              <AlertDescription>
                Your session has expired. Please log in again.
              </AlertDescription>
            </Alert>

            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>Warning</AlertTitle>
              <AlertDescription>
                This action cannot be undone. Please proceed with caution.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Contextual Alerts</CardTitle>
            <CardDescription>Various alert styles for different contexts</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <Alert>
              <CheckCircle2 className="h-4 w-4" />
              <AlertTitle>Success!</AlertTitle>
              <AlertDescription>
                Your changes have been saved successfully.
              </AlertDescription>
            </Alert>

            <Alert>
              <Rocket className="h-4 w-4" />
              <AlertTitle>New Feature</AlertTitle>
              <AlertDescription>
                Check out our latest update with improved performance.
              </AlertDescription>
            </Alert>

            <Alert>
              <Info className="h-4 w-4" />
              <AlertTitle>Did you know?</AlertTitle>
              <AlertDescription>
                You can customize these components to match your brand.
              </AlertDescription>
            </Alert>

            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertTitle>Connection Lost</AlertTitle>
              <AlertDescription>
                Unable to connect to the server. Retrying...
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
