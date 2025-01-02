'use client'

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { fetchPaper } from '@/lib/papers';
import { Paper } from '@prisma/client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatDate } from '@/lib/utils';

interface PaperChatProps {
  paperId: string;
}

const PaperChat: React.FC<PaperChatProps> = ({ paperId }) => {
  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(true);
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'loading') return;
    if (!session) {
      router.push('/login');
      return;
    }

    const loadPaper = async () => {
      setLoading(true);
      try {
        const fetchedPaper = await fetchPaper(paperId);
        if (!fetchedPaper) {
          console.error('Paper not found');
          router.push('/');
          return;
        }
        setPaper(fetchedPaper);
      } catch (error) {
        console.error('Error fetching paper:', error);
        router.push('/');
      } finally {
        setLoading(false);
      }
    };
    loadPaper();
  }, [paperId, session, status, router]);

  if (!paper || loading || status === 'loading') {
    return null;
  }

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto">
      <motion.div 
        className="p-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-bold leading-tight">
              {paper.title}
            </CardTitle>
            <div className="pt-4 border-t">
              <div className="space-y-2 text-sm text-muted-foreground">
                {paper.authors && (
                  <div className="font-medium">
                    {paper.authors}
                  </div>
                )}
                <div className="font-medium">
                  Added: {formatDate(paper.createdAt)}
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none [&>p]:mb-4">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {paper.summary}
              </ReactMarkdown>
            </div>
            
            <div className="mt-6 pt-4 border-t">
              <a 
                href={paper.url} 
                target="_blank" 
                rel="noopener noreferrer" 
                className="text-primary hover:underline inline-flex items-center"
              >
                Read Full Paper →
              </a>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
};

export default PaperChat; 