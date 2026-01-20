"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import {
  AlertCircle,
  ArrowRight,
  Bell,
  Check,
  ChevronRight,
  Download,
  Heart,
  Info,
  Mail,
  Moon,
  Settings,
  Star,
  Sun,
  User,
  Zap,
} from "lucide-react"
import {
  Bar,
  BarChart,
  Line,
  LineChart,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Cell,
  Pie,
  PieChart,
} from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"

const barChartData = [
  { month: "Jan", value: 186 },
  { month: "Feb", value: 305 },
  { month: "Mar", value: 237 },
  { month: "Apr", value: 273 },
  { month: "May", value: 209 },
]

const lineChartData = [
  { month: "Jan", desktop: 186, mobile: 80 },
  { month: "Feb", desktop: 305, mobile: 200 },
  { month: "Mar", desktop: 237, mobile: 120 },
  { month: "Apr", desktop: 273, mobile: 190 },
  { month: "May", desktop: 209, mobile: 130 },
]

const pieChartData = [
  { name: "chrome", value: 275, fill: "var(--chart-1)" },
  { name: "safari", value: 200, fill: "var(--chart-2)" },
  { name: "firefox", value: 187, fill: "var(--chart-3)" },
  { name: "edge", value: 173, fill: "var(--chart-4)" },
]

