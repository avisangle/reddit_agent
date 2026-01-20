import { Alert, AlertDescription } from "@/components/ui/alert"
import { Info, AlertTriangle, CheckCircle, XCircle } from "lucide-react"
import { cn } from "@/lib/utils"

type CalloutVariant = "info" | "warning" | "success" | "error"

interface CalloutProps {
  variant?: CalloutVariant
  children: React.ReactNode
  className?: string
}

const icons = {
  info: Info,
  warning: AlertTriangle,
  success: CheckCircle,
  error: XCircle,
}

const styles = {
  info: "border-blue-500 bg-blue-50 text-blue-900 [&>svg]:text-blue-500",
  warning: "border-yellow-500 bg-yellow-50 text-yellow-900 [&>svg]:text-yellow-500",
  success: "border-green-500 bg-green-50 text-green-900 [&>svg]:text-green-500",
  error: "border-red-500 bg-red-50 text-red-900 [&>svg]:text-red-500",
}

export function Callout({ variant = "info", children, className }: CalloutProps) {
  const Icon = icons[variant]

  return (
    <Alert className={cn("border-l-4", styles[variant], className)}>
      <Icon className="h-4 w-4" />
      <AlertDescription className="[&_p]:m-0 [&_strong]:font-semibold">
        {children}
      </AlertDescription>
    </Alert>
  )
}
