import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import Image from "next/image"

// This would typically come from an API or database
const featuredArticles = [
  {
    id: 1,
    title: "Major Political Reform Announced",
    excerpt: "Government unveils new legislative package aimed at modernizing...",
    topic: "Politics",
    image: "/placeholder.svg?height=400&width=600",
    href: "/topics/politics/1",
  },
  {
    id: 2,
    title: "Championship Finals Set to Begin",
    excerpt: "The stage is set for an epic showdown as teams prepare for...",
    topic: "Sports",
    image: "/placeholder.svg?height=400&width=600",
    href: "/topics/sports/2",
  },
  {
    id: 3,
    title: "New Blockbuster Breaks Records",
    excerpt: "Latest summer release shatters box office expectations with...",
    topic: "Entertainment",
    image: "/placeholder.svg?height=400&width=600",
    href: "/topics/entertainment/3",
  },
]

export default function Home() {
  return (
    <div className="container py-6 md:py-12">
      <section className="mb-12">
        <h1 className="mb-8 text-4xl font-bold">Top Stories</h1>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {featuredArticles.map((article) => (
            <Link key={article.id} href={article.href}>
              <Card className="h-full overflow-hidden transition-shadow hover:shadow-lg">
                <CardHeader className="p-0">
                  <Image
                    src={article.image || "/placeholder.svg"}
                    alt={article.title}
                    width={600}
                    height={400}
                    className="aspect-video object-cover"
                  />
                </CardHeader>
                <CardContent className="p-4">
                  <div className="mb-2 text-sm font-medium text-primary">{article.topic}</div>
                  <CardTitle className="mb-2 line-clamp-2">{article.title}</CardTitle>
                  <p className="line-clamp-3 text-sm text-muted-foreground">{article.excerpt}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}

