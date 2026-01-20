"use client"

import { useState } from "react"
import { Navbar } from "@/components/navbar"
import { HeroSection } from "@/components/hero-section"
import { ButtonShowcase } from "@/components/showcases/button-showcase"
import { BadgeShowcase } from "@/components/showcases/badge-showcase"
import { CardShowcase } from "@/components/showcases/card-showcase"
import { AlertShowcase } from "@/components/showcases/alert-showcase"
import { AccordionShowcase } from "@/components/showcases/accordion-showcase"
import { TabsShowcase } from "@/components/showcases/tabs-showcase"
import { TableShowcase } from "@/components/showcases/table-showcase"
import { ChartShowcase } from "@/components/showcases/chart-showcase"
import { FormShowcase } from "@/components/showcases/form-showcase"
import { MiscShowcase } from "@/components/showcases/misc-showcase"
import { Separator } from "@/components/ui/separator"
import { Footer } from "@/components/footer"

export default function DesignSystemPage() {
  const [activeSection, setActiveSection] = useState<string | null>(null)

  return (
    <div className="min-h-screen bg-background">
      <Navbar activeSection={activeSection} setActiveSection={setActiveSection} />
      <main className="container mx-auto px-4 py-8">
        <HeroSection />
        
        <Separator className="my-12" />
        
        <section id="buttons" className="scroll-mt-20 mb-16">
          <ButtonShowcase />
        </section>
        
        <Separator className="my-12" />
        
        <section id="badges" className="scroll-mt-20 mb-16">
          <BadgeShowcase />
        </section>
        
        <Separator className="my-12" />
        
        <section id="cards" className="scroll-mt-20 mb-16">
          <CardShowcase />
        </section>
        
        <Separator className="my-12" />
        
        <section id="alerts" className="scroll-mt-20 mb-16">
          <AlertShowcase />
        </section>
        
        <Separator className="my-12" />
        
        <section id="accordion" className="scroll-mt-20 mb-16">
          <AccordionShowcase />
        </section>
        
        <Separator className="my-12" />
        
        <section id="tabs" className="scroll-mt-20 mb-16">
          <TabsShowcase />
        </section>
        
        <Separator className="my-12" />
        
        <section id="table" className="scroll-mt-20 mb-16">
          <TableShowcase />
        </section>
        
        <Separator className="my-12" />
        
        <section id="charts" className="scroll-mt-20 mb-16">
          <ChartShowcase />
        </section>
        
        <Separator className="my-12" />
        
        <section id="forms" className="scroll-mt-20 mb-16">
          <FormShowcase />
        </section>
        
        <Separator className="my-12" />
        
        <section id="misc" className="scroll-mt-20 mb-16">
          <MiscShowcase />
        </section>
      </main>
      <Footer />
    </div>
  )
}
