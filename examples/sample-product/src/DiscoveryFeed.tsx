// Sample Discovery Feed demonstrating Tribe, Hunt, and Self Variable Rewards
export function DiscoveryFeed({ items, userReputation }: { items: any[], userReputation: number }) {
  return (
    <div className="discovery-feed">
      {/* Rewards of the Tribe: Social recognition and peer upvotes */}
      <div className="leaderboard">
        <span>Global Creator Rank: #{userReputation}</span>
        <span className="badge">Top 5% Contributor</span>
      </div>

      {/* Rewards of the Hunt: Variable stream of unexpected inspiration */}
      <div className="infinite-scroll-feed">
        {items.map((item) => (
          <article key={item.id} className="feed-item">
            <h3>{item.title}</h3>
            <button aria-label="like">❤️ {item.likesCount}</button>
          </article>
        ))}
      </div>
    </div>
  );
}
