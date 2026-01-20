"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import { Check, Copy, Terminal } from "lucide-react"
import { codeToHtml } from "shiki"

interface CodeBlockProps {
  children: string
  language?: string
  filename?: string
  showLineNumbers?: boolean
  showCopy?: boolean
  className?: string
}

const languageLabels: Record<string, string> = {
  bash: "Bash",
  shell: "Shell",
  python: "Python",
  py: "Python",
  javascript: "JavaScript",
  js: "JavaScript",
  typescript: "TypeScript",
  ts: "TypeScript",
  json: "JSON",
  yaml: "YAML",
  yml: "YAML",
  sql: "SQL",
  text: "Text",
  plaintext: "Text",
}

export function CodeBlock({
  children,
  language = "text",
  filename,
  showLineNumbers = false,
  showCopy = true,
  className
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false)
  const [highlightedHtml, setHighlightedHtml] = useState<string | null>(null)

  useEffect(() => {
    async function highlight() {
      try {
        const html = await codeToHtml(children.trim(), {
          lang: language,
          theme: "github-dark-default",
        })
        setHighlightedHtml(html)
      } catch {
        // If language not supported, fallback to plain text
        try {
          const html = await codeToHtml(children.trim(), {
            lang: "text",
            theme: "github-dark-default",
          })
          setHighlightedHtml(html)
        } catch {
          setHighlightedHtml(null)
        }
      }
    }
    highlight()
  }, [children, language])

  const handleCopy = async () => {
    await navigator.clipboard.writeText(children.trim())
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const displayLanguage = languageLabels[language] || language.toUpperCase()

  return (
    <div className={cn(
      "relative group my-4 rounded-lg border border-border overflow-hidden",
      className
    )}>
      {/* Header bar with filename or language */}
      <div className="flex items-center justify-between px-4 py-2 bg-secondary/50 border-b border-border">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Terminal className="h-4 w-4" />
          {filename ? (
            <span className="font-medium">{filename}</span>
          ) : (
            <span>{displayLanguage}</span>
          )}
        </div>

        {showCopy && (
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-2 py-1 text-xs text-muted-foreground hover:text-foreground bg-secondary/80 hover:bg-secondary rounded transition-colors"
            aria-label={copied ? "Copied" : "Copy code"}
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-chart-1" />
                <span className="text-chart-1">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Code content */}
      <div className={cn(
        "overflow-x-auto bg-[#0d1117] text-sm",
        showLineNumbers && "[&_pre]:pl-12 [&_pre]:relative [&_.line]:before:absolute [&_.line]:before:left-4 [&_.line]:before:text-muted-foreground/50 [&_.line]:before:content-[counter(line)] [&_.line]:before:counter-increment-[line] [&_pre]:counter-reset-[line]"
      )}>
        {highlightedHtml ? (
          <div
            className="[&_pre]:p-4 [&_pre]:m-0 [&_pre]:bg-transparent [&_code]:bg-transparent"
            dangerouslySetInnerHTML={{ __html: highlightedHtml }}
          />
        ) : (
          <pre className="p-4 m-0">
            <code className="text-slate-100">{children.trim()}</code>
          </pre>
        )}
      </div>
    </div>
  )
}

interface InlineCodeProps {
  children: React.ReactNode
  className?: string
}

export function InlineCode({ children, className }: InlineCodeProps) {
  return (
    <code className={cn(
      "bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded text-sm font-mono",
      className
    )}>
      {children}
    </code>
  )
}
