import React, { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Plus, ArrowLeft, Home, FileText, Search } from 'lucide-react'
import { motion } from 'framer-motion'
import { useMenu } from '@/context/MenuContext'
import Link from 'next/link'
import { Research, Paper } from '@prisma/client'
import { formatDate } from '@/lib/utils'

interface MenuHeaderProps {
  showBackButton?: boolean
  onBack?: () => void
  onNewChat?: (e: React.MouseEvent) => void
  title: string
  type?: 'researches' | 'papers'
}

interface GroupedItems {
  [key: string]: Array<Research | Paper>
}

export function MenuHeader({ 
  showBackButton, 
  onBack, 
  onNewChat,
  title,
  type
}: MenuHeaderProps) {
  const { papers, researches, fetchPapers } = useMenu()
  const [hasFetchedPapers, setHasFetchedPapers] = useState(false)

  useEffect(() => {
    if (type === 'papers' && !hasFetchedPapers) {
      fetchPapers()
      setHasFetchedPapers(true)
    }
  }, [type, fetchPapers, hasFetchedPapers])

  const groupItemsByDate = (items: Array<Research | Paper>): GroupedItems => {
    return items.reduce((groups: GroupedItems, item) => {
      const updatedAt = new Date(item.updatedAt)
      const formattedDate = formatDate(updatedAt)
      
      if (!groups[formattedDate]) {
        groups[formattedDate] = []
      }
      groups[formattedDate].push(item)
      return groups
    }, {})
  }

  const renderList = () => {
    if (type === 'papers') {
      const groupedPapers = groupItemsByDate(papers)
      return Object.entries(groupedPapers).map(([date, items]) => (
        <div key={date}>
          <div className="text-sm font-bold text-primary-foreground/70 px-4 py-2">{date}</div>
          {items.map((paper) => (
            <motion.li
              key={paper.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="w-full"
            >
              <Button
                variant="ghost"
                className="w-full justify-start text-base py-4"
                asChild
              >
                <Link href={`/papers/${paper.id}`}>
                  <FileText className="mr-3 h-5 w-5 shrink-0" />
                  <span className="truncate">{paper.title}</span>
                </Link>
              </Button>
            </motion.li>
          ))}
        </div>
      ))
    }

    if (type === 'researches') {
      const groupedResearches = groupItemsByDate(researches)
      return Object.entries(groupedResearches).map(([date, items]) => (
        <div key={date}>
          <div className="text-sm font-bold text-primary-foreground/70 px-4 py-2">{date}</div>
          {items.map((research: Research) => (
            <motion.li
              key={research.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="w-full"
            >
              <Button
                variant="ghost"
                className="w-full justify-start text-base py-4"
                asChild
              >
                <Link href={`/researches/${research.id}`}>
                  <Search className="mr-3 h-5 w-5 shrink-0" />
                  <span className="truncate">{research.title}</span>
                </Link>
              </Button>
            </motion.li>
          ))}
        </div>
      ))
    }

    return null
  }

  return (
    <>
      <motion.div 
        className="flex items-center gap-2 mb-6"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ 
          duration: 0.4,
          delay: 0.2,
          ease: "easeOut"
        }}
      >
        {showBackButton ? (
          <Button
            variant="ghost"
            size="icon"
            onClick={onBack}
            className="h-8 w-8 group relative"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
        ) : (
          <div className="h-8 w-8 flex items-center justify-center">
            <Home className="h-4 w-4" />
          </div>
        )}
        <motion.div 
          className="flex-1"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ 
            duration: 0.3, 
            delay: 0.1,
            ease: "easeOut"
          }}
        >
          <h2 className="text-2xl font-bold">{title}</h2>
        </motion.div>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={onNewChat}
          title="New research"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </motion.div>
      
      <div className="h-px bg-primary-foreground mb-2" />

      {type && (
        <>
          <ul>
            {renderList()}
          </ul>
        </>
      )}
    </>
  )
} 