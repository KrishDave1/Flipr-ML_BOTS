"use client"

import Link from "next/link"
import { Newspaper } from "lucide-react"
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { Menu } from "lucide-react"
import { topicSubtopics } from "@/lib/topics"

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="lg:hidden">
              <Menu className="h-6 w-6" />
              <span className="sr-only">Toggle navigation menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left">
            <div className="grid gap-4 py-4">
              {Object.entries(topicSubtopics).map(([topic, subtopics]) => (
                <div key={topic} className="space-y-2">
                  <Link href={`/topics/${topic}`} className="text-sm font-medium capitalize hover:underline">
                    {topic}
                  </Link>
                  <div className="pl-4 text-sm text-muted-foreground">
                    {subtopics.slice(0, 3).map((subtopic) => (
                      <Link
                        key={subtopic}
                        href={`/topics/${topic}?subtopic=${encodeURIComponent(subtopic)}`}
                        className="block py-1 hover:text-foreground"
                      >
                        {subtopic}
                      </Link>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </SheetContent>
        </Sheet>
        <Link href="/" className="mr-6 flex items-center space-x-2">
          <Newspaper className="h-6 w-6" />
          <span className="hidden font-bold sm:inline-block">News Portal</span>
        </Link>
        <NavigationMenu className="hidden lg:flex">
          <NavigationMenuList>
            {Object.entries(topicSubtopics).map(([topic, subtopics]) => (
              <NavigationMenuItem key={topic}>
                <NavigationMenuTrigger className="capitalize">{topic}</NavigationMenuTrigger>
                <NavigationMenuContent>
                  <div className="grid w-[400px] gap-3 p-4">
                    <Link href={`/topics/${topic}`} className="block text-sm font-medium hover:underline">
                      All {topic} News
                    </Link>
                    <div className="grid grid-cols-2 gap-2">
                      {subtopics.map((subtopic) => (
                        <Link
                          key={subtopic}
                          href={`/topics/${topic}?subtopic=${encodeURIComponent(subtopic)}`}
                          className="block text-sm text-muted-foreground hover:text-foreground"
                        >
                          {subtopic}
                        </Link>
                      ))}
                    </div>
                  </div>
                </NavigationMenuContent>
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

