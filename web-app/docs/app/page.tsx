import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { CodeBlock } from "@/components/docs";
import { CheckCircle, Shield, BarChart3, Database, Info } from "lucide-react";

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <section className="py-12 text-center">
        <Badge variant="secondary" className="mb-4">v2.5 - Production Ready</Badge>
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Reddit Comment Engagement Agent
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          A compliance-first, AI-powered Reddit engagement bot with quality scoring,
          intelligent selection, and human-in-the-loop approval.
        </p>
        <div className="flex gap-4 justify-center">
          <Button asChild size="lg">
            <Link href="/getting-started">Get Started</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/architecture">View Architecture</Link>
          </Button>
        </div>
      </section>

      {/* Overview Card */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Overview</CardTitle>
          <CardDescription>
            Built with LangGraph and powered by Google&apos;s Gemini 2.5 Flash
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="mb-4">
            The Reddit Agent is a sophisticated engagement system that automatically generates
            high-quality comment replies while maintaining strict compliance with Reddit&apos;s guidelines.
          </p>
          <ul className="space-y-2">
            <li className="flex items-start gap-2">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
              <span><strong>7-Factor Quality Scoring</strong> - AI-powered scoring based on upvote ratio, karma, freshness, and more</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
              <span><strong>Inbox Priority System</strong> - Prioritizes direct replies with separate cooldowns</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
              <span><strong>Subreddit Diversity</strong> - Limits comments per subreddit with quality overrides</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
              <span><strong>Human-in-the-Loop</strong> - All drafts require approval via Slack/Telegram before posting</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
              <span><strong>Historical Learning</strong> - Learns from past performance per subreddit</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
              <span><strong>Shadowban Detection</strong> - Circuit breaker halts operations on high risk</span>
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* Key Features Grid */}
      <h2 className="text-2xl font-bold mb-4">Key Features</h2>
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <Shield className="h-8 w-8 text-primary mb-2" />
            <CardTitle className="text-lg">Safety First</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              ≤8 comments/day, subreddit allow-lists, bot filtering, and anti-fingerprinting measures
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <BarChart3 className="h-8 w-8 text-primary mb-2" />
            <CardTitle className="text-lg">Quality Driven</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              7-factor AI scoring with historical learning and performance tracking
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <Database className="h-8 w-8 text-primary mb-2" />
            <CardTitle className="text-lg">Fully Auditable</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              SQLite database tracks all actions, decisions, and outcomes
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Start */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Quick Start</CardTitle>
          <CardDescription>Get up and running in minutes</CardDescription>
        </CardHeader>
        <CardContent>
          <CodeBlock language="bash">{`# Clone and setup
git clone https://github.com/avisangle/reddit_agent.git
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
python main.py run --once`}</CodeBlock>
        </CardContent>
      </Card>

      {/* Architecture Highlights */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Architecture Highlights</CardTitle>
          <CardDescription>13-node LangGraph workflow</CardDescription>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-1 text-sm">
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
        </CardContent>
      </Card>

      {/* Status Alert */}
      <Alert className="mb-8">
        <Info className="h-4 w-4" />
        <AlertTitle>Status</AlertTitle>
        <AlertDescription>
          Version 2.5 - Fully operational with smart selection and auto-publishing.
          136 tests passing, 4 database migrations applied.
        </AlertDescription>
      </Alert>

      {/* Footer */}
      <footer className="text-center py-8 border-t text-sm text-muted-foreground">
        <p>Reddit Comment Engagement Agent v2.5 | Built with LangGraph + Gemini 2.5 Flash</p>
      </footer>
    </div>
  );
}
