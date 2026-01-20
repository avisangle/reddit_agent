import { cn } from "@/lib/utils";

interface PageWrapperProps {
  children: React.ReactNode;
  className?: string;
}

export function PageWrapper({ children, className }: PageWrapperProps) {
  return (
    <article className={cn("max-w-4xl mx-auto", className)}>
      {children}
    </article>
  );
}

interface PageHeaderProps {
  title: string;
  description?: React.ReactNode;
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="mb-8 not-prose">
      <h1 className="text-4xl font-bold tracking-tight mb-2">{title}</h1>
      {description && (
        <p className="text-lg text-muted-foreground">{description}</p>
      )}
    </div>
  );
}
