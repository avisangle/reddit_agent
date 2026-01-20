import { cn } from "@/lib/utils"

interface SectionProps {
    children: React.ReactNode
    className?: string
    id?: string
}

export function Section({ children, className, id }: SectionProps) {
    return (
        <section id={id} className={cn("mt-12", className)}>
            {children}
        </section>
    )
}

interface SectionHeaderProps {
    children: React.ReactNode
    className?: string
}

export function SectionHeader({ children, className }: SectionHeaderProps) {
    return (
        <h2 className={cn(
            "text-2xl font-semibold tracking-tight border-b border-border pb-3 mb-6",
            className
        )}>
            {children}
        </h2>
    )
}

interface SubSectionProps {
    children: React.ReactNode
    className?: string
}

export function SubSection({ children, className }: SubSectionProps) {
    return (
        <div className={cn("mt-8 space-y-4", className)}>
            {children}
        </div>
    )
}

interface SubSectionHeaderProps {
    children: React.ReactNode
    className?: string
}

export function SubSectionHeader({ children, className }: SubSectionHeaderProps) {
    return (
        <h3 className={cn(
            "text-xl font-medium tracking-tight",
            className
        )}>
            {children}
        </h3>
    )
}
