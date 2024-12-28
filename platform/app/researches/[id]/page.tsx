'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Chat from '@/components/chat'
import { useResearches } from '@/context/ResearchesContext'
import { useSession } from 'next-auth/react'

const ResearchPage = () => {
  const params = useParams()
  const id = params?.id as string
  const router = useRouter()
  const { setSelectedResearch, researches, loading } = useResearches()
  const { status } = useSession()

  useEffect(() => {
    if (status === "loading") return
    if (!id) {
      router.push('/')
      return
    }

    if (!loading && researches.length > 0) {
      const research = researches.find(research => research.id === id)
      if (research) {
        setSelectedResearch(research)
      } else {
        router.push('/')
      }
    }
  }, [id, researches, setSelectedResearch, router, loading, status])

  if (status === "loading" || !id || loading) return null

  return (
    <Chat researchId={id} />
  )
}

export default ResearchPage