export default function ThemeComparePage() {
  const [activeTheme, setActiveTheme] = useState<"original" | "ocean" | "forest" | "rose">("original")

  return (
    <div className={`min-h-screen transition-colors duration-300 ${activeTheme !== "original" ? activeTheme : ""}`}>
      <style jsx global>{`
        /* Ocean Dark Theme - Cool blues and cyans */
        .ocean {
          --background: #0c1222;
          --foreground: #e2e8f0;
          --card: #131b2e;
          --card-foreground: #e2e8f0;
          --popover: #131b2e;
          --popover-foreground: #e2e8f0;
          --primary: #0ea5e9;
          --primary-foreground: #ffffff;
          --secondary: #1e293b;
          --secondary-foreground: #e2e8f0;
          --muted: #1e293b;
          --muted-foreground: #94a3b8;
          --accent: #164e63;
          --accent-foreground: #22d3ee;
          --destructive: #ef4444;
          --destructive-foreground: #ffffff;
          --border: #1e3a5f;
          --input: #1e3a5f;
          --ring: #0ea5e9;
          --chart-1: #22d3ee;
          --chart-2: #0ea5e9;
          --chart-3: #6366f1;
          --chart-4: #a78bfa;
          --chart-5: #64748b;
        }

        /* Forest Dark Theme - Rich greens and earth tones */
        .forest {
          --background: #0f1a14;
          --foreground: #e2ebe5;
          --card: #162118;
          --card-foreground: #e2ebe5;
          --popover: #162118;
          --popover-foreground: #e2ebe5;
          --primary: #22c55e;
          --primary-foreground: #ffffff;
          --secondary: #1c2e22;
          --secondary-foreground: #e2ebe5;
          --muted: #1c2e22;
          --muted-foreground: #86a992;
          --accent: #14532d;
          --accent-foreground: #4ade80;
          --destructive: #f87171;
          --destructive-foreground: #ffffff;
          --border: #2d4a37;
          --input: #2d4a37;
          --ring: #22c55e;
          --chart-1: #4ade80;
          --chart-2: #22c55e;
          --chart-3: #fbbf24;
          --chart-4: #f97316;
          --chart-5: #6b7280;
        }

        /* Rose Dark Theme - Warm pinks and magentas */
        .rose {
          --background: #1a0f14;
          --foreground: #f5e6ec;
          --card: #241620;
          --card-foreground: #f5e6ec;
          --popover: #241620;
          --popover-foreground: #f5e6ec;
          --primary: #ec4899;
          --primary-foreground: #ffffff;
          --secondary: #2e1a25;
          --secondary-foreground: #f5e6ec;
          --muted: #2e1a25;
          --muted-foreground: #b38da0;
          --accent: #831843;
          --accent-foreground: #f472b6;
          --destructive: #f87171;
          --destructive-foreground: #ffffff;
          --border: #4a2d3d;
          --input: #4a2d3d;
          --ring: #ec4899;
          --chart-1: #f472b6;
          --chart-2: #ec4899;
          --chart-3: #a855f7;
          --chart-4: #8b5cf6;
          --chart-5: #6b7280;
        }
      `}</style>

      <div className="bg-background text-foreground min-h-screen">
        {/* Header */}
        <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container mx-auto px-6 py-4 flex items-center justify-between">
            <h1 className="text-xl font-bold">Theme Comparison</h1>
            <div className="flex items-center gap-2">
              <Button
                variant={activeTheme === "original" ? "default" : "outline"}
                size="sm"
                onClick={() => setActiveTheme("original")}
                className="bg-transparent"
              >
                <Sun className="h-4 w-4 mr-2" />
                Original
              </Button>
              <Button
                variant={activeTheme === "ocean" ? "default" : "outline"}
                size="sm"
                onClick={() => setActiveTheme("ocean")}
                className="bg-transparent"
              >
                <Moon className="h-4 w-4 mr-2" />
                Ocean
              </Button>
              <Button
                variant={activeTheme === "forest" ? "default" : "outline"}
                size="sm"
                onClick={() => setActiveTheme("forest")}
                className="bg-transparent"
              >
                <Moon className="h-4 w-4 mr-2" />
                Forest
              </Button>
              <Button
                variant={activeTheme === "rose" ? "default" : "outline"}
                size="sm"
                onClick={() => setActiveTheme("rose")}
                className="bg-transparent"
              >
                <Moon className="h-4 w-4 mr-2" />
                Rose
              </Button>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-6 py-12 space-y-16">
          {/* Theme Info */}
          <section className="text-center max-w-2xl mx-auto">
            <Badge variant="secondary" className="mb-4">
              Active: {activeTheme.charAt(0).toUpperCase() + activeTheme.slice(1)} Theme
            </Badge>
            <h2 className="text-4xl font-bold mb-4 text-balance">
              Compare Dark Themes
            </h2>
            <p className="text-muted-foreground text-lg text-pretty">
              Toggle between your original dark theme and three alternative color schemes to see how components look.
            </p>
          </section>

          <Separator />

          {/* Color Palette Preview */}
          <section>
            <h3 className="text-2xl font-semibold mb-6">Color Palette</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              <div className="space-y-2">
                <div className="h-16 rounded-lg bg-primary" />
                <p className="text-sm font-medium">Primary</p>
              </div>
              <div className="space-y-2">
                <div className="h-16 rounded-lg bg-secondary" />
                <p className="text-sm font-medium">Secondary</p>
              </div>
              <div className="space-y-2">
                <div className="h-16 rounded-lg bg-accent" />
                <p className="text-sm font-medium">Accent</p>
              </div>
              <div className="space-y-2">
                <div className="h-16 rounded-lg bg-muted" />
                <p className="text-sm font-medium">Muted</p>
              </div>
              <div className="space-y-2">
                <div className="h-16 rounded-lg bg-destructive" />
                <p className="text-sm font-medium">Destructive</p>
              </div>
              <div className="space-y-2">
                <div className="h-16 rounded-lg bg-card border border-border" />
                <p className="text-sm font-medium">Card</p>
              </div>
            </div>
            <div className="grid grid-cols-5 gap-4 mt-6">
              <div className="space-y-2">
                <div className="h-12 rounded-lg bg-chart-1" />
                <p className="text-xs text-muted-foreground">Chart 1</p>
              </div>
              <div className="space-y-2">
                <div className="h-12 rounded-lg bg-chart-2" />
                <p className="text-xs text-muted-foreground">Chart 2</p>
              </div>
              <div className="space-y-2">
                <div className="h-12 rounded-lg bg-chart-3" />
                <p className="text-xs text-muted-foreground">Chart 3</p>
              </div>
              <div className="space-y-2">
                <div className="h-12 rounded-lg bg-chart-4" />
                <p className="text-xs text-muted-foreground">Chart 4</p>
              </div>
              <div className="space-y-2">
                <div className="h-12 rounded-lg bg-chart-5" />
                <p className="text-xs text-muted-foreground">Chart 5</p>
              </div>
            </div>
          </section>

          <Separator />

          {/* Buttons */}
          <section>
            <h3 className="text-2xl font-semibold mb-6">Buttons</h3>
            <div className="flex flex-wrap gap-4">
              <Button>Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline" className="bg-transparent">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="destructive">Destructive</Button>
              <Button variant="link">Link</Button>
            </div>
            <div className="flex flex-wrap gap-4 mt-4">
              <Button size="lg">
                <Zap className="mr-2 h-5 w-5" />
                Large with Icon
              </Button>
              <Button size="sm">
                Small
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
              <Button size="icon" variant="outline" className="bg-transparent">
                <Heart className="h-4 w-4" />
              </Button>
            </div>
          </section>

          <Separator />

          {/* Badges */}
          <section>
            <h3 className="text-2xl font-semibold mb-6">Badges</h3>
            <div className="flex flex-wrap gap-3">
              <Badge>Default</Badge>
              <Badge variant="secondary">Secondary</Badge>
              <Badge variant="outline">Outline</Badge>
              <Badge variant="destructive">Destructive</Badge>
              <Badge>
                <Check className="h-3 w-3 mr-1" />
                Success
              </Badge>
              <Badge variant="secondary">
                <Star className="h-3 w-3 mr-1" />
                Featured
              </Badge>
            </div>
          </section>

          <Separator />

          {/* Cards */}
          <section>
            <h3 className="text-2xl font-semibold mb-6">Cards</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Simple Card</CardTitle>
                  <CardDescription>A basic card component</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Cards contain content and actions about a single subject.
                  </p>
                </CardContent>
                <CardFooter>
                  <Button className="w-full">Action</Button>
                </CardFooter>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center gap-4">
                  <Avatar>
                    <AvatarImage src="https://github.com/shadcn.png" />
                    <AvatarFallback>CN</AvatarFallback>
                  </Avatar>
                  <div>
                    <CardTitle className="text-base">User Profile</CardTitle>
                    <CardDescription>@username</CardDescription>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Full-stack developer passionate about building great products.
                  </p>
                </CardContent>
                <CardFooter className="gap-2">
                  <Button variant="outline" size="sm" className="bg-transparent">
                    <Mail className="h-4 w-4 mr-2" />
                    Message
                  </Button>
                  <Button size="sm">Follow</Button>
                </CardFooter>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Statistics</CardTitle>
                    <Badge variant="secondary">+12%</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Progress</span>
                      <span className="text-muted-foreground">75%</span>
                    </div>
                    <Progress value={75} />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Completed</span>
                      <span className="text-muted-foreground">45%</span>
                    </div>
                    <Progress value={45} />
                  </div>
                </CardContent>
              </Card>
            </div>
          </section>

          <Separator />

          {/* Alerts */}
          <section>
            <h3 className="text-2xl font-semibold mb-6">Alerts</h3>
            <div className="space-y-4 max-w-2xl">
              <Alert>
                <Info className="h-4 w-4" />
                <AlertTitle>Information</AlertTitle>
                <AlertDescription>
                  This is an informational alert with default styling.
                </AlertDescription>
              </Alert>
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>
                  Something went wrong. Please try again later.
                </AlertDescription>
              </Alert>
            </div>
          </section>

          <Separator />

          {/* Accordion */}
          <section>
            <h3 className="text-2xl font-semibold mb-6">Accordion</h3>
            <Accordion type="single" collapsible className="max-w-2xl">
              <AccordionItem value="item-1">
                <AccordionTrigger>What is this theme comparison?</AccordionTrigger>
                <AccordionContent>
                  This page allows you to compare different dark theme color schemes and see how they affect all UI components in real-time.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-2">
                <AccordionTrigger>How do I apply a theme?</AccordionTrigger>
                <AccordionContent>
                  Use the theme switcher buttons in the header to toggle between themes. Copy the CSS variables from your preferred theme into your globals.css file.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-3">
                <AccordionTrigger>Can I customize further?</AccordionTrigger>
                <AccordionContent>
                  Absolutely! These themes are starting points. You can adjust any CSS variable to fine-tune colors, borders, shadows, and more.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </section>

          <Separator />

          {/* Tabs */}
          <section>
            <h3 className="text-2xl font-semibold mb-6">Tabs</h3>
            <Tabs defaultValue="overview" className="max-w-2xl">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="analytics">Analytics</TabsTrigger>
                <TabsTrigger value="settings">Settings</TabsTrigger>
              </TabsList>
              <TabsContent value="overview" className="mt-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Overview</CardTitle>
                    <CardDescription>Your project summary at a glance</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span>Total Users</span>
                      <Badge>2,543</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Active Sessions</span>
                      <Badge variant="secondary">847</Badge>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="analytics" className="mt-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Analytics</CardTitle>
                    <CardDescription>Performance metrics</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Progress value={68} className="mb-2" />
                    <p className="text-sm text-muted-foreground">68% of monthly goal reached</p>
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="settings" className="mt-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Settings</CardTitle>
                    <CardDescription>Manage your preferences</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Bell className="h-4 w-4" />
                        <span>Notifications</span>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Moon className="h-4 w-4" />
                        <span>Dark Mode</span>
                      </div>
                      <Switch defaultChecked />
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </section>

          <Separator />

          {/* Table */}
          <section>
            <h3 className="text-2xl font-semibold mb-6">Table</h3>
            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback>JD</AvatarFallback>
                        </Avatar>
                        John Doe
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge>Active</Badge>
                    </TableCell>
                    <TableCell>Admin</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback>JS</AvatarFallback>
                        </Avatar>
                        Jane Smith
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">Pending</Badge>
                    </TableCell>
                    <TableCell>Editor</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <Avatar className="h-8 w-8">
                          <AvatarFallback>BW</AvatarFallback>
                        </Avatar>
                        Bob Wilson
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">Inactive</Badge>
                    </TableCell>
                    <TableCell>Viewer</TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </Card>
          </section>

          <Separator />

          {/* Charts */}
          <section>
            <h3 className="text-2xl font-semibold mb-6">Charts</h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Bar Chart</CardTitle>
                  <CardDescription>Monthly performance</CardDescription>
                </CardHeader>
                <CardContent>
                  <ChartContainer
                    config={{
                      value: {
                        label: "Value",
                        color: "var(--chart-1)",
                      },
                    }}
                    className="h-[200px]"
                  >
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={barChartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                        <XAxis dataKey="month" stroke="var(--muted-foreground)" fontSize={12} />
                        <YAxis stroke="var(--muted-foreground)" fontSize={12} />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Bar dataKey="value" fill="var(--chart-1)" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Line Chart</CardTitle>
                  <CardDescription>Device comparison</CardDescription>
                </CardHeader>
                <CardContent>
                  <ChartContainer
                    config={{
                      desktop: {
                        label: "Desktop",
                        color: "var(--chart-1)",
                      },
                      mobile: {
                        label: "Mobile",
                        color: "var(--chart-2)",
                      },
                    }}
                    className="h-[200px]"
                  >
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={lineChartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                        <XAxis dataKey="month" stroke="var(--muted-foreground)" fontSize={12} />
                        <YAxis stroke="var(--muted-foreground)" fontSize={12} />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Line type="monotone" dataKey="desktop" stroke="var(--chart-1)" strokeWidth={2} dot={false} />
                        <Line type="monotone" dataKey="mobile" stroke="var(--chart-2)" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Pie Chart</CardTitle>
                  <CardDescription>Browser distribution</CardDescription>
                </CardHeader>
                <CardContent>
                  <ChartContainer
                    config={{
                      chrome: { label: "Chrome", color: "var(--chart-1)" },
                      safari: { label: "Safari", color: "var(--chart-2)" },
                      firefox: { label: "Firefox", color: "var(--chart-3)" },
                      edge: { label: "Edge", color: "var(--chart-4)" },
                    }}
                    className="h-[200px]"
                  >
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <Pie
                          data={pieChartData}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          innerRadius={40}
                          outerRadius={70}
                        >
                          {pieChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.fill} />
                          ))}
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                </CardContent>
              </Card>
            </div>
          </section>

          <Separator />

          {/* Form Elements */}
          <section>
            <h3 className="text-2xl font-semibold mb-6">Form Elements</h3>
            <Card className="max-w-md">
              <CardHeader>
                <CardTitle>Contact Form</CardTitle>
                <CardDescription>See how inputs look in this theme</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Name</label>
                  <Input placeholder="Enter your name" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Email</label>
                  <Input type="email" placeholder="Enter your email" />
                </div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">Subscribe to newsletter</label>
                  <Switch />
                </div>
              </CardContent>
              <CardFooter>
                <Button className="w-full">Submit</Button>
              </CardFooter>
            </Card>
          </section>

          {/* Theme CSS Reference */}
          <Separator />
          
          <section>
            <h3 className="text-2xl font-semibold mb-6">Theme CSS Variables</h3>
            <p className="text-muted-foreground mb-4">
              Copy the CSS below to apply the selected theme to your globals.css
            </p>
            <Card>
              <CardContent className="pt-6">
                <pre className="text-sm overflow-x-auto p-4 bg-muted rounded-lg">
                  <code>
{activeTheme === "original" ? `/* Your Original Dark Theme */
.dark {
  --background: #1a1b1e;
  --foreground: #f0f0f0;
  --card: #222327;
  --card-foreground: #f0f0f0;
  --primary: rgb(255, 143, 51);
  --primary-foreground: #ffffff;
  --secondary: #2a2c33;
  --secondary-foreground: #f0f0f0;
  --muted: #2a2c33;
  --muted-foreground: #a0a0a0;
  --accent: #1e293b;
  --accent-foreground: #79c0ff;
  --destructive: #f87171;
  --border: #33353a;
  --ring: #8c5cff;
  --chart-1: #4ade80;
  --chart-2: #8c5cff;
  --chart-3: #fca5a5;
  --chart-4: #5993f4;
  --chart-5: #a0a0a0;
}` : activeTheme === "ocean" ? `/* Ocean Dark Theme */
.dark {
  --background: #0c1222;
  --foreground: #e2e8f0;
  --card: #131b2e;
  --card-foreground: #e2e8f0;
  --primary: #0ea5e9;
  --primary-foreground: #ffffff;
  --secondary: #1e293b;
  --secondary-foreground: #e2e8f0;
  --muted: #1e293b;
  --muted-foreground: #94a3b8;
  --accent: #164e63;
  --accent-foreground: #22d3ee;
  --destructive: #ef4444;
  --border: #1e3a5f;
  --ring: #0ea5e9;
  --chart-1: #22d3ee;
  --chart-2: #0ea5e9;
  --chart-3: #6366f1;
  --chart-4: #a78bfa;
  --chart-5: #64748b;
}` : activeTheme === "forest" ? `/* Forest Dark Theme */
.dark {
  --background: #0f1a14;
  --foreground: #e2ebe5;
  --card: #162118;
  --card-foreground: #e2ebe5;
  --primary: #22c55e;
  --primary-foreground: #ffffff;
  --secondary: #1c2e22;
  --secondary-foreground: #e2ebe5;
  --muted: #1c2e22;
  --muted-foreground: #86a992;
  --accent: #14532d;
  --accent-foreground: #4ade80;
  --destructive: #f87171;
  --border: #2d4a37;
  --ring: #22c55e;
  --chart-1: #4ade80;
  --chart-2: #22c55e;
  --chart-3: #fbbf24;
  --chart-4: #f97316;
  --chart-5: #6b7280;
}` : `/* Rose Dark Theme */
.dark {
  --background: #1a0f14;
  --foreground: #f5e6ec;
  --card: #241620;
  --card-foreground: #f5e6ec;
  --primary: #ec4899;
  --primary-foreground: #ffffff;
  --secondary: #2e1a25;
  --secondary-foreground: #f5e6ec;
  --muted: #2e1a25;
  --muted-foreground: #b38da0;
  --accent: #831843;
  --accent-foreground: #f472b6;
  --destructive: #f87171;
  --border: #4a2d3d;
  --ring: #ec4899;
  --chart-1: #f472b6;
  --chart-2: #ec4899;
  --chart-3: #a855f7;
  --chart-4: #8b5cf6;
  --chart-5: #6b7280;
}`}
                  </code>
                </pre>
              </CardContent>
            </Card>
          </section>
        </main>

        {/* Footer */}
        <footer className="border-t border-border mt-16">
          <div className="container mx-auto px-6 py-8 text-center text-muted-foreground">
            <p>Theme Comparison Tool</p>
          </div>
        </footer>
      </div>
    </div>
  )
}
