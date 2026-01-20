"use client"

import Link from "next/link"
import { Menu, Layers } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu"
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from "@/components/ui/sheet"
import { Separator } from "@/components/ui/separator"

interface NavbarProps {
  activeSection: string | null
  setActiveSection: (section: string | null) => void
}

const components = [
  { name: "Buttons", href: "#buttons", description: "Interactive button variants" },
  { name: "Badges", href: "#badges", description: "Status and label indicators" },
  { name: "Cards", href: "#cards", description: "Content containers" },
  { name: "Alerts", href: "#alerts", description: "Feedback messages" },
  { name: "Accordion", href: "#accordion", description: "Expandable sections" },
  { name: "Tabs", href: "#tabs", description: "Tabbed navigation" },
  { name: "Table", href: "#table", description: "Data display" },
  { name: "Charts", href: "#charts", description: "Data visualization" },
  { name: "Forms", href: "#forms", description: "Input components" },
  { name: "Misc", href: "#misc", description: "Other components" },
]

export function Navbar({ activeSection, setActiveSection }: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <Layers className="h-4 w-4 text-primary-foreground" />
          </div>
          <span className="font-semibold text-lg">Design System</span>
        </Link>

        {/* Desktop Navigation */}
        <NavigationMenu className="hidden md:flex">
          <NavigationMenuList>
            <NavigationMenuItem>
              <NavigationMenuTrigger>Components</NavigationMenuTrigger>
              <NavigationMenuContent>
                <ul className="grid w-[400px] gap-1 p-2 md:w-[500px] md:grid-cols-2 lg:w-[600px]">
                  {components.map((component) => (
                    <li key={component.name}>
                      <NavigationMenuLink asChild>
                        <a
                          href={component.href}
                          className="block select-none rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                        >
                          <div className="text-sm font-medium leading-none">{component.name}</div>
                          <p className="line-clamp-1 text-sm leading-snug text-muted-foreground mt-1">
                            {component.description}
                          </p>
                        </a>
                      </NavigationMenuLink>
                    </li>
                  ))}
                </ul>
              </NavigationMenuContent>
            </NavigationMenuItem>
            <NavigationMenuItem>
              <NavigationMenuLink asChild>
                <a href="#buttons" className="group inline-flex h-9 w-max items-center justify-center rounded-md bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground focus:outline-none disabled:pointer-events-none disabled:opacity-50">
                  Documentation
                </a>
              </NavigationMenuLink>
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="hidden md:flex bg-transparent">
            GitHub
          </Button>
          <Button size="sm" className="hidden md:flex">
            Get Started
          </Button>

          {/* Mobile Navigation */}
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-[300px] sm:w-[400px]">
              <SheetTitle className="text-left">Navigation</SheetTitle>
              <nav className="flex flex-col gap-4 mt-6">
                <div className="flex flex-col gap-2">
                  <h4 className="font-medium text-sm text-muted-foreground">Components</h4>
                  <Separator />
                  {components.map((component) => (
                    <a
                      key={component.name}
                      href={component.href}
                      className="block py-2 px-2 rounded-md text-sm hover:bg-accent transition-colors"
                    >
                      {component.name}
                    </a>
                  ))}
                </div>
                <Separator />
                <div className="flex flex-col gap-2">
                  <Button variant="outline" className="w-full bg-transparent">GitHub</Button>
                  <Button className="w-full">Get Started</Button>
                </div>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
