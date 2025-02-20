'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import ResearchChat from '@/components/research-chat'
import { useMenu } from '@/context/MenuContext'
import { useSession } from 'next-auth/react'
import { Research } from '@prisma/client'

const ResearchPage = () => {
  const params = useParams()
  const id = params?.id as string
  const router = useRouter()
  const { setSelectedResearch, researches, loadingResearches } = useMenu()
  const { status } = useSession()

  useEffect(() => {
    if (status === "loading") return
    if (!id) {
      router.push('/')
      return
    }

    if (!loadingResearches && researches.length > 0) {
      const research = researches.find((research: Research) => research.id === id)
      if (research) {
        setSelectedResearch(research)
      } else {
        router.push('/')
      }
    }
  }, [id, researches, setSelectedResearch, router, loadingResearches, status])

  if (status === "loading" || !id || loadingResearches) return null

  return (
    <ResearchChat researchId={id} />
  )
}

export default ResearchPage
