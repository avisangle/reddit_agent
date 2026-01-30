"use client"

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
import { Separator } from "@/components/ui/separator"
import Link from "next/link"
import { Settings, Key, Bell, Globe, Shield, Database } from "lucide-react"

export default function ConfigurationPage() {
  return (
    <PageWrapper className="py-8 px-4">
      <PageHeader
        title="Configuration Reference"
        description={<>Complete reference for all <InlineCode>.env</InlineCode> configuration options.</>}
      />

      <Section>
        <SectionHeader>Environment Variables</SectionHeader>

        <Tabs defaultValue="reddit" className="w-full">
          <TabsList className="flex-wrap h-auto gap-1">
            <TabsTrigger value="reddit" className="gap-1.5">
              <Settings className="h-4 w-4" />
              Reddit API
            </TabsTrigger>
            <TabsTrigger value="llm" className="gap-1.5">
              <Key className="h-4 w-4" />
              LLM Keys
            </TabsTrigger>
            <TabsTrigger value="notifications" className="gap-1.5">
              <Bell className="h-4 w-4" />
              Notifications
            </TabsTrigger>
            <TabsTrigger value="url" className="gap-1.5">
              <Globe className="h-4 w-4" />
              Public URL
            </TabsTrigger>
          </TabsList>

          <TabsContent value="reddit" className="mt-6 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Reddit API Credentials
                  <Badge variant="destructive">Required</Badge>
                </CardTitle>
                <CardDescription>OAuth application and account credentials</CardDescription>
              </CardHeader>
              <CardContent>
                <CodeBlock language="bash">{`# OAuth Application Credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here

# Account Credentials
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# User Agent Format
REDDIT_USER_AGENT=android:com.yourapp.agent:v2.5 (by /u/YourUsername)`}</CodeBlock>
                <Callout variant="info">
                  <strong>Creating Reddit App</strong>: Visit{" "}
                  <a href="https://www.reddit.com/prefs/apps" className="text-primary hover:underline">reddit.com/prefs/apps</a> → &quot;Create App&quot; → Select &quot;script&quot; → Copy client ID and secret.
                </Callout>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Subreddit Configuration
                  <Badge variant="destructive">Required</Badge>
                </CardTitle>
                <CardDescription>Allow-list of subreddits the agent can operate in</CardDescription>
              </CardHeader>
              <CardContent>
                <CodeBlock language="bash">{`# Comma-separated list (no spaces)
ALLOWED_SUBREDDITS=sysadmin,learnpython,startups,devops`}</CodeBlock>
                <Callout variant="warning">
                  <strong>Important</strong>: Only add subreddits where you&apos;re an active, legitimate member. The agent will ONLY operate in these subreddits.
                </Callout>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="llm" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  LLM API Keys
                  <Badge variant="destructive">At least one required</Badge>
                </CardTitle>
                <CardDescription>API keys for AI providers</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <CodeBlock language="bash">{`# Recommended: Gemini 2.5 Flash (fastest, cheapest)
GEMINI_API_KEY=your_gemini_api_key

# Alternatives
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key`}</CodeBlock>

                <div>
                  <p className="font-medium mb-2">Model Selection Priority:</p>
                  <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
                    <li><Badge variant="default">1st</Badge> Gemini 2.5 Flash (if <InlineCode>GEMINI_API_KEY</InlineCode> set)</li>
                    <li><Badge variant="secondary">2nd</Badge> GPT-4 Turbo (if <InlineCode>OPENAI_API_KEY</InlineCode> set)</li>
                    <li><Badge variant="outline">3rd</Badge> Claude 3.5 Sonnet (if <InlineCode>ANTHROPIC_API_KEY</InlineCode> set)</li>
                  </ol>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notifications" className="mt-6 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Slack
                  <Badge variant="secondary">Option A</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CodeBlock language="bash">{`NOTIFICATION_TYPE=slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL`}</CodeBlock>
                <p className="text-sm text-muted-foreground mt-2">
                  Setup: <a href="https://api.slack.com/messaging/webhooks" className="text-primary hover:underline">api.slack.com/messaging/webhooks</a>
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Telegram
                  <Badge variant="secondary">Option B</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CodeBlock language="bash">{`NOTIFICATION_TYPE=telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=your_chat_id`}</CodeBlock>
                <p className="text-sm text-muted-foreground mt-2">
                  Setup: Create bot via <a href="https://t.me/botfather" className="text-primary hover:underline">@BotFather</a>
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Custom Webhook
                  <Badge variant="secondary">Option C</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CodeBlock language="bash">{`NOTIFICATION_TYPE=webhook
WEBHOOK_URL=https://your-webhook-url.com/endpoint`}</CodeBlock>
                <p className="text-sm text-muted-foreground mt-2">Webhook Payload:</p>
                <CodeBlock language="json">{`{
  "draft_id": 123,
  "subreddit": "sysadmin",
  "target_id": "t1_abc123",
  "draft_text": "Your comment text...",
  "quality_score": 0.85,
  "priority": "HIGH",
  "approve_url": "https://your-domain.com/approve?token=...",
  "reject_url": "https://your-domain.com/reject?token=..."
}`}</CodeBlock>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="url" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  Public URL
                  <Badge variant="destructive">Required</Badge>
                </CardTitle>
                <CardDescription>URL for approval button callbacks</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Local development (ngrok):</p>
                    <CodeBlock language="bash">{`PUBLIC_URL=https://abc123.ngrok.io`}</CodeBlock>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Production (Railway, Fly.io, etc.):</p>
                    <CodeBlock language="bash">{`PUBLIC_URL=https://your-app.railway.app`}</CodeBlock>
                  </div>
                </div>
                <Callout variant="warning">
                  <strong>Critical</strong>: Approval buttons won&apos;t work without a publicly accessible URL. For local dev, use ngrok.
                </Callout>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </Section>

      <Section>
        <SectionHeader>Safety Limits</SectionHeader>
        <p className="text-muted-foreground mb-4">
          These values are <Badge variant="destructive">Hardcoded</Badge> in <InlineCode>config.py</InlineCode> and cannot be changed via <InlineCode>.env</InlineCode>:
        </p>
        <CodeBlock language="python">{`# config.py
class Settings(BaseSettings):
    max_comments_per_day: int = 8       # Daily limit
    max_comments_per_run: int = 3       # Per-run limit
    post_reply_ratio: float = 0.3       # 30% posts, 70% comments
    shadowban_risk_threshold: float = 0.7
    token_ttl_hours: int = 48`}</CodeBlock>
        <Callout variant="info">
          <strong>Why hardcoded?</strong> To prevent accidental misconfiguration that could trigger shadowbans.
        </Callout>
      </Section>

      <Section>
        <SectionHeader>Feature Toggles</SectionHeader>

        <Tabs defaultValue="inbox" className="w-full">
          <TabsList className="flex-wrap h-auto">
            <TabsTrigger value="inbox">Inbox Priority</TabsTrigger>
            <TabsTrigger value="diversity">Diversity</TabsTrigger>
            <TabsTrigger value="exploration">Exploration</TabsTrigger>
            <TabsTrigger value="autopublish">Auto-Publish</TabsTrigger>
          </TabsList>

          <TabsContent value="inbox" className="mt-6">
            <CodeBlock language="bash">{`INBOX_PRIORITY_ENABLED=True
INBOX_COOLDOWN_HOURS=6
RISING_COOLDOWN_HOURS=24`}</CodeBlock>

            <div className="overflow-x-auto mt-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Variable</TableHead>
                    <TableHead>Default</TableHead>
                    <TableHead>Range</TableHead>
                    <TableHead>Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell><InlineCode>INBOX_PRIORITY_ENABLED</InlineCode></TableCell>
                    <TableCell><Badge>True</Badge></TableCell>
                    <TableCell>bool</TableCell>
                    <TableCell>Enable inbox priority tagging</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><InlineCode>INBOX_COOLDOWN_HOURS</InlineCode></TableCell>
                    <TableCell><Badge variant="secondary">6</Badge></TableCell>
                    <TableCell>1-24</TableCell>
                    <TableCell>Cooldown for inbox replies</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><InlineCode>RISING_COOLDOWN_HOURS</InlineCode></TableCell>
                    <TableCell><Badge variant="secondary">24</Badge></TableCell>
                    <TableCell>12-48</TableCell>
                    <TableCell>Cooldown for rising content</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          <TabsContent value="diversity" className="mt-6">
            <CodeBlock language="bash">{`DIVERSITY_ENABLED=True
MAX_PER_SUBREDDIT=2
MAX_PER_POST=1
DIVERSITY_QUALITY_BOOST_THRESHOLD=0.75`}</CodeBlock>

            <div className="overflow-x-auto mt-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Variable</TableHead>
                    <TableHead>Default</TableHead>
                    <TableHead>Range</TableHead>
                    <TableHead>Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell><InlineCode>DIVERSITY_ENABLED</InlineCode></TableCell>
                    <TableCell><Badge>True</Badge></TableCell>
                    <TableCell>bool</TableCell>
                    <TableCell>Enable diversity filtering</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><InlineCode>MAX_PER_SUBREDDIT</InlineCode></TableCell>
                    <TableCell><Badge variant="secondary">2</Badge></TableCell>
                    <TableCell>1-3</TableCell>
                    <TableCell>Max comments per subreddit per run</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><InlineCode>MAX_PER_POST</InlineCode></TableCell>
                    <TableCell><Badge variant="destructive">1</Badge></TableCell>
                    <TableCell>1</TableCell>
                    <TableCell>Max comments per post (strict)</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><InlineCode>DIVERSITY_QUALITY_BOOST_THRESHOLD</InlineCode></TableCell>
                    <TableCell><Badge variant="secondary">0.75</Badge></TableCell>
                    <TableCell>0.0-1.0</TableCell>
                    <TableCell>Quality score bypass threshold</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          <TabsContent value="exploration" className="mt-6">
            <CodeBlock language="bash">{`SCORE_EXPLORATION_RATE=0.25
SCORE_TOP_N_RANDOM=5`}</CodeBlock>

            <div className="overflow-x-auto mt-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Variable</TableHead>
                    <TableHead>Default</TableHead>
                    <TableHead>Range</TableHead>
                    <TableHead>Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell><InlineCode>SCORE_EXPLORATION_RATE</InlineCode></TableCell>
                    <TableCell><Badge variant="secondary">0.25</Badge></TableCell>
                    <TableCell>0.0-0.5</TableCell>
                    <TableCell>Probability of random selection</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><InlineCode>SCORE_TOP_N_RANDOM</InlineCode></TableCell>
                    <TableCell><Badge variant="secondary">5</Badge></TableCell>
                    <TableCell>3-10</TableCell>
                    <TableCell>Pool size for exploration</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </TabsContent>

          <TabsContent value="autopublish" className="mt-6">
            <CodeBlock language="bash">{`AUTO_PUBLISH_ENABLED=True`}</CodeBlock>

            <div className="overflow-x-auto mt-4">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Variable</TableHead>
                    <TableHead>Default</TableHead>
                    <TableHead>Description</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell><InlineCode>AUTO_PUBLISH_ENABLED</InlineCode></TableCell>
                    <TableCell><Badge>True</Badge></TableCell>
                    <TableCell>Auto-publish approved drafts</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>

            <Callout variant="info">
              <strong>If disabled</strong>: Use <InlineCode>python main.py publish --limit 3</InlineCode> to manually publish.
            </Callout>
          </TabsContent>
        </Tabs>
      </Section>

      <Section>
        <SectionHeader>Advanced Configuration</SectionHeader>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Database
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CodeBlock language="bash">{`DATABASE_URL=sqlite:///reddit_agent.db
# Alternative: PostgreSQL
# DATABASE_URL=postgresql://user:pass@host:5432/dbname`}</CodeBlock>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Logging
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CodeBlock language="bash">{`LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json  # json or text`}</CodeBlock>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Persona Selection</CardTitle>
            </CardHeader>
            <CardContent>
              <CodeBlock language="bash">{`DEFAULT_PERSONA=helpful
# Available: helpful, skeptical, curious,
#            experienced, analytical`}</CodeBlock>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Context Loading</CardTitle>
            </CardHeader>
            <CardContent>
              <CodeBlock language="bash">{`MAX_PARENT_COMMENTS=3
MAX_COMMENT_LENGTH=500
MAX_SUBMISSION_LENGTH=1000`}</CodeBlock>
            </CardContent>
          </Card>
        </div>
      </Section>

      <Section>
        <SectionHeader>Configuration Validation</SectionHeader>
        <p className="text-muted-foreground mb-4">The agent validates all configuration on startup:</p>
        <CodeBlock language="text">{`✓ Reddit credentials valid
✓ At least one LLM key present
✓ Notification type configured
✓ Public URL accessible
✓ Allowed subreddits non-empty
✓ Safety limits within bounds`}</CodeBlock>

        <Separator className="my-6" />

        <p className="font-medium mb-2">Startup failures:</p>
        <CodeBlock language="text">{`❌ GEMINI_API_KEY not set and no alternative LLM key found
❌ PUBLIC_URL not accessible (callback server unreachable)
❌ ALLOWED_SUBREDDITS is empty`}</CodeBlock>
      </Section>

      <Section>
        <SectionHeader>Example .env File</SectionHeader>
        <CodeBlock language="bash">{`# Reddit API
REDDIT_CLIENT_ID=abc123xyz
REDDIT_CLIENT_SECRET=xyz789abc
REDDIT_USERNAME=YourUsername
REDDIT_PASSWORD=YourPassword
REDDIT_USER_AGENT=android:com.yourapp.agent:v2.5 (by /u/YourUsername)

# Subreddits
ALLOWED_SUBREDDITS=sysadmin,learnpython,startups

# LLM
GEMINI_API_KEY=AIzaSy...

# Notifications
NOTIFICATION_TYPE=slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Callback
PUBLIC_URL=https://your-app.railway.app

# Feature Toggles
INBOX_PRIORITY_ENABLED=True
DIVERSITY_ENABLED=True
AUTO_PUBLISH_ENABLED=True

# Cooldowns
INBOX_COOLDOWN_HOURS=6
RISING_COOLDOWN_HOURS=24

# Diversity
MAX_PER_SUBREDDIT=2
MAX_PER_POST=1
DIVERSITY_QUALITY_BOOST_THRESHOLD=0.75

# Exploration
SCORE_EXPLORATION_RATE=0.25
SCORE_TOP_N_RANDOM=5

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json`}</CodeBlock>
      </Section>

      <Section>
        <SectionHeader>Security Best Practices</SectionHeader>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-red-500" />
                Protect .env
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CodeBlock language="bash">{`# .gitignore
.env
.env.local
.env.*.local`}</CodeBlock>
              <Callout variant="error">
                <strong>Never commit <InlineCode>.env</InlineCode> to Git!</strong>
              </Callout>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Rotate API Keys</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>Reddit password: <Badge variant="outline">90 days</Badge></li>
                <li>LLM API keys: <Badge variant="outline">6 months</Badge></li>
                <li>Webhook URLs: <Badge variant="outline">After incidents</Badge></li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Monitor API Usage</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li><a href="https://www.reddit.com/prefs/apps" className="text-primary hover:underline">Reddit API</a></li>
                <li><a href="https://console.cloud.google.com" className="text-primary hover:underline">Gemini API</a></li>
                <li><a href="https://platform.openai.com/usage" className="text-primary hover:underline">OpenAI API</a></li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </Section>

      <Section>
        <SectionHeader>Next Steps</SectionHeader>
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                <Link href="/features" className="text-primary hover:underline">Features</Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Enable/disable features</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                <Link href="/architecture" className="text-primary hover:underline">Architecture</Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">How config affects workflow</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                <Link href="/faq" className="text-primary hover:underline">FAQ</Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Configuration troubleshooting</p>
            </CardContent>
          </Card>
        </div>

        <Separator className="my-8" />

        <Callout variant="info">
          <strong>Configuration Philosophy</strong>: Sensible defaults with safety constraints hardcoded. Feature toggles available, but core safety limits are non-negotiable.
        </Callout>
      </Section>
    </PageWrapper>
  )
}
