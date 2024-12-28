'use client'

import { useParams } from 'next/navigation';
import PaperChat from '@/components/paper-chat';

const PaperDetailPage: React.FC = () => {
  const params = useParams();
  const { id } = params as { id: string };

  return (
    <div className="h-screen no-scrollbar overflow-y-auto">
      <PaperChat paperId={id} />
    </div>
  );
};

export default PaperDetailPage; 