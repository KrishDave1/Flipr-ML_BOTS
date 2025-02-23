import Image from "next/image"
import { notFound } from "next/navigation"
import { topicSubtopics, type TopicKey } from "@/lib/topics"

interface ArticlePageProps {
  params: {
    topic: TopicKey
    articleId: string
  }
}

// This would typically come from an API or database
const getArticle = (topic: string, articleId: string) => {
  // Simulating an article fetch
  if (Object.keys(topicSubtopics).includes(topic) && Number.parseInt(articleId) > 0) {
    return {
      id: articleId,
      title: `${topic.charAt(0).toUpperCase() + topic.slice(1)} Article ${articleId}`,
      content: `This is a detailed article about ${topic}. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam euismod, nisi vel consectetur interdum, nisl nunc egestas nunc, vitae tincidunt nisl nunc euismod nunc. Sed euismod, nisi vel consectetur interdum, nisl nunc egestas nunc, vitae tincidunt nisl nunc euismod nunc.

      Nullam euismod, nisi vel consectetur interdum, nisl nunc egestas nunc, vitae tincidunt nisl nunc euismod nunc. Sed euismod, nisi vel consectetur interdum, nisl nunc egestas nunc, vitae tincidunt nisl nunc euismod nunc.
      
      Nullam euismod, nisi vel consectetur interdum, nisl nunc egestas nunc, vitae tincidunt nisl nunc euismod nunc. Sed euismod, nisi vel consectetur interdum, nisl nunc egestas nunc, vitae tincidunt nisl nunc euismod nunc.`,
      image: "/placeholder.svg",
      subtopic: topicSubtopics[topic as TopicKey][0], // Just using the first subtopic for this example
      date: new Date().toLocaleDateString(),
      author: "John Doe",
    }
  }
  return null
}

export default function ArticlePage({ params }: ArticlePageProps) {
  const article = getArticle(params.topic, params.articleId)

  if (!article) {
    notFound()
  }

  return (
    <article className="container max-w-4xl py-6 md:py-12">
      <header className="mb-8">
        <h1 className="mb-2 text-3xl font-bold md:text-4xl lg:text-5xl">{article.title}</h1>
        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
          <span>{article.date}</span>
          <span>•</span>
          <span>By {article.author}</span>
          <span>•</span>
          <span className="capitalize">{article.subtopic}</span>
        </div>
      </header>
      <Image
        src={article.image || "/placeholder.svg"}
        alt={article.title}
        width={1200}
        height={600}
        className="mb-8 aspect-video rounded-lg object-cover"
      />
      <div className="prose max-w-none">
        {article.content.split("\n\n").map((paragraph, index) => (
          <p key={index}>{paragraph}</p>
        ))}
      </div>
    </article>
  )
}

