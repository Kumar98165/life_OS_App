import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 1000 * 60 * 5, // 5 minutes fresh window
      gcTime: 1000 * 60 * 15, // 15 minutes garbage collection (reduced from default 24h to save memory on 2GB devices)
      refetchOnWindowFocus: false, // Prevent aggressive background refetches on low-end devices
      refetchOnReconnect: 'always',
    },
  },
});

