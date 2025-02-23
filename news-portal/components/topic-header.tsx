"use client"

import { Button } from "@/components/ui/button"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import { topicSubtopics, type TopicKey } from "@/lib/topics"
import Link from "next/link"
import { useSearchParams } from "next/navigation"

interface TopicHeaderProps {
  topic: TopicKey
}

export function TopicHeader({ topic }: TopicHeaderProps) {
  const searchParams = useSearchParams()
  const currentSubtopic = searchParams.get("subtopic")
  const subtopics = topicSubtopics[topic]

  return (
    <div className="mb-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-4xl font-bold capitalize">{topic}</h1>
      </div>
      <ScrollArea className="w-full whitespace-nowrap">
        <div className="flex w-max space-x-2 p-1">
          <Button variant={!currentSubtopic ? "secondary" : "ghost"} size="sm" className="text-sm" asChild>
            <Link href={`/topics/${topic}`}>All</Link>
          </Button>
          {subtopics.map((subtopic) => (
            <Button
              key={subtopic}
              variant={currentSubtopic === subtopic ? "secondary" : "ghost"}
              size="sm"
              className="text-sm"
              asChild
            >
              <Link href={`/topics/${topic}?subtopic=${encodeURIComponent(subtopic)}`}>{subtopic}</Link>
            </Button>
          ))}
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
    </div>
  )
}

