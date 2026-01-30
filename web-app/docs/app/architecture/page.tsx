"use client"

import Link from "next/link"
import {
  Callout,
  CodeBlock,
  InlineCode,
  PageWrapper,
  PageHeader,
  Section,
  SectionHeader,
  SubSection,
  SubSectionHeader,
  DiagramContainer,
  DiagramNode,
  DiagramFlow,
  DiagramGroup,
  DiagramRow,
  DiagramConnector,
  DiagramServiceList
} from "@/components/docs"
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import {
  Shield,
  Users,
  Zap,
  Database,
  Bell,
  Code,
  Settings,
  Download,
  Filter,
  BarChart3,
  CheckCircle,
  FileText,
  Shuffle,
  Target,
  MessageSquare,
  Send,
  Server,
  Terminal,
  Cloud,
  Laptop,
  GitBranch
} from "lucide-react"

export default function ArchitecturePage() {
  return (
    <PageWrapper className="py-8 px-4">
      <PageHeader
        title="Architecture Overview"
        description="The Reddit Agent is built on a modular, workflow-driven architecture powered by LangGraph. This page explains the system design, workflow nodes, and key components."
      />

      <Section>
        <SectionHeader>System Overview</SectionHeader>

        <DiagramContainer title="LangGraph 13-Node Workflow">
          {/* First row: fetch → ratio → score → filter → rules → sort → diversity → limit */}
          <DiagramFlow className="justify-center mb-4">
            <DiagramNode icon={<Download className="h-4 w-4" />} size="sm">fetch</DiagramNode>
            <DiagramNode icon={<BarChart3 className="h-4 w-4" />} size="sm">ratio</DiagramNode>
            <DiagramNode icon={<Target className="h-4 w-4" />} size="sm" variant="primary">score</DiagramNode>
            <DiagramNode icon={<Filter className="h-4 w-4" />} size="sm">filter</DiagramNode>
            <DiagramNode icon={<CheckCircle className="h-4 w-4" />} size="sm">rules</DiagramNode>
            <DiagramNode icon={<Shuffle className="h-4 w-4" />} size="sm">sort</DiagramNode>
            <DiagramNode icon={<Users className="h-4 w-4" />} size="sm">diversity</DiagramNode>
            <DiagramNode icon={<Shield className="h-4 w-4" />} size="sm">limit</DiagramNode>
          </DiagramFlow>

          <DiagramConnector />

          {/* Second row: select → context → generate → notify */}
          <DiagramFlow className="justify-center mb-4">
            <DiagramNode icon={<Target className="h-4 w-4" />} size="sm">select</DiagramNode>
            <DiagramNode icon={<FileText className="h-4 w-4" />} size="sm">context</DiagramNode>
            <DiagramNode icon={<MessageSquare className="h-4 w-4" />} size="sm" variant="primary">generate</DiagramNode>
            <DiagramNode icon={<Send className="h-4 w-4" />} size="sm">notify</DiagramNode>
          </DiagramFlow>

          <DiagramConnector label="inbox prioritized, quality-scored, diversity-filtered" />

          {/* Core Services */}
          <DiagramRow className="mt-4">
            <DiagramGroup title="Core Services" className="min-w-[200px]">
              <DiagramServiceList
                services={[
                  "RedditClient",
                  "ContextBuilder",
                  "RuleEngine",
                  "PromptManager",
                  "StateManager",
                  "Notifiers",
                  "Poster"
                ]}
              />
            </DiagramGroup>
          </DiagramRow>
        </DiagramContainer>
      </Section>

      <Section>
        <SectionHeader>Key Architectural Principles</SectionHeader>

        <SubSection>
          <SubSectionHeader>1. Compliance-First Design</SubSectionHeader>
          <p className="text-muted-foreground">Every component enforces safety constraints:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground mt-2">
            <li><strong className="text-foreground">Volume limits</strong>: Hardcoded ≤8 comments/day, ≤3 per run</li>
            <li><strong className="text-foreground">Cooldown periods</strong>: 6h for inbox, 24h for rising content</li>
            <li><strong className="text-foreground">Subreddit allow-lists</strong>: Only operates in configured subreddits</li>
            <li><strong className="text-foreground">Bot filtering</strong>: Skips AutoModerator and bot accounts</li>
            <li><strong className="text-foreground">Shadowban detection</strong>: Circuit breaker halts on high risk</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>2. Human-in-the-Loop (HITL)</SubSectionHeader>
          <p className="text-muted-foreground">All drafts require explicit human approval before posting:</p>
          <CodeBlock>{`Agent → Generate Draft → Notify via Slack/Telegram →
User Clicks Approve → Auto-Publish to Reddit`}</CodeBlock>
        </SubSection>

        <SubSection>
          <SubSectionHeader>3. Quality-Driven Selection</SubSectionHeader>
          <p className="text-muted-foreground">
            The scoring system uses 7 weighted factors including upvote ratio, author karma, freshness, velocity, question signals, thread depth, and historical performance. 
            See <Link href="/features#quality-scoring-system" className="text-primary hover:underline">Features - Quality Scoring</Link> for the complete breakdown and weights.
          </p>
        </SubSection>
      </Section>

      <Section>
        <SectionHeader>13-Node Workflow</SectionHeader>
        <p className="text-muted-foreground mb-6">The LangGraph workflow processes candidates through these nodes:</p>

        <SubSection>
          <SubSectionHeader>1. fetch_candidates</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: Fetch inbox replies (HIGH priority) and rising posts/comments.</p>
          <p className="text-muted-foreground"><strong className="text-foreground">Inputs</strong>: None</p>
          <p className="text-muted-foreground"><strong className="text-foreground">Outputs</strong>: <InlineCode>comment_candidates</InlineCode>, <InlineCode>post_candidates</InlineCode></p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Implementation</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Fetches inbox unread messages</li>
            <li>Fetches rising posts from allowed subreddits</li>
            <li>Fetches rising comments from allowed subreddits</li>
            <li>Tags inbox replies with <InlineCode>priority=HIGH</InlineCode></li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>2. select_by_ratio</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: Apply post/comment ratio distribution (30% posts, 70% comments).</p>
          <p className="text-muted-foreground"><strong className="text-foreground">Configuration</strong>: <InlineCode>POST_REPLY_RATIO=0.3</InlineCode></p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Logic</strong>:</p>
          <CodeBlock>{`total_count = max_comments_per_run  # 3
post_count = int(total_count * POST_REPLY_RATIO)  # 0.9 → 1
comment_count = total_count - post_count  # 2`}</CodeBlock>
        </SubSection>

        <SubSection>
          <SubSectionHeader>3. score_candidates</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: AI-powered 7-factor quality scoring.</p>
          <p className="text-muted-foreground"><strong className="text-foreground">Inputs</strong>: Candidates from ratio selection</p>
          <p className="text-muted-foreground"><strong className="text-foreground">Outputs</strong>: Candidates with <InlineCode>quality_score</InlineCode> (0.0-1.0)</p>
          <p className="text-muted-foreground mt-2">
            Scoring factors: upvote ratio, author karma, freshness, velocity, question signal, thread depth, and historical performance. 
            See <Link href="/features#quality-scoring-system" className="text-primary hover:underline">Quality Scoring</Link> for weights and calculation details.
          </p>
        </SubSection>

        <SubSection>
          <SubSectionHeader>4. filter_candidates</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: Remove already-replied items and those in cooldown.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Checks</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Not in <InlineCode>replied_items</InlineCode> table</li>
            <li>Cooldown expired (6h inbox, 24h rising)</li>
            <li>Not deleted/removed</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>5. check_rules</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: Verify subreddit compliance.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Checks</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Subreddit in <InlineCode>ALLOWED_SUBREDDITS</InlineCode></li>
            <li>Cached rules loaded from <InlineCode>subreddit_rules_cache</InlineCode></li>
            <li>Validates against common anti-bot rules</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>6. sort_by_score</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: Sort by (priority, quality_score) with 25% exploration.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Algorithm</strong>:</p>
          <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
            <li>Group candidates by priority (HIGH first)</li>
            <li>Within each priority, sort by <InlineCode>quality_score</InlineCode> descending</li>
            <li>Apply 25% exploration rate (randomize top 5)</li>
          </ol>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Why exploration?</strong> Avoid predictable patterns that trigger bot detection.</p>
        </SubSection>

        <SubSection>
          <SubSectionHeader>7. diversity_select</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: Apply diversity limits (max 2/subreddit, max 1/post).</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Configuration</strong>:</p>
          <CodeBlock>{`DIVERSITY_ENABLED=True
MAX_PER_SUBREDDIT=2
MAX_PER_POST=1
DIVERSITY_QUALITY_BOOST_THRESHOLD=0.75`}</CodeBlock>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Logic</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Track comments per subreddit in current selection</li>
            <li>Track comments per post</li>
            <li>Allow quality override (score ≥0.75 bypasses subreddit limit)</li>
            <li><strong className="text-foreground">Max 1 per post</strong> is strict (no override)</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>8. check_daily_limit</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: Enforce ≤8 comments/day limit.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Implementation</strong>:</p>
          <CodeBlock>{`today = datetime.utcnow().date()
today_count = session.query(DailyStats).filter(
    DailyStats.date == today
).first()

if today_count and today_count.count >= 8:
    return False  # Halt workflow`}</CodeBlock>
        </SubSection>

        <SubSection>
          <SubSectionHeader>9. select_candidate</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: Pick next candidate to process.</p>
          <p className="text-muted-foreground"><strong className="text-foreground">Logic</strong>: Pop first candidate from sorted, filtered list.</p>
        </SubSection>

        <SubSection>
          <SubSectionHeader>10. build_context</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: Load vertical context chain for LLM.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Strategy</strong>: Vertical-first context loading:</p>
          <CodeBlock>{`target_comment
└── parent_comment
    └── grandparent_comment
        └── submission (post)`}</CodeBlock>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Limits</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Max 3 parent comments</li>
            <li>Truncate each to 500 chars</li>
            <li>Include submission title/body</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>11. generate_draft</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: LLM generates reply draft.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Implementation</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Uses Gemini 2.5 Flash (default)</li>
            <li>Loads persona from <InlineCode>prompts/templates.yaml</InlineCode></li>
            <li>Applies PII scrubbing</li>
            <li>Injects few-shot examples</li>
            <li>Max output: 300 words</li>
          </ul>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Personas</strong>: Helpful, Skeptical, Curious, Experienced, Analytical</p>
        </SubSection>

        <SubSection>
          <SubSectionHeader>12. notify_human</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: Send draft to Slack/Telegram for approval.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Approval Link Format</strong>:</p>
          <CodeBlock>{`https://<PUBLIC_URL>/approve?token=<hashed-token>`}</CodeBlock>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Token Security</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>SHA-256 hashed (not stored in plaintext)</li>
            <li>48-hour TTL</li>
            <li>One-time use</li>
            <li>IP validation (optional)</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>13. Auto-Publish (Background Task)</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Purpose</strong>: Post approved drafts to Reddit.</p>
          <p className="text-muted-foreground"><strong className="text-foreground">Trigger</strong>: Draft status changes to <InlineCode>APPROVED</InlineCode></p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Implementation</strong>:</p>
          <CodeBlock>{`@app.post("/approve")
async def approve_draft(token: str, background_tasks: BackgroundTasks):
    # Verify token, update status to APPROVED
    background_tasks.add_task(publish_approved_drafts)`}</CodeBlock>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Behavior</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Polls database for <InlineCode>APPROVED</InlineCode> drafts</li>
            <li>Posts to Reddit using PRAW</li>
            <li>Updates status to <InlineCode>PUBLISHED</InlineCode></li>
            <li>Tracks engagement after 24h</li>
          </ul>
        </SubSection>
      </Section>

      <Section>
        <SectionHeader>Database Schema</SectionHeader>

        <SubSection>
          <SubSectionHeader>replied_items</SubSectionHeader>
          <p className="text-muted-foreground mb-4">Tracks processed Reddit items with cooldowns:</p>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Column</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Description</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow><TableCell><InlineCode>item_id</InlineCode></TableCell><TableCell>String</TableCell><TableCell>Reddit fullname (e.g., t1_abc123)</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>subreddit</InlineCode></TableCell><TableCell>String</TableCell><TableCell>Subreddit name</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>candidate_type</InlineCode></TableCell><TableCell>String</TableCell><TableCell>INBOX, RISING_POST, or RISING_COMMENT</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>replied_at</InlineCode></TableCell><TableCell>DateTime</TableCell><TableCell>When we replied/processed</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>cooldown_until</InlineCode></TableCell><TableCell>DateTime</TableCell><TableCell>When cooldown expires</TableCell></TableRow>
              </TableBody>
            </Table>
          </div>
        </SubSection>

        <SubSection>
          <SubSectionHeader>draft_queue</SubSectionHeader>
          <p className="text-muted-foreground mb-4">Stores comment drafts with approval status:</p>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Column</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Description</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow><TableCell><InlineCode>draft_id</InlineCode></TableCell><TableCell>Integer</TableCell><TableCell>Primary key</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>target_id</InlineCode></TableCell><TableCell>String</TableCell><TableCell>Reddit item to reply to</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>subreddit</InlineCode></TableCell><TableCell>String</TableCell><TableCell>Subreddit name</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>draft_text</InlineCode></TableCell><TableCell>Text</TableCell><TableCell>Generated comment text</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>context_url</InlineCode></TableCell><TableCell>String</TableCell><TableCell>Reddit permalink</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>status</InlineCode></TableCell><TableCell>String</TableCell><TableCell>PENDING, APPROVED, PUBLISHED, REJECTED</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>approval_token_hash</InlineCode></TableCell><TableCell>String</TableCell><TableCell>SHA-256 hashed token</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>token_expires_at</InlineCode></TableCell><TableCell>DateTime</TableCell><TableCell>Approval link expiry</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>quality_score</InlineCode></TableCell><TableCell>Float</TableCell><TableCell>AI quality score (0.0-1.0)</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>candidate_priority</InlineCode></TableCell><TableCell>String</TableCell><TableCell>HIGH (inbox) or NORMAL</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>created_at</InlineCode></TableCell><TableCell>DateTime</TableCell><TableCell>Draft generation time</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>approved_at</InlineCode></TableCell><TableCell>DateTime</TableCell><TableCell>When approved</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>published_at</InlineCode></TableCell><TableCell>DateTime</TableCell><TableCell>When posted to Reddit</TableCell></TableRow>
              </TableBody>
            </Table>
          </div>
        </SubSection>

        <SubSection>
          <SubSectionHeader>performance_history</SubSectionHeader>
          <p className="text-muted-foreground mb-4">Tracks draft outcomes for learning:</p>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Column</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Description</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow><TableCell><InlineCode>draft_id</InlineCode></TableCell><TableCell>Integer</TableCell><TableCell>Foreign key to draft_queue</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>subreddit</InlineCode></TableCell><TableCell>String</TableCell><TableCell>Subreddit name</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>quality_score</InlineCode></TableCell><TableCell>Float</TableCell><TableCell>Original quality score</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>upvotes</InlineCode></TableCell><TableCell>Integer</TableCell><TableCell>24h upvote count</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>replies</InlineCode></TableCell><TableCell>Integer</TableCell><TableCell>24h reply count</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>was_removed</InlineCode></TableCell><TableCell>Boolean</TableCell><TableCell>Mod/auto-removed</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>engagement_score</InlineCode></TableCell><TableCell>Float</TableCell><TableCell>Calculated engagement metric</TableCell></TableRow>
                <TableRow><TableCell><InlineCode>created_at</InlineCode></TableCell><TableCell>DateTime</TableCell><TableCell>Performance record time</TableCell></TableRow>
              </TableBody>
            </Table>
          </div>
        </SubSection>
      </Section>

      <Section>
        <SectionHeader>Core Services</SectionHeader>

        <SubSection>
          <SubSectionHeader>RedditClient</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Responsibility</strong>: Reddit API interactions with safety checks.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Features</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>PRAW wrapper with error handling</li>
            <li>Shadowban detection (downvote pattern analysis)</li>
            <li>Bot account filtering (AutoModerator, suffix checks)</li>
            <li>Rate limiting (respects Reddit API limits)</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>ContextBuilder</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Responsibility</strong>: Build context chain for LLM.</p>
          <p className="text-muted-foreground"><strong className="text-foreground">Strategy</strong>: Vertical-first loading (parent → grandparent → submission).</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Output Format</strong>:</p>
          <CodeBlock>{`{
  "submission": {
    "title": "...",
    "body": "...",
    "url": "..."
  },
  "parent_comments": [
    {"author": "user1", "body": "..."},
    {"author": "user2", "body": "..."}
  ],
  "target_comment": {
    "author": "user3",
    "body": "..."
  }
}`}</CodeBlock>
        </SubSection>

        <SubSection>
          <SubSectionHeader>RuleEngine</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Responsibility</strong>: Subreddit compliance checks.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Features</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Loads rules from Reddit API</li>
            <li>Caches in <InlineCode>subreddit_rules_cache</InlineCode> (7-day TTL)</li>
            <li>Validates against common anti-bot patterns</li>
            <li>Returns compliance score (0.0-1.0)</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>PromptManager</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Responsibility</strong>: LLM prompt construction with safety.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Features</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Loads templates from <InlineCode>prompts/templates.yaml</InlineCode></li>
            <li>PII scrubbing (emails, phone numbers, addresses)</li>
            <li>Persona selection</li>
            <li>Few-shot example injection</li>
            <li>Token counting (respects LLM context limits)</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>StateManager</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Responsibility</strong>: State tracking, tokens, idempotency.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Features</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Token generation with SHA-256 hashing</li>
            <li>Token expiry (48h TTL)</li>
            <li>Idempotency checks (prevent duplicate processing)</li>
            <li>Status transitions (PENDING → APPROVED → PUBLISHED)</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>Notifiers</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Responsibility</strong>: Send drafts for approval.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Implementations</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li><strong className="text-foreground">SlackNotifier</strong>: Incoming webhooks with buttons</li>
            <li><strong className="text-foreground">TelegramNotifier</strong>: Bot API with inline buttons</li>
            <li><strong className="text-foreground">WebhookNotifier</strong>: Generic HTTP POST</li>
          </ul>
          <p className="text-muted-foreground mt-4"><strong className="text-foreground">Message Format</strong>:</p>
          <CodeBlock>{`New draft for r/subreddit_name

Quality Score: 0.85
Priority: HIGH

Draft:
<comment text>

[Approve] [Reject] [View Context]`}</CodeBlock>
        </SubSection>

        <SubSection>
          <SubSectionHeader>Poster</SubSectionHeader>
          <p className="text-muted-foreground"><strong className="text-foreground">Responsibility</strong>: Publish approved drafts to Reddit.</p>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Features</strong>:</p>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>PRAW comment posting</li>
            <li>Error handling (deleted posts, locked threads)</li>
            <li>Anti-fingerprinting (random jitter between posts)</li>
            <li>Engagement tracking (fetch 24h metrics)</li>
          </ul>
        </SubSection>
      </Section>

      <Section>
        <SectionHeader>Security Considerations</SectionHeader>

        <SubSection>
          <SubSectionHeader>Token Security</SubSectionHeader>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li><strong className="text-foreground">Hashing</strong>: SHA-256 (tokens never stored in plaintext)</li>
            <li><strong className="text-foreground">Expiry</strong>: 48-hour TTL</li>
            <li><strong className="text-foreground">One-time use</strong>: Invalidated after approve/reject</li>
            <li><strong className="text-foreground">IP validation</strong>: Optional IP address check in JWT</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>Approval Link Example</SubSectionHeader>
          <CodeBlock>{`https://your-domain.com/approve?token=abc123def456`}</CodeBlock>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Token Structure</strong> (before hashing):</p>
          <CodeBlock>{`{draft_id}.{random_secret}.{timestamp}`}</CodeBlock>
          <p className="text-muted-foreground mt-2"><strong className="text-foreground">Stored in Database</strong>:</p>
          <CodeBlock>{`approval_token_hash = hashlib.sha256(token.encode()).hexdigest()`}</CodeBlock>
        </SubSection>

        <SubSection>
          <SubSectionHeader>Security Headers</SubSectionHeader>
          <p className="text-muted-foreground">FastAPI callback server includes:</p>
          <CodeBlock>{`Referrer-Policy: no-referrer
X-Content-Type-Options: nosniff
X-Frame-Options: DENY`}</CodeBlock>
        </SubSection>
      </Section>

      <Section>
        <SectionHeader>Performance Optimizations</SectionHeader>

        <SubSection>
          <SubSectionHeader>Caching</SubSectionHeader>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li><strong className="text-foreground">Subreddit rules</strong>: 7-day TTL in <InlineCode>subreddit_rules_cache</InlineCode></li>
            <li><strong className="text-foreground">Historical scores</strong>: Weighted decay (recent results matter more)</li>
            <li><strong className="text-foreground">Dashboard metrics</strong>: 30-second cache in <InlineCode>dashboard_service.py</InlineCode></li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>Database Indexes</SubSectionHeader>
          <CodeBlock>{`CREATE INDEX idx_drafts_status ON draft_queue(status);
CREATE INDEX idx_drafts_created_at ON draft_queue(created_at);
CREATE INDEX idx_replied_items_cooldown ON replied_items(cooldown_until);
CREATE INDEX idx_daily_stats_date ON daily_stats(date);`}</CodeBlock>
        </SubSection>

        <SubSection>
          <SubSectionHeader>Query Optimization</SubSectionHeader>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li>Batch queries where possible</li>
            <li>Limit Reddit API calls (respects 60 req/min)</li>
            <li>Use SQLAlchemy query filters early</li>
          </ul>
        </SubSection>
      </Section>

      <Section>
        <SectionHeader>Deployment Architecture</SectionHeader>

        <SubSection>
          <SubSectionHeader>Local Development</SubSectionHeader>
          <DiagramContainer>
            <DiagramGroup title="Local Machine" className="w-full">
              <DiagramRow className="gap-6">
                <div className="flex-1 space-y-4">
                  <DiagramNode icon={<Terminal className="h-4 w-4" />} size="md" className="w-full justify-center">
                    <div className="text-center">
                      <div className="font-medium">Terminal 1</div>
                      <div className="text-xs text-muted-foreground">ngrok Tunnel</div>
                    </div>
                  </DiagramNode>
                  <DiagramNode icon={<Code className="h-4 w-4" />} size="md" className="w-full justify-center">
                    <div className="text-center">
                      <div className="font-medium">Terminal 3</div>
                      <div className="text-xs text-muted-foreground">Agent Workflow</div>
                    </div>
                  </DiagramNode>
                </div>
                <div className="flex-1 space-y-4">
                  <DiagramNode icon={<Server className="h-4 w-4" />} size="md" variant="primary" className="w-full justify-center">
                    <div className="text-center">
                      <div className="font-medium">Terminal 2</div>
                      <div className="text-xs text-muted-foreground">Callback Server</div>
                    </div>
                  </DiagramNode>
                  <DiagramNode icon={<Database className="h-4 w-4" />} size="md" className="w-full justify-center">
                    <div className="text-center">
                      <div className="font-medium">SQLite DB</div>
                      <div className="text-xs text-muted-foreground">reddit_agent.db</div>
                    </div>
                  </DiagramNode>
                </div>
              </DiagramRow>
            </DiagramGroup>
          </DiagramContainer>
        </SubSection>

        <SubSection>
          <SubSectionHeader>Production (Railway/Fly.io)</SubSectionHeader>
          <DiagramContainer>
            <div className="space-y-4">
              {/* Cloud Platform */}
              <DiagramGroup title="Cloud Platform (Railway)" className="w-full">
                <DiagramRow className="gap-6">
                  <DiagramNode icon={<Server className="h-4 w-4" />} size="md" variant="primary" className="flex-1 justify-center">
                    <div className="text-center">
                      <div className="font-medium">Callback Server</div>
                      <div className="text-xs text-muted-foreground">Always On</div>
                    </div>
                  </DiagramNode>
                  <DiagramNode icon={<Database className="h-4 w-4" />} size="md" className="flex-1 justify-center">
                    <div className="text-center">
                      <div className="font-medium">SQLite DB</div>
                      <div className="text-xs text-muted-foreground">Persistent Volume</div>
                    </div>
                  </DiagramNode>
                </DiagramRow>
              </DiagramGroup>

              <DiagramConnector label="Approval Links" />

              {/* Local / GitHub Actions */}
              <DiagramGroup title="Local / GitHub Actions" className="w-full">
                <DiagramRow>
                  <DiagramNode icon={<GitBranch className="h-4 w-4" />} size="md" className="w-full justify-center">
                    <div className="text-center">
                      <div className="font-medium">Agent Workflow</div>
                      <div className="text-xs text-muted-foreground">Scheduled (cron)</div>
                    </div>
                  </DiagramNode>
                </DiagramRow>
              </DiagramGroup>
            </div>
          </DiagramContainer>
        </SubSection>
      </Section>

      <Section>
        <SectionHeader>Testing Strategy</SectionHeader>

        <SubSection>
          <SubSectionHeader>Unit Tests (136 tests)</SubSectionHeader>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li><strong className="text-foreground">Services</strong>: <InlineCode>test_reddit_client.py</InlineCode>, <InlineCode>test_context_builder.py</InlineCode>, etc.</li>
            <li><strong className="text-foreground">Workflow</strong>: <InlineCode>test_graph.py</InlineCode>, <InlineCode>test_nodes.py</InlineCode></li>
            <li><strong className="text-foreground">Utilities</strong>: <InlineCode>test_logging.py</InlineCode>, <InlineCode>test_config.py</InlineCode></li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>Integration Tests</SubSectionHeader>
          <ul className="list-disc list-inside space-y-1 text-muted-foreground">
            <li><strong className="text-foreground">Approval flow</strong>: End-to-end token → approve → publish</li>
            <li><strong className="text-foreground">Workflow</strong>: Fetch → score → generate → notify</li>
            <li><strong className="text-foreground">Database</strong>: Migrations, queries, constraints</li>
          </ul>
        </SubSection>

        <SubSection>
          <SubSectionHeader>CI/CD</SubSectionHeader>
          <CodeBlock>{`# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
          pytest --cov=. --cov-report=xml`}</CodeBlock>
        </SubSection>
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
              <p className="text-sm text-muted-foreground">Deep dive into quality scoring and diversity</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">
                <Link href="/configuration" className="text-primary hover:underline">Configuration</Link>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Advanced configuration options</p>
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
          <p><strong>Architecture Design</strong>: The system follows a modular, workflow-driven design that prioritizes safety, quality, and human oversight. Each component is independently testable and can be swapped or extended without affecting others.</p>
        </Callout>
      </Section>
    </PageWrapper>
  )
}
