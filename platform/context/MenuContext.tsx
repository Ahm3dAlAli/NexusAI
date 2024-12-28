'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { fetchResearches } from '@/lib/researches'
import { fetchPapers as fetchUserPapers } from '@/lib/papers'
import { Research, Paper } from '@prisma/client'

interface MenuContextType {
  researches: Research[]
  papers: Paper[]
  loadingResearches: boolean
  loadingPapers: boolean
  selectedResearch: Research | null
  setSelectedResearch: (research: Research | null) => void
  createResearch: (data: { title: string }) => Promise<Research | null>
  fetchPapers: () => Promise<void>
}

const MenuContext = createContext<MenuContextType | undefined>(undefined)

export const MenuProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [researches, setResearches] = useState<Research[]>([])
  const [papers, setPapers] = useState<Paper[]>([])
  const [loadingResearches, setLoadingResearches] = useState<boolean>(false)
  const [loadingPapers, setLoadingPapers] = useState<boolean>(false)
  const [selectedResearch, setSelectedResearch] = useState<Research | null>(null)

  const loadResearches = async () => {
    setLoadingResearches(true)
    try {
      const data = await fetchResearches()
      setResearches(data)
    } catch (error) {
      console.error('Failed to fetch researches:', error)
    } finally {
      setLoadingResearches(false)
    }
  }

  const loadPapers = async () => {
    setLoadingPapers(true)
    try {
      const data = await fetchUserPapers()
      setPapers(data)
    } catch (error) {
      console.error('Failed to fetch papers:', error)
    } finally {
      setLoadingPapers(false)
    }
  }

  useEffect(() => {
    loadResearches()
  }, [])

  useEffect(() => {
    loadPapers()
  }, [])

  const createResearch = async (data: { title: string }) => {
    try {
      const response = await fetch('/api/researches', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      if (response.ok) {
        const newResearch = await response.json()
        setResearches([newResearch, ...researches])
        return newResearch
      }
    } catch (error) {
      console.error('Error creating research:', error)
    }
    return null
  }

  const fetchPapers = async () => {
    await loadPapers()
  }

  return (
    <MenuContext.Provider value={{
      researches,
      papers,
      loadingResearches,
      loadingPapers,
      selectedResearch,
      setSelectedResearch,
      createResearch,
      fetchPapers,
    }}>
      {children}
    </MenuContext.Provider>
  )
}

export const useMenu = () => {
  const context = useContext(MenuContext)
  if (!context) {
    throw new Error('useMenu must be used within a MenuProvider')
  }
  return context
}