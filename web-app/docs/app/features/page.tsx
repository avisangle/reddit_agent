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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import Link from "next/link"
import { Shield, Zap, Target, Brain, AlertTriangle, Clock, CheckCircle2 } from "lucide-react"

export default function FeaturesPage() {
  return (
    <PageWrapper className="py-8 px-4">
      <PageHeader
        title="Features"
        description="The Reddit Agent includes advanced features designed for quality, safety, and compliance."
      />

      <Section>
        <SectionHeader>Quality Scoring System</SectionHeader>

        <SubSection>
          <SubSectionHeader>7-Factor AI Scoring</SubSectionHeader>
          <p className="text-muted-foreground mb-6">Every candidate is scored from 0.0 to 1.0 using seven weighted factors:</p>

          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-medium">Upvote Ratio</span>
                <Badge variant="secondary">25%</Badge>
              </div>
              <Progress value={25} className="h-2" />
              <p className="text-sm text-muted-foreground">Post/comment engagement quality</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-medium">Freshness</span>
                <Badge variant="secondary">20%</Badge>
              </div>
              <Progress value={20} className="h-2" />
              <p className="text-sm text-muted-foreground">How recent the content is (exponential decay)</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-medium">Author Karma</span>
                <Badge variant="secondary">15%</Badge>
              </div>
              <Progress value={15} className="h-2" />
              <p className="text-sm text-muted-foreground">Credibility of author (<InlineCode>log(karma) / 15</InlineCode>)</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-medium">Historical Performance</span>
                <Badge variant="secondary">15%</Badge>
              </div>
              <Progress value={15} className="h-2" />
              <p className="text-sm text-muted-foreground">Past success rate in this subreddit</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-medium">Velocity</span>
                <Badge variant="secondary">10%</Badge>
              </div>
              <Progress value={10} className="h-2" />
              <p className="text-sm text-muted-foreground">Comment growth rate</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-medium">Question Signal</span>
                <Badge variant="secondary">10%</Badge>
              </div>
              <Progress value={10} className="h-2" />
              <p className="text-sm text-muted-foreground">Presence of questions in title/body</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-medium">Thread Depth</span>
                <Badge variant="secondary">5%</Badge>
              </div>
              <Progress value={5} className="h-2" />
              <p className="text-sm text-muted-foreground">Shallow threads score higher</p>
            </div>
          </div>
        </SubSection>

        <SubSection>
          <SubSectionHeader>Example Calculation</SubSectionHeader>
          <CodeBlock language="python">{`# High-quality candidate
upvote_ratio = 0.95      # 95% upvoted → 0.95 * 0.25 = 0.238
karma_score = 0.80       # 5k karma → 0.80 * 0.15 = 0.120
freshness = 0.90         # 2 hours old → 0.90 * 0.20 = 0.180
velocity = 0.70          # 50 comments/10h → 0.70 * 0.10 = 0.070
question = 1.00          # Has "?" → 1.00 * 0.10 = 0.100
depth = 0.80             # 2 levels deep → 0.80 * 0.05 = 0.040
historical = 0.85        # Good history → 0.85 * 0.15 = 0.128

total_score = 0.876  # ✅ High quality candidate`}</CodeBlock>
        </SubSection>

        <SubSection>
          <SubSectionHeader>Historical Learning</SubSectionHeader>
          <p className="text-muted-foreground">The agent learns from past performance:</p>
          <CodeBlock language="python">{`# Weighted average of past outcomes in each subreddit
engagement_score = (upvotes * 0.7) + (replies * 0.3)
decay_factor = exp(-days_since / 30)  # Recent results matter more

historical_score = avg(engagement_scores * decay_factors)`}</CodeBlock>
          <Callout variant="success">
            <p><strong>Result</strong>: The agent gets better over time, learning which types of content work best in each subreddit.</p>
          </Callout>
        </SubSection>
      </Section>

      <Section>
        <SectionHeader>Inbox Priority System</SectionHeader>

        <div className="grid gap-4 md:grid-cols-2 mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-primary" />
                HIGH Priority
              </CardTitle>
              <CardDescription>Inbox replies</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">Direct replies are processed first:</p>
              <ul className="text-sm space-y-1">
                <li className="flex items-center gap-2"><Badge variant="default">HIGH</Badge> Reply to your comment</li>
                <li className="flex items-center gap-2"><Badge variant="default">HIGH</Badge> Reply to your post</li>
                <li className="flex items-center gap-2"><Badge variant="default">HIGH</Badge> Mention in thread</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-muted-foreground" />
                NORMAL Priority
              </CardTitle>
              <CardDescription>Rising content</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">Proactive engagement opportunities:</p>
              <ul className="text-sm space-y-1">
                <li className="flex items-center gap-2"><Badge variant="secondary">NORMAL</Badge> Rising post</li>
                <li className="flex items-center gap-2"><Badge variant="secondary">NORMAL</Badge> Rising comment</li>
              </ul>
            </CardContent>
          </Card>
        </div>

        <SubSection>
          <SubSectionHeader>Separate Cooldowns</SubSectionHeader>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Candidate Type</TableHead>
                  <TableHead>Cooldown</TableHead>
                  <TableHead>Rationale</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell><Badge variant="default">HIGH</Badge> Inbox</TableCell>
                  <TableCell>6 hours</TableCell>
                  <TableCell>More forgiving - you&apos;re responding to engagement</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell><Badge variant="secondary">NORMAL</Badge> Rising</TableCell>
                  <TableCell>24 hours</TableCell>
                  <TableCell>Conservative - proactive commenting</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>
        </SubSection>
      </Section>

      <Section>
        <SectionHeader>Subreddit Diversity</SectionHeader>

        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Max Per Subreddit</CardTitle>
              <CardDescription>Prevents clustering in a single subreddit</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <CodeBlock language="bash">{`MAX_PER_SUBREDDIT=2
DIVERSITY_QUALITY_BOOST_THRESHOLD=0.75`}</CodeBlock>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Up to 2 comments per subreddit per run</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Quality override: Score ≥0.75 can bypass limit</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Max Per Post</CardTitle>
              <CardDescription>Strict limit to avoid spam patterns</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <CodeBlock language="bash">{`MAX_PER_POST=1  # No override allowed`}</CodeBlock>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Only 1 comment per post, ever</span>
                </div>
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm">No quality override - strict limit</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </Section>

      <Section>
        <SectionHeader>Exploration Rate</SectionHeader>
        <p className="text-muted-foreground mb-4">25% of selections are randomized to prevent bot detection:</p>
        <CodeBlock language="python">{`# Configuration
SCORE_EXPLORATION_RATE=0.25
SCORE_TOP_N_RANDOM=5

# Algorithm
top_candidates = sorted_candidates[:5]  # Top 5 by score
if random() < 0.25:  # 25% chance
    selected = random.choice(top_candidates)
else:
    selected = top_candidates[0]  # Highest score`}</CodeBlock>
        <Callout variant="info">
          <strong>Why?</strong> Always selecting the highest-scoring candidate creates predictable timing patterns that Reddit&apos;s anti-bot systems can detect.
        </Callout>
      </Section>

      <Section>
        <SectionHeader>Safety Features</SectionHeader>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-red-500" />
                Shadowban Detection
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">Circuit breaker halts if risk threshold exceeded:</p>
              <CodeBlock language="python">{`SHADOWBAN_RISK_THRESHOLD=0.7`}</CodeBlock>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-blue-500" />
                Anti-Fingerprinting
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">Random jitter adds unpredictability:</p>
              <CodeBlock language="python">{`jitter = random.uniform(5, 15)  # 5-15s`}</CodeBlock>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-purple-500" />
                Auto-Publish
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Click &quot;Approve&quot; → Draft publishes automatically → Engagement tracked after 24h</p>
            </CardContent>
          </Card>
        </div>
      </Section>

      <Section>
        <SectionHeader>Engagement Tracking</SectionHeader>

        <p className="text-muted-foreground mb-4">After publishing, the agent fetches engagement data:</p>
        <CodeBlock language="bash">{`python main.py check-engagement --limit 50`}</CodeBlock>

        <div className="grid gap-4 md:grid-cols-2 mt-6">
          <div>
            <p className="font-medium mb-2">Tracked Metrics</p>
            <ul className="space-y-2">
              <li className="flex items-center gap-2"><Badge variant="outline">Upvotes</Badge></li>
              <li className="flex items-center gap-2"><Badge variant="outline">Downvotes</Badge></li>
              <li className="flex items-center gap-2"><Badge variant="outline">Replies</Badge></li>
              <li className="flex items-center gap-2"><Badge variant="outline">Awards</Badge></li>
              <li className="flex items-center gap-2"><Badge variant="outline">Removal Status</Badge></li>
            </ul>
          </div>
          <div>
            <p className="font-medium mb-2">Learning Loop</p>
            <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
              <li>Publish comment with <InlineCode>quality_score=0.85</InlineCode></li>
              <li>Wait 24 hours</li>
              <li>Fetch metrics: <InlineCode>upvotes=15, replies=3</InlineCode></li>
              <li>Calculate engagement score</li>
              <li>Store in <InlineCode>performance_history</InlineCode></li>
              <li>Next run: Historical factor increases</li>
            </ol>
          </div>
        </div>
      </Section>

      <Section>
        <SectionHeader>Safety Constraints</SectionHeader>
        <p className="text-muted-foreground mb-6">All features respect these hard limits:</p>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Constraint</TableHead>
                <TableHead>Value</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Enforcement</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell>Max comments/day</TableCell>
                <TableCell><strong>8</strong></TableCell>
                <TableCell><Badge variant="destructive">Hardcoded</Badge></TableCell>
                <TableCell><InlineCode>daily_stats</InlineCode> table</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Max comments/run</TableCell>
                <TableCell><strong>3</strong></TableCell>
                <TableCell><Badge variant="destructive">Hardcoded</Badge></TableCell>
                <TableCell>Workflow runner</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>HITL required</TableCell>
                <TableCell><strong>Always</strong></TableCell>
                <TableCell><Badge variant="destructive">Hardcoded</Badge></TableCell>
                <TableCell>No bypass</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Subreddit allow-list</TableCell>
                <TableCell><strong>Strict</strong></TableCell>
                <TableCell><Badge variant="default">Configurable</Badge></TableCell>
                <TableCell>Config only</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Bot filtering</TableCell>
                <TableCell><strong>Enabled</strong></TableCell>
                <TableCell><Badge variant="destructive">Hardcoded</Badge></TableCell>
                <TableCell>Cannot disable</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>Token expiry</TableCell>
                <TableCell><strong>48h</strong></TableCell>
                <TableCell><Badge variant="destructive">Hardcoded</Badge></TableCell>
                <TableCell>Enforced</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>

        <Callout variant="error">
          <p><strong>Non-negotiable</strong>: These safety constraints are hardcoded and cannot be disabled. They ensure Reddit ToS compliance and prevent shadowbans.</p>
        </Callout>
      </Section>

      <Section>
        <SectionHeader>Feature Configuration</SectionHeader>
        <p className="text-muted-foreground mb-4">
          All features can be configured via environment variables. Key toggles include:
        </p>
        <ul className="list-disc list-inside space-y-1 text-muted-foreground mb-4">
          <li><InlineCode>INBOX_PRIORITY_ENABLED</InlineCode> - Enable inbox priority system</li>
          <li><InlineCode>DIVERSITY_ENABLED</InlineCode> - Enable subreddit diversity limits</li>
          <li><InlineCode>AUTO_PUBLISH_ENABLED</InlineCode> - Auto-publish approved drafts</li>
        </ul>
        <p className="text-muted-foreground">
          See <Link href="/configuration#feature-toggles" className="text-primary hover:underline">Configuration Reference</Link> for all options and defaults.
        </p>
      </Section>

      <Section>
        <SectionHeader>Next Steps</SectionHeader>
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                <Link href="/configuration" className="text-primary hover:underline">Configuration</Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Detailed <InlineCode>.env</InlineCode> reference</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                <Link href="/architecture" className="text-primary hover:underline">Architecture</Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Understand the 13-node workflow</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                <Link href="/faq" className="text-primary hover:underline">FAQ</Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Common questions and troubleshooting</p>
            </CardContent>
          </Card>
        </div>

        <Separator className="my-8" />

        <Callout variant="info">
          <p><strong>Feature Philosophy</strong>: Every feature is designed with safety and compliance as the top priority. Quality and engagement are secondary to avoiding shadowbans and respecting Reddit&apos;s community guidelines.</p>
        </Callout>
      </Section>
    </PageWrapper>
  )
}
