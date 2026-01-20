import React from "react"
import type { Metadata } from 'next'

import './globals.css'

import { Plus_Jakarta_Sans, IBM_Plex_Mono } from 'next/font/google'

// Initialize fonts with CSS variables
const plusJakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ["400", "500", "600", "700"],
  variable: '--font-sans'
})
const ibmPlexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ["400", "500", "600"],
  variable: '--font-mono'
})

export const metadata: Metadata = {
  title: 'Reddit Agent Admin',
  description: 'Admin dashboard for Reddit Comment Engagement Agent',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${plusJakarta.variable} ${ibmPlexMono.variable} font-sans antialiased bg-background text-foreground`}>
        {children}
      </body>
    </html>
  )
}
