"use client"

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function AccordionShowcase() {
  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold tracking-tight mb-2">Accordion</h2>
        <p className="text-muted-foreground text-lg">
          A vertically stacked set of interactive headings that each reveal a section of content.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Single Accordion</CardTitle>
            <CardDescription>Only one item can be open at a time</CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger>Is it accessible?</AccordionTrigger>
                <AccordionContent>
                  Yes. It adheres to the WAI-ARIA design pattern and includes keyboard navigation support.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-2">
                <AccordionTrigger>Is it styled?</AccordionTrigger>
                <AccordionContent>
                  Yes. It comes with default styles that match the other components&apos; aesthetic.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-3">
                <AccordionTrigger>Is it animated?</AccordionTrigger>
                <AccordionContent>
                  Yes. It&apos;s animated by default, but you can disable it if you prefer.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Multiple Accordion</CardTitle>
            <CardDescription>Multiple items can be open simultaneously</CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="multiple" className="w-full">
              <AccordionItem value="item-1">
                <AccordionTrigger>Can I customize it?</AccordionTrigger>
                <AccordionContent>
                  Absolutely. The components are built with Tailwind CSS and can be easily customized to match your design.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-2">
                <AccordionTrigger>Does it support dark mode?</AccordionTrigger>
                <AccordionContent>
                  Yes, all components support both light and dark modes out of the box using CSS variables.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="item-3">
                <AccordionTrigger>Is it responsive?</AccordionTrigger>
                <AccordionContent>
                  Yes. All components are designed to be fully responsive and work seamlessly on all screen sizes.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>FAQ Section</CardTitle>
            <CardDescription>A common use case for accordions</CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="faq-1">
                <AccordionTrigger>How do I get started?</AccordionTrigger>
                <AccordionContent>
                  Getting started is easy! Simply install the package using npm or yarn, then import the components you need. Each component is self-contained and can be used independently.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="faq-2">
                <AccordionTrigger>What frameworks are supported?</AccordionTrigger>
                <AccordionContent>
                  Our components work with any React-based framework including Next.js, Remix, and Create React App. They&apos;re built on top of Radix UI primitives for maximum compatibility.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="faq-3">
                <AccordionTrigger>Is there TypeScript support?</AccordionTrigger>
                <AccordionContent>
                  Yes! All components are written in TypeScript and include full type definitions. You&apos;ll get complete autocomplete and type checking in your IDE.
                </AccordionContent>
              </AccordionItem>
              <AccordionItem value="faq-4">
                <AccordionTrigger>How do I customize the styles?</AccordionTrigger>
                <AccordionContent>
                  Components use Tailwind CSS classes and CSS variables for styling. You can customize them by modifying the CSS variables in your globals.css file or by adding Tailwind classes directly to the components.
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
