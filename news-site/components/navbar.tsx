"use client"

import Link from "next/link"
import { Newspaper } from "lucide-react"
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from "@/components/ui/navigation-menu"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Menu } from "lucide-react"

const topics = [
  { name: "Politics", href: "/topics/politics" },
  { name: "Sports", href: "/topics/sports" },
  { name: "Entertainment", href: "/topics/entertainment" },
  { name: "Technology", href: "/topics/technology" },
  { name: "Business", href: "/topics/business" },
]

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="md:hidden">
              <Menu className="h-6 w-6" />
              <span className="sr-only">Toggle navigation menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left">
            <div className="grid gap-4 py-4">
              {topics.map((topic) => (
                <Link key={topic.href} href={topic.href} className="text-sm font-medium hover:underline">
                  {topic.name}
                </Link>
              ))}
            </div>
          </SheetContent>
        </Sheet>
        <Link href="/" className="mr-6 flex items-center space-x-2">
          <Newspaper className="h-6 w-6" />
          <span className="hidden font-bold sm:inline-block">News Portal</span>
        </Link>
        <NavigationMenu className="hidden md:flex">
          <NavigationMenuList>
            {topics.map((topic) => (
              <NavigationMenuItem key={topic.href}>
                <Link href={topic.href} legacyBehavior passHref>
                  <NavigationMenuLink className="group inline-flex h-9 w-max items-center justify-center rounded-md bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground focus:outline-none disabled:pointer-events-none disabled:opacity-50 data-[active]:bg-accent/50 data-[state=open]:bg-accent/50">
                    {topic.name}
                  </NavigationMenuLink>
                </Link>
              </NavigationMenuItem>
            ))}
          </NavigationMenuList>
        </NavigationMenu>
        <div className="ml-auto flex items-center space-x-4">
          <Button variant="ghost" size="sm">
            Sign In
          </Button>
          <Button size="sm">Subscribe</Button>
        </div>
      </div>
    </header>
  )
}

