import Link from "next/link";

export default function Home() {
  return (
    <section style={{ maxWidth: "800px", margin: "0 auto", paddingTop: "3rem" }}>
        <h1>Reddit Comment Engagement Agent</h1>
        <p style={{ fontSize: "1.25rem", color: "var(--text-muted)", marginBottom: "2rem" }}>
          A compliance-first, AI-powered Reddit engagement bot with quality scoring,
          intelligent selection, and human-in-the-loop approval.
        </p>

        <div style={{ display: "flex", gap: "1rem", marginBottom: "3rem" }}>
          <Link href="/getting-started" className="btn btn-primary">
            Get Started
          </Link>
          <Link href="/architecture" className="btn btn-secondary">
            View Architecture
          </Link>
        </div>

        <div className="card">
          <h2>Overview</h2>
          <p>
            The Reddit Agent is a sophisticated engagement system that automatically generates
            high-quality comment replies while maintaining strict compliance with Reddit's guidelines.
            Built with LangGraph and powered by Google's Gemini 2.5 Flash, it includes advanced features like:
          </p>

          <ul>
            <li><strong>7-Factor Quality Scoring</strong> - AI-powered scoring based on upvote ratio, karma, freshness, and more</li>
            <li><strong>Inbox Priority System</strong> - Prioritizes direct replies with separate cooldowns</li>
            <li><strong>Subreddit Diversity</strong> - Limits comments per subreddit with quality overrides</li>
            <li><strong>Human-in-the-Loop</strong> - All drafts require approval via Slack/Telegram before posting</li>
            <li><strong>Historical Learning</strong> - Learns from past performance per subreddit</li>
            <li><strong>Shadowban Detection</strong> - Circuit breaker halts operations on high risk</li>
          </ul>
        </div>

        <div className="card">
          <h2>Key Features</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1rem" }}>
            <div>
              <h3>Safety First</h3>
              <p style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>
                ≤8 comments/day, subreddit allow-lists, bot filtering, and anti-fingerprinting measures
              </p>
            </div>
            <div>
              <h3>Quality Driven</h3>
              <p style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>
                7-factor AI scoring with historical learning and performance tracking
              </p>
            </div>
            <div>
              <h3>Fully Auditable</h3>
              <p style={{ fontSize: "0.875rem", color: "var(--text-muted)" }}>
                SQLite database tracks all actions, decisions, and outcomes
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <h2>Quick Start</h2>
          <pre><code>{`# Clone and setup
git clone https://github.com/yourusername/reddit_agent.git
cd reddit_agent

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure .env file
cp .env.example .env
# Edit .env with your credentials

# Run migrations
alembic upgrade head

# Start callback server (for approvals)
python main.py server

# In another terminal: Run agent
python main.py run --once`}</code></pre>
        </div>

        <div className="card">
          <h2>Architecture Highlights</h2>
          <p>
            The agent uses a <strong>13-node LangGraph workflow</strong> that processes candidates through:
          </p>
          <ol>
            <li>Fetch candidates (inbox replies + rising content)</li>
            <li>Apply post/comment ratio distribution (30/70)</li>
            <li>Score with 7-factor AI quality system</li>
            <li>Filter cooldowns and duplicates</li>
            <li>Verify subreddit compliance</li>
            <li>Sort by (priority, quality_score) with 25% exploration</li>
            <li>Apply diversity limits (max 2/subreddit, 1/post)</li>
            <li>Check daily limits (≤8/day)</li>
            <li>Build vertical context chain</li>
            <li>Generate draft with Gemini 2.5 Flash</li>
            <li>Send for human approval</li>
            <li>Auto-publish approved drafts</li>
            <li>Track 24h engagement metrics</li>
          </ol>
        </div>

        <div className="callout callout-info">
          <p>
            <strong>Status:</strong> Version 2.5 - Fully operational with smart selection and auto-publishing.
            136 tests passing, 4 database migrations applied.
          </p>
        </div>

        <footer style={{
          textAlign: "center",
          marginTop: "3rem",
          paddingTop: "2rem",
          borderTop: "1px solid var(--border)",
          color: "var(--text-muted)",
          fontSize: "0.875rem"
        }}>
          <p>Reddit Comment Engagement Agent v2.5 | Built with LangGraph + Gemini 2.5 Flash</p>
        </footer>
      </section>
  );
}
