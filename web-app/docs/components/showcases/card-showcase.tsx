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
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { MoreHorizontal, Heart, MessageCircle, Share2, Bookmark, ArrowRight } from "lucide-react"

export function CardShowcase() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight mb-2">Cards</h2>
        <p className="text-muted-foreground text-lg">
          Displays a card with header, content, and footer.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Simple Card</CardTitle>
            <CardDescription>A basic card with title and description</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              This is a simple card component that can be used to display content in a contained format.
            </p>
          </CardContent>
          <CardFooter>
            <Button variant="outline" className="w-full bg-transparent">Learn More</Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-start justify-between">
            <div>
              <CardTitle>Card with Action</CardTitle>
              <CardDescription>Features an action button in the header</CardDescription>
            </div>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              This card includes a header action for additional options or controls.
            </p>
          </CardContent>
          <CardFooter className="gap-2">
            <Button className="flex-1">Primary</Button>
            <Button variant="outline" className="flex-1 bg-transparent">Secondary</Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-4">
              <Avatar>
                <AvatarImage src="https://github.com/shadcn.png" alt="User" />
                <AvatarFallback>CN</AvatarFallback>
              </Avatar>
              <div>
                <CardTitle className="text-base">Sarah Wilson</CardTitle>
                <CardDescription>Product Designer</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Just shipped a new feature! Really excited about the user feedback we&apos;ve been receiving.
            </p>
          </CardContent>
          <CardFooter className="gap-4">
            <Button variant="ghost" size="sm" className="gap-1">
              <Heart className="h-4 w-4" />
              42
            </Button>
            <Button variant="ghost" size="sm" className="gap-1">
              <MessageCircle className="h-4 w-4" />
              12
            </Button>
            <Button variant="ghost" size="sm" className="gap-1">
              <Share2 className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" className="ml-auto gap-1">
              <Bookmark className="h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>

        <Card className="md:col-span-2 lg:col-span-2">
          <CardHeader>
            <Badge variant="secondary" className="w-fit mb-2">Featured</Badge>
            <CardTitle>Wide Card Layout</CardTitle>
            <CardDescription>
              This card spans multiple columns to demonstrate flexibility
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-1">
                <p className="text-2xl font-bold">2,350</p>
                <p className="text-sm text-muted-foreground">Total Users</p>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-bold">1,234</p>
                <p className="text-sm text-muted-foreground">Active Today</p>
              </div>
              <div className="space-y-1">
                <p className="text-2xl font-bold">87%</p>
                <p className="text-sm text-muted-foreground">Engagement Rate</p>
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Button variant="outline" className="gap-2 bg-transparent">
              View Analytics
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Pricing Card</CardTitle>
            <CardDescription>Pro Plan</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-baseline gap-1">
              <span className="text-4xl font-bold">$29</span>
              <span className="text-muted-foreground">/month</span>
            </div>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                Unlimited projects
              </li>
              <li className="flex items-center gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                Priority support
              </li>
              <li className="flex items-center gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                Advanced analytics
              </li>
            </ul>
          </CardContent>
          <CardFooter>
            <Button className="w-full">Get Started</Button>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
