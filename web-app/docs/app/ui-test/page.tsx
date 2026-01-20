import { AccordionShowcase } from "@/components/showcases/accordion-showcase"
import { AlertShowcase } from "@/components/showcases/alert-showcase"
import { BadgeShowcase } from "@/components/showcases/badge-showcase"
import { ButtonShowcase } from "@/components/showcases/button-showcase"
import { CardShowcase } from "@/components/showcases/card-showcase"
import { FormShowcase } from "@/components/showcases/form-showcase"
import { MiscShowcase } from "@/components/showcases/misc-showcase"
import { TableShowcase } from "@/components/showcases/table-showcase"
import { TabsShowcase } from "@/components/showcases/tabs-showcase"

export default function UITestPage() {
    return (
        <div className="max-w-6xl mx-auto py-12 px-4 space-y-16">
            {/* Warning Banner */}
            <div className="bg-destructive/10 border border-destructive/30 rounded-lg p-4 text-center">
                <p className="text-destructive font-medium">
                    ⚠️ This is a test page for previewing UI components. Not linked to main navigation.
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                    Access via <code className="bg-secondary px-1.5 py-0.5 rounded">/ui-test</code>
                </p>
            </div>

            <h1 className="text-4xl font-bold text-center">UI Component Showcase</h1>
            <p className="text-center text-muted-foreground text-lg">
                Preview all available UI components from <code className="bg-secondary px-1.5 py-0.5 rounded">@/components/showcases</code>
            </p>

            {/* Table of Contents */}
            <div className="bg-secondary/30 rounded-lg p-6">
                <h2 className="font-semibold mb-4">Components</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
                    <a href="#buttons" className="hover:text-primary">→ Buttons</a>
                    <a href="#badges" className="hover:text-primary">→ Badges</a>
                    <a href="#cards" className="hover:text-primary">→ Cards</a>
                    <a href="#alerts" className="hover:text-primary">→ Alerts</a>
                    <a href="#accordions" className="hover:text-primary">→ Accordions</a>
                    <a href="#tabs" className="hover:text-primary">→ Tabs</a>
                    <a href="#forms" className="hover:text-primary">→ Forms</a>
                    <a href="#tables" className="hover:text-primary">→ Tables</a>
                    <a href="#misc" className="hover:text-primary">→ Miscellaneous</a>
                </div>
            </div>

            {/* Showcases */}
            <section id="buttons">
                <ButtonShowcase />
            </section>

            <hr className="border-border" />

            <section id="badges">
                <BadgeShowcase />
            </section>

            <hr className="border-border" />

            <section id="cards">
                <CardShowcase />
            </section>

            <hr className="border-border" />

            <section id="alerts">
                <AlertShowcase />
            </section>

            <hr className="border-border" />

            <section id="accordions">
                <AccordionShowcase />
            </section>

            <hr className="border-border" />

            <section id="tabs">
                <TabsShowcase />
            </section>

            <hr className="border-border" />

            <section id="forms">
                <FormShowcase />
            </section>

            <hr className="border-border" />

            <section id="tables">
                <TableShowcase />
            </section>

            <hr className="border-border" />

            <section id="misc">
                <MiscShowcase />
            </section>

            {/* Footer */}
            <footer className="text-center text-muted-foreground text-sm pt-8 border-t border-border">
                <p>UI components from <code className="bg-secondary px-1.5 py-0.5 rounded">@/components/ui</code></p>
                <p className="mt-1">Showcases from <code className="bg-secondary px-1.5 py-0.5 rounded">@/components/showcases</code></p>
            </footer>
        </div>
    )
}
