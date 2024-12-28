import React, { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Plus, ArrowLeft, Home, FileText, Search } from 'lucide-react'
import { motion } from 'framer-motion'
import { useMenu } from '@/context/MenuContext'
import Link from 'next/link'

interface MenuHeaderProps {
  showBackButton?: boolean
  onBack?: () => void
  onNewChat?: (e: React.MouseEvent) => void
  title: string
  type?: 'researches' | 'papers'
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

  const renderList = () => {
    if (type === 'papers') {
      return papers.map((paper) => (
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
      ))
    }

    if (type === 'researches') {
      return researches.map((research) => (
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