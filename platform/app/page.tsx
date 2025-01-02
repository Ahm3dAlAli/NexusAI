'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input, InputWrapper } from '@/components/ui/input'
import ResearchChat from '@/components/research-chat'
import { useMenu } from '@/context/MenuContext'
import { motion } from 'framer-motion'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { Card } from '@/components/ui/card'
import { Sparkles } from 'lucide-react'
import { Icons } from '@/components/ui/icons'
const exampleQuestions = [
  {
    title: "Quantum Computing",
    questions: [
      "Analyze new methodology used for quantum supremacy demonstrations",
      "What are the recent developments in quantum computing?",
    ]
  },
  {
    title: "Medical Science",
    questions: [
      "What's the current understanding of long COVID mechanisms?",
      "Summarize the latest findings in CRISPR gene editing technology",
    ]
  },
  {
    title: "Technology",
    questions: [
      "What are the latest advancements in renewable energy storage?",
      "Current state of autonomous vehicle technology",
    ]
  }
]

const Home: React.FC = () => {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [initialMessage, setInitialMessage] = useState<string | null>(null)
  const { createResearch, selectedResearch, setSelectedResearch } = useMenu()
  const [, setWindowHeight] = useState(0)
  const { data: session, status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === "loading") return
    if (!session) router.push('/login')
  }, [session, status, router])

  useEffect(() => {
    setWindowHeight(window.innerHeight)
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (input.trim() === '') return
    setLoading(true)
    try {
      const research = await createResearch({ 
        title: input.trim()
      })
      if (research) {
        setInitialMessage(input.trim())
        setInput('')
        setSelectedResearch(research)
      }
    } catch (error) {
      console.error('Failed to create research:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExampleClick = (question: string) => {
    setInput(question)
  }

  if (!session) {
    return null
  }

  return (
    <>
      {!selectedResearch ? (
        <div className="flex flex-col h-screen max-w-5xl mx-auto items-center justify-center no-scrollbar overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ 
              duration: 0.4,
              delay: 0.2,
              ease: "easeOut"
            }}
            className="text-center"
          >
            <h1 className="text-4xl font-bold mb-2">
            📚 NexusAI 🤖
            </h1>
            <p className="text-xl text-muted-foreground mb-4">
              Research scientific literature in minutes, not hours
            </p>
          </motion.div>
          <motion.div 
            className="flex justify-center w-full"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ 
              duration: 0.4,
              delay: 0.2,
              ease: "easeOut"
            }}
          >
            <form onSubmit={handleSubmit} className="flex w-full max-w-[800px] space-x-2">
              <InputWrapper>
                <Input
                  value={input}
                  onChange={handleInputChange}
                  placeholder="What do you want to research?"
                  disabled={loading}
                />
              </InputWrapper>
              <Button type="submit" disabled={loading} size="icon">
                <Icons.arrowRight className="h-4 w-4" />
              </Button>
            </form>
          </motion.div>
          <motion.div
            className="w-full max-w-[800px] mt-8"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ 
              duration: 0.4,
              delay: 0.4,
              ease: "easeOut"
            }}
          >
            <div className="flex items-center gap-2 mb-4 text-muted-foreground">
              <Sparkles className="h-5 w-5" />
              <h2 className="text-lg font-medium">Example research questions</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {exampleQuestions.map((category, idx) => (
                <div key={idx} className="space-y-2">
                  <h3 className="font-medium text-base pl-1">
                    {category.title}
                  </h3>
                  <div className="space-y-2">
                    {category.questions.map((question, qIdx) => (
                      <Card 
                        key={qIdx} 
                        className="p-3 hover:bg-accent/50 transition-colors cursor-pointer"
                        onClick={() => handleExampleClick(question)}
                      >
                        <span className="text-sm">
                          {question}
                        </span>
                      </Card>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      ) : (
        <div className="h-screen no-scrollbar overflow-y-auto">
          <ResearchChat
            researchId={selectedResearch.id}
            initialMessage={initialMessage || undefined}
          />
        </div>
      )}
    </>
  )
}
export default Home