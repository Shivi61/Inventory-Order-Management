// Simple shimmer placeholder used while data loads.
export default function Skeleton({ rows = 4 }) {
  return (
    <div className="skeleton-wrap">
      {Array.from({ length: rows }).map((_, i) => (
        <div className="skeleton-row" key={i} />
      ))}
    </div>
  )
}
