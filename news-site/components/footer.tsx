import Link from "next/link"
import { Newspaper } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="container flex flex-col gap-6 py-8 md:flex-row md:items-start md:justify-between">
        <div className="flex flex-col gap-2">
          <Link href="/" className="flex items-center space-x-2">
            <Newspaper className="h-6 w-6" />
            <span className="font-bold">News Portal</span>
          </Link>
          <p className="text-sm text-muted-foreground">Your trusted source for the latest news and updates.</p>
        </div>
        <div className="grid grid-cols-2 gap-12 sm:grid-cols-3">
          <div className="space-y-2">
            <h4 className="font-medium">Topics</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/topics/politics" className="hover:underline">
                  Politics
                </Link>
              </li>
              <li>
                <Link href="/topics/sports" className="hover:underline">
                  Sports
                </Link>
              </li>
              <li>
                <Link href="/topics/entertainment" className="hover:underline">
                  Entertainment
                </Link>
              </li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">Company</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/about" className="hover:underline">
                  About
                </Link>
              </li>
              <li>
                <Link href="/careers" className="hover:underline">
                  Careers
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:underline">
                  Contact
                </Link>
              </li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/privacy" className="hover:underline">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:underline">
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div className="border-t">
        <div className="container flex flex-col items-center gap-2 py-4 md:flex-row md:justify-between">
          <p className="text-center text-sm text-muted-foreground">
            © {new Date().getFullYear()} News Portal. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}

