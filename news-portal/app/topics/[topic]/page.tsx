import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TopicHeader } from "@/components/topic-header"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import Image from "next/image"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { topicSubtopics, type TopicKey } from "@/lib/topics"

interface TopicPageProps {
  params: {
    topic: TopicKey
  }
  searchParams: {
    page?: string
    subtopic?: string
  }
}

// This would typically come from an API or database
const generateArticles = (topic: string, subtopic?: string) => {
  return Array.from({ length: 50 }).map((_, i) => ({
    id: i + 1,
    title: `${subtopic || topic} Article ${i + 1}`,
    excerpt: `Latest news about ${subtopic || topic}. Lorem ipsum dolor sit amet, consectetur adipiscing elit.`,
    image: "/placeholder.svg",
    href: `/topics/${topic}/${i + 1}`,
    subtopic: subtopic || topic,
  }))
}

export default function TopicPage({ params, searchParams }: TopicPageProps) {
  const currentPage = Number(searchParams.page) || 1
  const subtopic = searchParams.subtopic
  const itemsPerPage = 9

  // Validate topic
  if (!Object.keys(topicSubtopics).includes(params.topic)) {
    return <div className="container py-6">Topic not found</div>
  }

  const allArticles = generateArticles(params.topic, subtopic)
  const totalPages = Math.ceil(allArticles.length / itemsPerPage)

  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentArticles = allArticles.slice(startIndex, endIndex)

  return (
    <div className="container py-6 md:py-12">
      <TopicHeader topic={params.topic} />

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
                <div className="mb-2 text-sm font-medium text-primary">{article.subtopic}</div>
                <CardTitle className="mb-2 line-clamp-2">{article.title}</CardTitle>
                <p className="line-clamp-3 text-sm text-muted-foreground">{article.excerpt}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="mt-8 flex items-center justify-center gap-2">
        <Button variant="outline" size="icon" disabled={currentPage <= 1} asChild>
          <Link
            href={{
              pathname: `/topics/${params.topic}`,
              query: {
                ...(subtopic && { subtopic }),
                page: currentPage > 1 ? currentPage - 1 : 1,
              },
            }}
          >
            <ChevronLeft className="h-4 w-4" />
          </Link>
        </Button>
        <span className="text-sm text-muted-foreground">
          Page {currentPage} of {totalPages}
        </span>
        <Button variant="outline" size="icon" disabled={currentPage >= totalPages} asChild>
          <Link
            href={{
              pathname: `/topics/${params.topic}`,
              query: {
                ...(subtopic && { subtopic }),
                page: currentPage < totalPages ? currentPage + 1 : totalPages,
              },
            }}
          >
            <ChevronRight className="h-4 w-4" />
          </Link>
        </Button>
      </div>
    </div>
  )
}

