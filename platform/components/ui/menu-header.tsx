import React from 'react'
import { Button } from '@/components/ui/button'
import { Plus, ArrowLeft } from 'lucide-react'
import { motion } from 'framer-motion'

interface MenuHeaderProps {
  showBackButton?: boolean
  onBack?: () => void
  onNewChat?: (e: React.MouseEvent) => void
  title: string
}

export function MenuHeader({ 
  showBackButton, 
  onBack, 
  onNewChat,
  title 
}: MenuHeaderProps) {
  return (
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
      {showBackButton && (
        <Button
          variant="ghost"
          size="icon"
          onClick={onBack}
          className="h-8 w-8 group relative"
          title="Home"
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
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
  )
} 