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
    id?: string
}

function generateId(text: string): string {
    return text
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .trim()
}

export function SectionHeader({ children, className, id }: SectionHeaderProps) {
    const headingId = id || (typeof children === 'string' ? generateId(children) : undefined)
    
    return (
        <h2 
            id={headingId}
            className={cn(
                "text-2xl font-semibold tracking-tight border-b border-border pb-3 mb-6 scroll-mt-20",
                className
            )}
        >
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
    id?: string
}

export function SubSectionHeader({ children, className, id }: SubSectionHeaderProps) {
    const headingId = id || (typeof children === 'string' ? generateId(children) : undefined)
    
    return (
        <h3 
            id={headingId}
            className={cn(
                "text-xl font-medium tracking-tight scroll-mt-20",
                className
            )}
        >
            {children}
        </h3>
    )
}
