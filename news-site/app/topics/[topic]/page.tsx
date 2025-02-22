import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import Image from "next/image"
import { ChevronLeft, ChevronRight } from "lucide-react"

interface TopicPageProps {
  params: {
    topic: string
  }
  searchParams: {
    page?: string
  }
}

// This would typically come from an API or database
const articles = Array.from({ length: 12 }).map((_, i) => ({
  id: i + 1,
  title: `Article ${i + 1} about ${i % 2 === 0 ? "breaking news" : "latest developments"}`,
  excerpt:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
  image: "/placeholder.svg?height=400&width=600",
  href: `/topics/politics/${i + 1}`,
}))

export default function TopicPage({ params, searchParams }: TopicPageProps) {
  const currentPage = Number(searchParams.page) || 1
  const itemsPerPage = 9
  const totalPages = Math.ceil(articles.length / itemsPerPage)

  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentArticles = articles.slice(startIndex, endIndex)

  return (
    <div className="container py-6 md:py-12">
      <h1 className="mb-8 text-4xl font-bold capitalize">{params.topic}</h1>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {currentArticles.map((article) => (
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
                <CardTitle className="mb-2 line-clamp-2">{article.title}</CardTitle>
                <p className="line-clamp-3 text-sm text-muted-foreground">{article.excerpt}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="mt-8 flex items-center justify-center gap-2">
        <Button variant="outline" size="icon" disabled={currentPage <= 1} asChild>
          <Link href={`/topics/${params.topic}?page=${currentPage - 1}`}>
            <ChevronLeft className="h-4 w-4" />
          </Link>
        </Button>
        <span className="text-sm text-muted-foreground">
          Page {currentPage} of {totalPages}
        </span>
        <Button variant="outline" size="icon" disabled={currentPage >= totalPages} asChild>
          <Link href={`/topics/${params.topic}?page=${currentPage + 1}`}>
            <ChevronRight className="h-4 w-4" />
          </Link>
        </Button>
      </div>
    </div>
  )
}

