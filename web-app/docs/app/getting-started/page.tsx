"use client"

import Link from "next/link"
import { Callout, CodeBlock, InlineCode, PageWrapper, PageHeader, Section, SectionHeader, SubSection, SubSectionHeader } from "@/components/docs"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Terminal, Server, Play, TestTube, Settings, Wrench } from "lucide-react"

export default function GettingStartedPage() {
  return (
    <PageWrapper className="py-8 px-4">
      <PageHeader
        title="Getting Started"
        description="Welcome to the Reddit Comment Engagement Agent! This guide will help you set up and run the agent."
      />

      <Section>
        <SectionHeader>Prerequisites</SectionHeader>
        <p className="text-muted-foreground mb-6">Before you begin, ensure you have:</p>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Terminal className="h-4 w-4 text-primary" />
                Python 3.11+
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Required runtime for the agent</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Settings className="h-4 w-4 text-primary" />
                Reddit API
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                <Link href="https://www.reddit.com/prefs/apps" className="text-primary hover:underline">Create app here</Link>
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Wrench className="h-4 w-4 text-primary" />
                LLM API Key
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Gemini recommended</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Server className="h-4 w-4 text-primary" />
                Notification Service
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Slack, Telegram, or webhook</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Play className="h-4 w-4 text-primary" />
                Public URL
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">ngrok for local, or cloud deploy</p>
            </CardContent>
          </Card>
        </div>
      </Section>

      <Section>
        <SectionHeader>Installation</SectionHeader>

        <SubSection>
          <SubSectionHeader>1. Clone the Repository</SubSectionHeader>
          <CodeBlock language="bash">{`git clone https://github.com/yourusername/reddit_agent.git
cd reddit_agent`}</CodeBlock>
        </SubSection>

        <SubSection>
          <SubSectionHeader>2. Create Virtual Environment</SubSectionHeader>
          <Tabs defaultValue="unix" className="w-full">
            <TabsList>
              <TabsTrigger value="unix">macOS / Linux</TabsTrigger>
              <TabsTrigger value="windows">Windows</TabsTrigger>
            </TabsList>
            <TabsContent value="unix" className="mt-4">
              <CodeBlock language="bash">{`python -m venv venv
source venv/bin/activate`}</CodeBlock>
            </TabsContent>
            <TabsContent value="windows" className="mt-4">
              <CodeBlock language="bash">{`python -m venv venv
venv\\Scripts\\activate`}</CodeBlock>
            </TabsContent>
          </Tabs>
          <Callout variant="warning">
            <strong>IMPORTANT</strong>: Always activate the virtual environment before running any Python commands!
          </Callout>
        </SubSection>

        <SubSection>
          <SubSectionHeader>3. Install Dependencies</SubSectionHeader>
          <CodeBlock language="bash">{`pip install -r requirements.txt`}</CodeBlock>
        </SubSection>
      </Section>

      <Section>
        <SectionHeader>Configuration</SectionHeader>

        <SubSection>
          <SubSectionHeader>1. Create Environment File</SubSectionHeader>
          <CodeBlock language="bash">{`cp .env.example .env`}</CodeBlock>
        </SubSection>

        <SubSection>
          <SubSectionHeader>2. Configure Required Variables</SubSectionHeader>
          <p className="text-muted-foreground mb-4">Edit <InlineCode>.env</InlineCode> with your credentials:</p>

          <Tabs defaultValue="reddit" className="w-full">
            <TabsList className="flex-wrap h-auto">
              <TabsTrigger value="reddit">Reddit API</TabsTrigger>
              <TabsTrigger value="subreddits">Subreddits</TabsTrigger>
              <TabsTrigger value="llm">LLM Keys</TabsTrigger>
              <TabsTrigger value="notifications">Notifications</TabsTrigger>
              <TabsTrigger value="url">Public URL</TabsTrigger>
            </TabsList>

            <TabsContent value="reddit" className="mt-4">
              <CodeBlock language="bash">{`REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=android:com.yourname.app:v2.1 (by /u/YourUsername)`}</CodeBlock>
            </TabsContent>

            <TabsContent value="subreddits" className="mt-4">
              <CodeBlock language="bash">{`ALLOWED_SUBREDDITS=sysadmin,learnpython,startups`}</CodeBlock>
              <Callout variant="warning">
                <strong>Safety First</strong>: Only add subreddits where you&apos;re an active, legitimate member. The agent enforces strict volume limits (≤8 comments/day) to avoid shadowbans.
              </Callout>
            </TabsContent>

            <TabsContent value="llm" className="mt-4">
              <CodeBlock language="bash">{`# Recommended: Gemini 2.5 Flash (fastest, cheapest)
GEMINI_API_KEY=your_gemini_api_key

# Alternatives
# OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key`}</CodeBlock>
            </TabsContent>

            <TabsContent value="notifications" className="mt-4 space-y-4">
              <div>
                <p className="font-medium mb-2">Option A: Slack</p>
                <CodeBlock language="bash">{`NOTIFICATION_TYPE=slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL`}</CodeBlock>
              </div>
              <div>
                <p className="font-medium mb-2">Option B: Telegram</p>
                <CodeBlock language="bash">{`NOTIFICATION_TYPE=telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id`}</CodeBlock>
              </div>
              <div>
                <p className="font-medium mb-2">Option C: Custom Webhook</p>
                <CodeBlock language="bash">{`NOTIFICATION_TYPE=webhook
WEBHOOK_URL=https://your-webhook-url.com/endpoint`}</CodeBlock>
              </div>
            </TabsContent>

            <TabsContent value="url" className="mt-4 space-y-4">
              <div>
                <p className="text-sm text-muted-foreground mb-2">Local development (ngrok):</p>
                <CodeBlock language="bash">{`PUBLIC_URL=https://xxxx.ngrok.io`}</CodeBlock>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-2">Production:</p>
                <CodeBlock language="bash">{`PUBLIC_URL=https://your-deployed-app.railway.app`}</CodeBlock>
              </div>
            </TabsContent>
          </Tabs>
        </SubSection>

        <SubSection>
          <SubSectionHeader>3. Database Setup</SubSectionHeader>
          <p className="text-muted-foreground">Run Alembic migrations to create the database:</p>
          <CodeBlock language="bash">{`source venv/bin/activate && alembic upgrade head`}</CodeBlock>

          <p className="text-muted-foreground mt-4">This creates <InlineCode>reddit_agent.db</InlineCode> with 6 tables:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground mt-2">
            <li><InlineCode>replied_items</InlineCode> - Tracks processed items</li>
            <li><InlineCode>draft_queue</InlineCode> - Draft comments awaiting approval</li>
            <li><InlineCode>subreddit_rules_cache</InlineCode> - Cached subreddit rules</li>
            <li><InlineCode>error_log</InlineCode> - Error tracking</li>
            <li><InlineCode>daily_stats</InlineCode> - Comment count tracking</li>
            <li><InlineCode>performance_history</InlineCode> - Draft performance metrics</li>
          </ul>
        </SubSection>
      </Section>

      <Section>
        <SectionHeader>Running the Agent</SectionHeader>
        <p className="text-muted-foreground mb-6">The agent requires <strong className="text-foreground">two terminals</strong>:</p>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="h-5 w-5 text-primary" />
                Terminal 1: Callback Server
              </CardTitle>
              <CardDescription>Handles approval buttons and auto-publishing</CardDescription>
            </CardHeader>
            <CardContent>
              <CodeBlock language="bash">{`source venv/bin/activate
python main.py server`}</CodeBlock>
              <Callout variant="info">
                The server runs on <InlineCode>http://localhost:8000</InlineCode> by default.
              </Callout>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Play className="h-5 w-5 text-primary" />
                Terminal 2: Agent Workflow
              </CardTitle>
              <CardDescription>Generates drafts and sends for approval</CardDescription>
            </CardHeader>
            <CardContent>
              <CodeBlock language="bash">{`source venv/bin/activate
python main.py run --once`}</CodeBlock>
              <Callout variant="success">
                The agent fetches candidates, scores them, generates drafts, and sends notifications.
              </Callout>
            </CardContent>
          </Card>
        </div>
      </Section>

      <Section>
        <SectionHeader>Approval Flow</SectionHeader>
        <ol className="list-decimal list-inside space-y-2 text-muted-foreground">
          <li><strong className="text-foreground">Agent generates draft</strong> → Sends to Slack/Telegram with approval buttons</li>
          <li><strong className="text-foreground">User clicks &quot;Approve&quot;</strong> → Opens <InlineCode>/approve?token=...</InlineCode> in browser</li>
          <li><strong className="text-foreground">Draft status changes</strong> to <InlineCode>APPROVED</InlineCode></li>
          <li><strong className="text-foreground">Auto-publish</strong>: Draft immediately posted to Reddit (background task)</li>
          <li><strong className="text-foreground">Draft status changes</strong> to <InlineCode>PUBLISHED</InlineCode></li>
        </ol>
      </Section>

      <Section>
        <SectionHeader>Testing with Dry Run</SectionHeader>
        <p className="text-muted-foreground">Test without posting to Reddit:</p>
        <CodeBlock language="bash">{`python main.py run --once --dry-run`}</CodeBlock>

        <div className="grid gap-2 mt-4">
          <div className="flex items-center gap-2">
            <Badge variant="default">✓</Badge>
            <span className="text-muted-foreground">Fetch candidates</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="default">✓</Badge>
            <span className="text-muted-foreground">Score with AI quality system</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="default">✓</Badge>
            <span className="text-muted-foreground">Generate drafts</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="default">✓</Badge>
            <span className="text-muted-foreground">Send for approval</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="destructive">✗</Badge>
            <span className="text-muted-foreground">NOT post to Reddit (even when approved)</span>
          </div>
        </div>
      </Section>

      <Section>
        <SectionHeader>Commands Reference</SectionHeader>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Command</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Description</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell><InlineCode>python main.py server</InlineCode></TableCell>
                <TableCell><Badge variant="secondary">Server</Badge></TableCell>
                <TableCell>Start callback server with auto-publish</TableCell>
              </TableRow>
              <TableRow>
                <TableCell><InlineCode>python main.py server --no-auto-publish</InlineCode></TableCell>
                <TableCell><Badge variant="secondary">Server</Badge></TableCell>
                <TableCell>Server without auto-publish</TableCell>
              </TableRow>
              <TableRow>
                <TableCell><InlineCode>python main.py run --once</InlineCode></TableCell>
                <TableCell><Badge variant="default">Agent</Badge></TableCell>
                <TableCell>Single workflow run</TableCell>
              </TableRow>
              <TableRow>
                <TableCell><InlineCode>python main.py run --once --dry-run</InlineCode></TableCell>
                <TableCell><Badge>Test</Badge></TableCell>
                <TableCell>Test without posting</TableCell>
              </TableRow>
              <TableRow>
                <TableCell><InlineCode>python main.py publish --limit 3</InlineCode></TableCell>
                <TableCell><Badge variant="default">Agent</Badge></TableCell>
                <TableCell>Manual publish approved drafts</TableCell>
              </TableRow>
              <TableRow>
                <TableCell><InlineCode>python main.py check-engagement --limit 50</InlineCode></TableCell>
                <TableCell><Badge variant="outline">Utility</Badge></TableCell>
                <TableCell>Check 24h engagement metrics</TableCell>
              </TableRow>
              <TableRow>
                <TableCell><InlineCode>python main.py health</InlineCode></TableCell>
                <TableCell><Badge variant="outline">Utility</Badge></TableCell>
                <TableCell>Show health status</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </Section>

      <Section>
        <SectionHeader>Local Development Setup</SectionHeader>
        <p className="text-muted-foreground mb-4">For local testing with ngrok:</p>
        <CodeBlock language="bash">{`# Terminal 1: Start ngrok
ngrok http 8000
# Copy the forwarding URL (e.g., https://abc123.ngrok.io)

# Terminal 2: Update .env
echo "PUBLIC_URL=https://abc123.ngrok.io" >> .env

# Terminal 3: Start callback server
source venv/bin/activate
python main.py server

# Terminal 4: Run agent
source venv/bin/activate
python main.py run --once`}</CodeBlock>

        <Callout variant="warning">
          <strong>Note</strong>: ngrok URLs change every time you restart unless you have a paid plan. Remember to update <InlineCode>PUBLIC_URL</InlineCode> in <InlineCode>.env</InlineCode> after each restart.
        </Callout>
      </Section>

      <Section>
        <SectionHeader>Troubleshooting</SectionHeader>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">&quot;No candidates found&quot;</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-muted-foreground"><strong className="text-foreground">Cause</strong>: No new content in allowed subreddits, or all candidates in cooldown.</p>
              <p className="text-muted-foreground"><strong className="text-foreground">Solution</strong>:</p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Check <InlineCode>ALLOWED_SUBREDDITS</InlineCode> is configured</li>
                <li>Wait for cooldown periods (6h inbox, 24h rising)</li>
                <li>Check <InlineCode>replied_items</InlineCode> table for cooldown status</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">&quot;Shadowban risk detected&quot;</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-muted-foreground"><strong className="text-foreground">Cause</strong>: Agent detected unusual downvote patterns.</p>
              <p className="text-muted-foreground"><strong className="text-foreground">Solution</strong>:</p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Review recent comments for quality</li>
                <li>Check subreddit rules compliance</li>
                <li>Wait 24-48 hours before resuming</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">&quot;LLM API error&quot;</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-muted-foreground"><strong className="text-foreground">Cause</strong>: Invalid API key or rate limit hit.</p>
              <p className="text-muted-foreground"><strong className="text-foreground">Solution</strong>:</p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Verify API key in <InlineCode>.env</InlineCode></li>
                <li>Check API quota/billing</li>
                <li>Try alternative LLM provider</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">&quot;Approval link not working&quot;</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p className="text-muted-foreground"><strong className="text-foreground">Cause</strong>: <InlineCode>PUBLIC_URL</InlineCode> not accessible or incorrect.</p>
              <p className="text-muted-foreground"><strong className="text-foreground">Solution</strong>:</p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Verify callback server is running</li>
                <li>Check ngrok tunnel is active</li>
                <li>Test <InlineCode>PUBLIC_URL/health</InlineCode> in browser</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </Section>

      <Section id="best-practices">
        <SectionHeader>Best Practices</SectionHeader>

        <Tabs defaultValue="schedule" className="w-full">
          <TabsList className="flex-wrap h-auto">
            <TabsTrigger value="schedule">Run Schedule</TabsTrigger>
            <TabsTrigger value="subreddits">Subreddit Selection</TabsTrigger>
            <TabsTrigger value="persona">Persona Selection</TabsTrigger>
            <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
          </TabsList>

          <TabsContent value="schedule" className="mt-4 space-y-4">
            <div>
              <p className="text-muted-foreground mb-2"><strong className="text-foreground">Local development:</strong></p>
              <CodeBlock language="bash">{`# Run manually when you're available to approve
python main.py run --once`}</CodeBlock>
            </div>

            <div>
              <p className="text-muted-foreground mb-2"><strong className="text-foreground">Production</strong> (GitHub Actions):</p>
              <CodeBlock language="yaml">{`schedule:
  - cron: '0 */4 * * *'  # Every 4 hours`}</CodeBlock>
            </div>

            <p className="text-muted-foreground"><strong className="text-foreground">Why not more frequent?</strong></p>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground">
              <li>Cooldown periods (6h/24h) mean less frequent runs are sufficient</li>
              <li>Avoid spam patterns</li>
              <li>Give time for quality engagement metrics</li>
            </ul>
          </TabsContent>

          <TabsContent value="subreddits" className="mt-4 space-y-4">
            <div>
              <p className="text-muted-foreground mb-2"><strong className="text-foreground">✅ Good subreddits:</strong></p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Where you&apos;re already active (100+ karma)</li>
                <li>Moderate size (10k-500k members)</li>
                <li>Technical/niche topics</li>
                <li>Friendly to helpful comments</li>
              </ul>
            </div>

            <div>
              <p className="text-muted-foreground mb-2"><strong className="text-foreground">❌ Avoid:</strong></p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Default subreddits (r/funny, r/pics)</li>
                <li>Highly moderated (strict rules)</li>
                <li>Where you&apos;re not a genuine member</li>
                <li>Controversial topics</li>
              </ul>
            </div>
          </TabsContent>

          <TabsContent value="persona" className="mt-4">
            <p className="text-muted-foreground mb-4">Match persona to subreddit culture:</p>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Subreddit Type</TableHead>
                    <TableHead>Best Persona</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow><TableCell>Technical (r/sysadmin)</TableCell><TableCell><Badge variant="secondary">Experienced</Badge> <Badge variant="outline">Analytical</Badge></TableCell></TableRow>
                  <TableRow><TableCell>Learning (r/learnpython)</TableCell><TableCell><Badge variant="secondary">Helpful</Badge> <Badge variant="outline">Patient</Badge></TableCell></TableRow>
                  <TableRow><TableCell>Discussion (r/startups)</TableCell><TableCell><Badge variant="secondary">Curious</Badge> <Badge variant="outline">Skeptical</Badge></TableCell></TableRow>
                  <TableRow><TableCell>Troubleshooting</TableCell><TableCell><Badge variant="secondary">Experienced</Badge> <Badge variant="outline">Helpful</Badge></TableCell></TableRow>
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          <TabsContent value="monitoring" className="mt-4 space-y-4">
            <div>
              <p className="text-muted-foreground mb-2"><strong className="text-foreground">Weekly checklist:</strong></p>
              <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                <li>Check recent comment scores: <InlineCode>python main.py check-engagement</InlineCode></li>
                <li>Review shadowban risk: Check <InlineCode>performance_history</InlineCode> downvotes</li>
                <li>Audit approved comments: Were they high quality?</li>
                <li>Adjust configuration if needed</li>
              </ol>
            </div>

            <div>
              <p className="text-muted-foreground mb-2"><strong className="text-foreground">Red flags:</strong></p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                <li>Consistent downvotes (-5 or worse)</li>
                <li>Mod removals</li>
                <li>Ban messages</li>
                <li>Unusual response patterns</li>
              </ul>
            </div>
          </TabsContent>
        </Tabs>
      </Section>

      <Section>
        <SectionHeader>Next Steps</SectionHeader>
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                <Link href="/architecture" className="text-primary hover:underline">Architecture Overview</Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Understand the 13-node workflow</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                <Link href="/configuration" className="text-primary hover:underline">Configuration Guide</Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Advanced configuration options</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                <Link href="/features" className="text-primary hover:underline">Features</Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Explore quality scoring and diversity</p>
            </CardContent>
          </Card>
        </div>

        <hr className="my-8" />

        <Callout variant="info">
          <strong>Need help?</strong> Check the <Link href="/faq" className="text-primary hover:underline">FAQ</Link> or review the troubleshooting section above.
        </Callout>
      </Section>
    </PageWrapper>
  )
}
