'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { fetchResearches, createResearch as apiCreateResearch } from '@/lib/researches'
import { useSession } from 'next-auth/react'

interface CreateResearchParams {
  title: string
}

interface Research {
  id: string
  title: string
  updatedAt: Date
}

interface ResearchesContextType {
  researches: Research[]
  loading: boolean
  createResearch: (params: CreateResearchParams) => Promise<Research | null>
  selectedResearch: Research | null
  setSelectedResearch: (research: Research | null) => void
}

const ResearchesContext = createContext<ResearchesContextType | undefined>(undefined)

export const useResearches = () => {
  const context = useContext(ResearchesContext)
  if (!context) {
    throw new Error('useResearches must be used within a ResearchesProvider')
  }
  return context
}

export const ResearchesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [researches, setResearches] = useState<Research[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedResearch, setSelectedResearch] = useState<Research | null>(null)
  const { data: session } = useSession()

  const loadResearches = async () => {
    if (!session) return
    setLoading(true)
    try {
      const convs = await fetchResearches()
      setResearches(convs)
    } catch (error) {
      console.error('Error fetching researches:', error)
    } finally {
      setLoading(false)
    }
  }

  const createResearch = async ({ title }: CreateResearchParams): Promise<Research | null> => {
    if (!session) return null
    try {
      const newConv = await apiCreateResearch({ title })
      setResearches((prev) => [newConv, ...prev])
      setSelectedResearch(newConv)
      return newConv
    } catch (error) {
      console.error('Error creating research:', error)
      return null
    }
  }

  useEffect(() => {
    loadResearches()
  }, [session])

  return (
    <ResearchesContext.Provider value={{ 
        researches, 
        loading, 
        createResearch, 
        selectedResearch, 
        setSelectedResearch 
      }}>
      {children}
    </ResearchesContext.Provider>
  )
}