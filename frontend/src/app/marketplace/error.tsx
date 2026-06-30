'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { RotateCcw } from 'lucide-react';

export default function MarketplaceError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="container py-16 text-center space-y-4 max-w-md mx-auto">
      <h2 className="text-2xl font-bold text-red-600">Failed to Load Projects</h2>
      <p className="text-neutral-500 dark:text-neutral-400">
        Could not load the decarbonization projects from the carbon intelligence registry. Please ensure the API services are active.
      </p>
      <Button onClick={() => reset()} className="flex items-center gap-2 mx-auto">
        <RotateCcw className="h-4 w-4" />
        Retry Connection
      </Button>
    </div>
  );
}
