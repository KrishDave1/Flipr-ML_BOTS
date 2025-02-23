import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Navbar } from "@/components/navbar"
import { Footer } from "@/components/footer"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "News Portal",
  description: "Your source for news across sports, entertainment, politics and more",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex min-h-screen flex-col">
          <Navbar />
            <main
              className="flex-1"
              style={{
                display: "flex",
                justifyContent: "center", 
                alignItems: "center", 
              }}
            >
              <div style = {{ width: "90%"}}>
                {children}
              </div>
            </main>
          <Footer />
        </div>
      </body>
    </html>
  )
}

