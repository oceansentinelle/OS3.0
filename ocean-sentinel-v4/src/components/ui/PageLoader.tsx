/**
 * Page Loader Component
 * Skeleton loader pour les transitions de pages
 */

export function PageLoader() {
  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header skeleton */}
        <div className="h-16 bg-muted rounded-lg animate-shimmer" />
        
        {/* Content skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-48 bg-muted rounded-lg animate-shimmer" />
          ))}
        </div>
      </div>
    </div>
  )
}
