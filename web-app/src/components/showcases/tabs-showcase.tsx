"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { User, Settings, CreditCard, Bell } from "lucide-react"

export function TabsShowcase() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight mb-2">Tabs</h2>
        <p className="text-muted-foreground text-lg">
          A set of layered sections of content—known as tab panels—that are displayed one at a time.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Basic Tabs</CardTitle>
            <CardDescription>Simple tab navigation</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="account" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="account">Account</TabsTrigger>
                <TabsTrigger value="password">Password</TabsTrigger>
                <TabsTrigger value="settings">Settings</TabsTrigger>
              </TabsList>
              <TabsContent value="account" className="mt-4 space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input id="name" placeholder="Enter your name" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="Enter your email" />
                </div>
                <Button>Save changes</Button>
              </TabsContent>
              <TabsContent value="password" className="mt-4 space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="current">Current password</Label>
                  <Input id="current" type="password" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="new">New password</Label>
                  <Input id="new" type="password" />
                </div>
                <Button>Update password</Button>
              </TabsContent>
              <TabsContent value="settings" className="mt-4">
                <p className="text-sm text-muted-foreground">
                  Configure your account settings and preferences here.
                </p>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Tabs with Icons</CardTitle>
            <CardDescription>Enhanced visual navigation</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="profile" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="profile" className="gap-1.5">
                  <User className="h-4 w-4" />
                  <span className="hidden sm:inline">Profile</span>
                </TabsTrigger>
                <TabsTrigger value="billing" className="gap-1.5">
                  <CreditCard className="h-4 w-4" />
                  <span className="hidden sm:inline">Billing</span>
                </TabsTrigger>
                <TabsTrigger value="notifications" className="gap-1.5">
                  <Bell className="h-4 w-4" />
                  <span className="hidden sm:inline">Alerts</span>
                </TabsTrigger>
                <TabsTrigger value="preferences" className="gap-1.5">
                  <Settings className="h-4 w-4" />
                  <span className="hidden sm:inline">Prefs</span>
                </TabsTrigger>
              </TabsList>
              <TabsContent value="profile" className="mt-4">
                <div className="rounded-lg border p-4">
                  <h4 className="font-medium mb-2">Profile Settings</h4>
                  <p className="text-sm text-muted-foreground">
                    Manage your public profile information.
                  </p>
                </div>
              </TabsContent>
              <TabsContent value="billing" className="mt-4">
                <div className="rounded-lg border p-4">
                  <h4 className="font-medium mb-2">Billing Information</h4>
                  <p className="text-sm text-muted-foreground">
                    View and manage your subscription and payment methods.
                  </p>
                </div>
              </TabsContent>
              <TabsContent value="notifications" className="mt-4">
                <div className="rounded-lg border p-4">
                  <h4 className="font-medium mb-2">Notification Preferences</h4>
                  <p className="text-sm text-muted-foreground">
                    Configure how you want to receive notifications.
                  </p>
                </div>
              </TabsContent>
              <TabsContent value="preferences" className="mt-4">
                <div className="rounded-lg border p-4">
                  <h4 className="font-medium mb-2">General Preferences</h4>
                  <p className="text-sm text-muted-foreground">
                    Customize your app experience and settings.
                  </p>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Content Tabs</CardTitle>
            <CardDescription>Tabs for organizing different types of content</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="overview" className="w-full">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="analytics">Analytics</TabsTrigger>
                <TabsTrigger value="reports">Reports</TabsTrigger>
                <TabsTrigger value="notifications">Notifications</TabsTrigger>
              </TabsList>
              <TabsContent value="overview" className="mt-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="rounded-lg border p-4">
                    <p className="text-sm text-muted-foreground">Total Revenue</p>
                    <p className="text-2xl font-bold">$45,231.89</p>
                    <p className="text-xs text-muted-foreground">+20.1% from last month</p>
                  </div>
                  <div className="rounded-lg border p-4">
                    <p className="text-sm text-muted-foreground">Subscriptions</p>
                    <p className="text-2xl font-bold">+2,350</p>
                    <p className="text-xs text-muted-foreground">+180.1% from last month</p>
                  </div>
                  <div className="rounded-lg border p-4">
                    <p className="text-sm text-muted-foreground">Active Now</p>
                    <p className="text-2xl font-bold">+573</p>
                    <p className="text-xs text-muted-foreground">+201 since last hour</p>
                  </div>
                </div>
              </TabsContent>
              <TabsContent value="analytics" className="mt-4">
                <div className="h-32 rounded-lg border flex items-center justify-center text-muted-foreground">
                  Analytics dashboard content
                </div>
              </TabsContent>
              <TabsContent value="reports" className="mt-4">
                <div className="h-32 rounded-lg border flex items-center justify-center text-muted-foreground">
                  Reports section content
                </div>
              </TabsContent>
              <TabsContent value="notifications" className="mt-4">
                <div className="h-32 rounded-lg border flex items-center justify-center text-muted-foreground">
                  Notifications settings
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
