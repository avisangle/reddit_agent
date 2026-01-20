"use client"

import { cn } from "@/lib/utils"
import { ArrowDown, ArrowRight } from "lucide-react"
import { ReactNode } from "react"

// ============================================
// DiagramContainer - Main wrapper for diagrams
// ============================================
interface DiagramContainerProps {
    children: ReactNode
    title?: string
    className?: string
}

export function DiagramContainer({ children, title, className }: DiagramContainerProps) {
    return (
        <div className={cn(
            "my-6 rounded-xl border border-border bg-secondary/30 p-6 overflow-x-auto",
            className
        )}>
            {title && (
                <div className="text-sm font-medium text-muted-foreground mb-4 text-center">
                    {title}
                </div>
            )}
            {children}
        </div>
    )
}

// ============================================
// DiagramNode - Individual node box
// ============================================
interface DiagramNodeProps {
    children: ReactNode
    icon?: ReactNode
    variant?: "default" | "primary" | "muted"
    size?: "sm" | "md" | "lg"
    className?: string
}

export function DiagramNode({
    children,
    icon,
    variant = "default",
    size = "md",
    className
}: DiagramNodeProps) {
    const variantStyles = {
        default: "bg-card border-border text-foreground",
        primary: "bg-primary/10 border-primary text-primary",
        muted: "bg-muted border-border text-muted-foreground",
    }

    const sizeStyles = {
        sm: "px-2 py-1 text-xs",
        md: "px-3 py-2 text-sm",
        lg: "px-4 py-3 text-base",
    }

    return (
        <div className={cn(
            "flex items-center gap-2 rounded-lg border font-medium transition-colors",
            variantStyles[variant],
            sizeStyles[size],
            className
        )}>
            {icon && <span className="flex-shrink-0">{icon}</span>}
            {children}
        </div>
    )
}

// ============================================
// DiagramFlow - Horizontal or vertical flow
// ============================================
interface DiagramFlowProps {
    children: ReactNode
    direction?: "horizontal" | "vertical"
    showArrows?: boolean
    className?: string
}

export function DiagramFlow({
    children,
    direction = "horizontal",
    showArrows = true,
    className
}: DiagramFlowProps) {
    const directionStyles = {
        horizontal: "flex-row items-center",
        vertical: "flex-col items-center",
    }

    const Arrow = direction === "horizontal" ? ArrowRight : ArrowDown

    // Convert children to array and interleave with arrows
    const childArray = Array.isArray(children) ? children : [children]
    const withArrows: ReactNode[] = []

    childArray.forEach((child, index) => {
        withArrows.push(
            <div key={`child-${index}`}>{child}</div>
        )
        if (showArrows && index < childArray.length - 1) {
            withArrows.push(
                <Arrow
                    key={`arrow-${index}`}
                    className="h-4 w-4 text-muted-foreground flex-shrink-0"
                />
            )
        }
    })

    return (
        <div className={cn(
            "flex gap-2 flex-wrap",
            directionStyles[direction],
            className
        )}>
            {withArrows}
        </div>
    )
}

// ============================================
// DiagramGroup - Labeled group of elements
// ============================================
interface DiagramGroupProps {
    children: ReactNode
    title: string
    description?: string
    className?: string
}

export function DiagramGroup({
    children,
    title,
    description,
    className
}: DiagramGroupProps) {
    return (
        <div className={cn(
            "rounded-xl border border-border bg-card p-4",
            className
        )}>
            <div className="border-b border-border pb-2 mb-3">
                <h4 className="font-semibold text-foreground">{title}</h4>
                {description && (
                    <p className="text-xs text-muted-foreground mt-0.5">{description}</p>
                )}
            </div>
            {children}
        </div>
    )
}

// ============================================
// DiagramRow - Horizontal layout helper
// ============================================
interface DiagramRowProps {
    children: ReactNode
    justify?: "start" | "center" | "end" | "between" | "around"
    className?: string
}

export function DiagramRow({
    children,
    justify = "center",
    className
}: DiagramRowProps) {
    const justifyStyles = {
        start: "justify-start",
        center: "justify-center",
        end: "justify-end",
        between: "justify-between",
        around: "justify-around",
    }

    return (
        <div className={cn(
            "flex flex-wrap items-start gap-4",
            justifyStyles[justify],
            className
        )}>
            {children}
        </div>
    )
}

// ============================================
// DiagramConnector - Vertical connector line
// ============================================
interface DiagramConnectorProps {
    className?: string
    label?: string
}

export function DiagramConnector({ className, label }: DiagramConnectorProps) {
    return (
        <div className={cn("flex flex-col items-center py-2", className)}>
            <div className="w-px h-4 bg-border" />
            <ArrowDown className="h-4 w-4 text-muted-foreground" />
            {label && (
                <span className="text-xs text-muted-foreground mt-1 text-center max-w-xs">
                    {label}
                </span>
            )}
        </div>
    )
}

// ============================================
// DiagramServiceList - List of services
// ============================================
interface DiagramServiceListProps {
    services: string[]
    className?: string
}

export function DiagramServiceList({ services, className }: DiagramServiceListProps) {
    return (
        <ul className={cn("space-y-1", className)}>
            {services.map((service, index) => (
                <li
                    key={index}
                    className="flex items-center gap-2 text-sm text-muted-foreground"
                >
                    <span className="w-1.5 h-1.5 rounded-full bg-primary flex-shrink-0" />
                    {service}
                </li>
            ))}
        </ul>
    )
}
