'use client'

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { fetchPaper } from '@/lib/papers';
import { Paper } from '@prisma/client';
import { Button } from '@/components/ui/button';
import { Copy } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface PaperChatProps {
  paperId: string;
}

const PaperChat: React.FC<PaperChatProps> = ({ paperId }) => {
  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(true);
  const { data: session, status } = useSession();
  const router = useRouter();
  const [copied, setCopied] = useState<boolean>(false);

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

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1000);
    });
  };

  if (!paper || loading || status === 'loading') {
    return null;
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">{paper.title}</h2>
        <Button variant="ghost" onClick={() => handleCopy(paper.url)} title="Copy URL">
          <Copy className="h-4 w-4" />
        </Button>
        {copied && <span className="text-sm text-green-500">Copied!</span>}
      </div>
      <p className="text-md mb-2"><strong>Authors:</strong> {paper.authors}</p>
      <p className="text-md mb-4"><strong>Summary:</strong></p>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {paper.summary}
      </ReactMarkdown>
      <a href={paper.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline mt-4 block">
        Read Full Paper
      </a>
    </div>
  );
};

export default PaperChat; 