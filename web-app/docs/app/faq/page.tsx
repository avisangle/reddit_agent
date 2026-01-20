import Link from "next/link"
import { Callout, CodeBlock } from "@/components/docs"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export default function FAQPage() {
  return (
    <article className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-4xl font-bold mb-4">Frequently Asked Questions</h1>
      <p className="text-muted-foreground mb-8">Common questions and troubleshooting for the Reddit Agent.</p>

      <h2 className="text-2xl font-semibold mt-12 mb-4">General Questions</h2>

      <Accordion type="single" collapsible className="w-full space-y-2">
        <AccordionItem value="tos" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">Is this bot against Reddit&apos;s Terms of Service?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p>The agent is designed to operate <strong>within</strong> Reddit&apos;s guidelines:</p>
            <p><strong>✅ Compliant:</strong></p>
            <ul>
              <li>≤8 comments/day (well below spam thresholds)</li>
              <li>Human-in-the-loop approval (you review every comment)</li>
              <li>Subreddit allow-lists (you control where it operates)</li>
              <li>Natural timing with anti-fingerprinting</li>
              <li>Respects subreddit rules and culture</li>
            </ul>
            <p><strong>❌ Against ToS:</strong></p>
            <ul>
              <li>Mass posting (agent prevents this)</li>
              <li>Automated upvoting/downvoting (agent doesn&apos;t do this)</li>
              <li>Ban evasion (don&apos;t use if you&apos;re banned)</li>
              <li>Spam/manipulation (HITL approval prevents this)</li>
            </ul>
            <Callout variant="warning">
              <p><strong>Your responsibility</strong>: You must approve all comments. Don&apos;t approve low-quality or spammy content. Use responsibly and ethically.</p>
            </Callout>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="shadowban" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">Will I get shadowbanned?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p>The agent includes extensive anti-shadowban measures:</p>
            <ul>
              <li>Volume limits (≤8/day)</li>
              <li>Random timing jitter</li>
              <li>Subreddit diversity</li>
              <li>Quality-first selection</li>
              <li>Shadowban detection circuit breaker</li>
            </ul>
            <p><strong>Risk level</strong>: Low if used as designed. Higher risk if:</p>
            <ul>
              <li>You approve low-quality comments</li>
              <li>You operate in subreddits where you&apos;re not active</li>
              <li>You override safety limits (hardcoded, can&apos;t do this)</li>
            </ul>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="cost" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">How much does it cost to run?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Free tier sufficient:</strong></p>
            <ul>
              <li>Gemini API: 50 requests/day free (enough for ≤8 comments)</li>
              <li>Railway/Fly.io: $0-5/month for callback server</li>
              <li>ngrok: Free for local development</li>
            </ul>
            <p><strong>Estimated monthly cost</strong>: $0-10 depending on deployment.</p>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <h2 className="text-2xl font-semibold mt-12 mb-4">Setup Questions</h2>

      <Accordion type="single" collapsible className="w-full space-y-2">
        <AccordionItem value="no-candidates" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">&quot;No candidates found&quot; - What&apos;s wrong?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Common causes:</strong></p>
            <ol>
              <li><strong>No new content</strong>: Allowed subreddits have no rising posts/comments
                <ul><li>Solution: Wait or add more subreddits to <code>ALLOWED_SUBREDDITS</code></li></ul>
              </li>
              <li><strong>All in cooldown</strong>: Previously replied items still in cooldown period
                <ul>
                  <li>Solution: Wait for cooldown to expire (6h inbox, 24h rising)</li>
                  <li>Check: <code>SELECT * FROM replied_items WHERE cooldown_until &gt; datetime(&apos;now&apos;)</code></li>
                </ul>
              </li>
              <li><strong>Quality threshold</strong>: No candidates meet minimum quality score
                <ul><li>Solution: Lower <code>DIVERSITY_QUALITY_BOOST_THRESHOLD</code> (default: 0.75)</li></ul>
              </li>
              <li><strong>Bot filtering</strong>: All candidates are bot accounts
                <ul><li>Solution: Normal behavior, wait for human-authored content</li></ul>
              </li>
            </ol>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="approval-link" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">&quot;Approval link not working&quot; - How to fix?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Checklist:</strong></p>
            <ol>
              <li><strong>Callback server running?</strong></li>
            </ol>
            <CodeBlock>{`# Check if server is up
curl http://localhost:8000/health`}</CodeBlock>
            <ol start={2}>
              <li><strong>PUBLIC_URL correct?</strong></li>
            </ol>
            <CodeBlock>{`# .env should match your actual URL
PUBLIC_URL=https://abc123.ngrok.io`}</CodeBlock>
            <ol start={3}>
              <li><strong>ngrok tunnel active?</strong> (local dev)</li>
            </ol>
            <CodeBlock>{`# Terminal 1
ngrok http 8000
# Copy forwarding URL to PUBLIC_URL`}</CodeBlock>
            <ol start={4}>
              <li><strong>Token expired?</strong> (48h TTL)
                <ul>
                  <li>Check <code>draft_queue.token_expires_at</code></li>
                  <li>Request new draft if expired</li>
                </ul>
              </li>
            </ol>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="password" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">How do I change the default password?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>For admin dashboard</strong> (Phase 1):</p>
            <CodeBlock>{`# Generate new bcrypt hash
source venv/bin/activate
python -c "import bcrypt; print(bcrypt.hashpw(b'your_new_password', bcrypt.gensalt(12)).decode())"

# Update .env
ADMIN_PASSWORD_HASH=$2b$12$<your_new_hash>`}</CodeBlock>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <h2 className="text-2xl font-semibold mt-12 mb-4">Workflow Questions</h2>

      <Accordion type="single" collapsible className="w-full space-y-2">
        <AccordionItem value="no-approve" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">What happens if I don&apos;t approve a draft?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>After 48 hours:</strong></p>
            <ul>
              <li>Token expires</li>
              <li>Draft remains as <code>PENDING</code> in database</li>
              <li>No action taken</li>
              <li>Candidate moves to cooldown (6h or 24h)</li>
            </ul>
            <p><strong>Manual cleanup:</strong></p>
            <CodeBlock>{`-- View pending drafts
SELECT * FROM draft_queue WHERE status = 'PENDING';

-- Manually reject expired drafts
UPDATE draft_queue SET status = 'REJECTED' WHERE token_expires_at < datetime('now');`}</CodeBlock>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="approve-later" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">Can I approve drafts later?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Yes</strong>, approval links work for 48 hours:</p>
            <ul>
              <li>Save Slack/Telegram message</li>
              <li>Click &quot;Approve&quot; anytime before expiry</li>
              <li>Draft publishes immediately after approval</li>
            </ul>
            <Callout variant="info">
              <p><strong>Tip</strong>: Star important Slack messages to review later.</p>
            </Callout>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="manual-publish" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">How do I manually publish approved drafts?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p>If <code>AUTO_PUBLISH_ENABLED=False</code>:</p>
            <CodeBlock>{`# Publish up to 3 approved drafts
python main.py publish --limit 3

# Dry run (test without posting)
python main.py publish --limit 3 --dry-run`}</CodeBlock>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="edit-draft" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">Can I edit a draft before approving?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Not directly</strong>, but you can:</p>
            <ol>
              <li>Reject the draft</li>
              <li>Copy the draft text</li>
              <li>Manually post with your edits</li>
              <li>Mark original target as replied:</li>
            </ol>
            <CodeBlock>{`INSERT INTO replied_items (item_id, subreddit, candidate_type, replied_at)
VALUES ('t1_abc123', 'sysadmin', 'MANUAL', datetime('now'));`}</CodeBlock>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <h2 className="text-2xl font-semibold mt-12 mb-4">Feature Questions</h2>

      <Accordion type="single" collapsible className="w-full space-y-2">
        <AccordionItem value="quality-scoring" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">How does quality scoring work?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p>See <Link href="/features#quality-scoring-system">Features - Quality Scoring</Link> for detailed explanation.</p>
            <p><strong>Quick summary:</strong></p>
            <ul>
              <li>7 weighted factors (upvote ratio, karma, freshness, etc.)</li>
              <li>Historical learning from past performance</li>
              <li>Score range: 0.0 (low quality) to 1.0 (high quality)</li>
              <li>Exploration: 25% randomization to avoid patterns</li>
            </ul>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="inbox-vs-rising" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">What&apos;s the difference between inbox and rising content?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Aspect</TableHead>
                  <TableHead>Inbox Replies</TableHead>
                  <TableHead>Rising Content</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow><TableCell><strong>Priority</strong></TableCell><TableCell>HIGH</TableCell><TableCell>NORMAL</TableCell></TableRow>
                <TableRow><TableCell><strong>Cooldown</strong></TableCell><TableCell>6 hours</TableCell><TableCell>24 hours</TableCell></TableRow>
                <TableRow><TableCell><strong>Source</strong></TableCell><TableCell>Direct replies to your posts/comments</TableCell><TableCell>Rising posts/comments in subreddits</TableCell></TableRow>
                <TableRow><TableCell><strong>Risk</strong></TableCell><TableCell>Lower (natural to respond)</TableCell><TableCell>Higher (proactive commenting)</TableCell></TableRow>
              </TableBody>
            </Table>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="disable-diversity">
          <AccordionTrigger>Can I disable diversity limits?</AccordionTrigger>
          <AccordionContent>
            <CodeBlock>{`# .env
DIVERSITY_ENABLED=False`}</CodeBlock>
            <p><strong>Not recommended</strong>: Diversity prevents spam patterns. Disabling increases shadowban risk.</p>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="historical-performance" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">How do I view historical performance?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <CodeBlock>{`-- Best performing subreddits
SELECT subreddit,
       AVG(engagement_score) as avg_engagement,
       COUNT(*) as num_comments
FROM performance_history
WHERE was_removed = FALSE
GROUP BY subreddit
ORDER BY avg_engagement DESC;

-- Recent performance trend
SELECT DATE(created_at) as date,
       AVG(engagement_score) as avg_engagement,
       AVG(upvotes) as avg_upvotes
FROM performance_history
WHERE created_at > datetime('now', '-30 days')
GROUP BY DATE(created_at)
ORDER BY date DESC;`}</CodeBlock>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <h2 className="text-2xl font-semibold mt-12 mb-4">Troubleshooting</h2>

      <Accordion type="single" collapsible className="w-full space-y-2">
        <AccordionItem value="rate-limit-llm" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">&quot;LLM API error: Rate limit exceeded&quot;</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Gemini:</strong></p>
            <ul>
              <li>Free tier: 50 requests/day</li>
              <li>Solution: Upgrade to paid tier or wait 24h</li>
            </ul>
            <p><strong>OpenAI:</strong></p>
            <ul>
              <li>Check billing: <a href="https://platform.openai.com/account/billing">platform.openai.com/account/billing</a></li>
              <li>Solution: Add payment method or reduce usage</li>
            </ul>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="rate-limit-reddit" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">&quot;Reddit API error: 429 Too Many Requests&quot;</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Cause:</strong> Exceeded 60 requests/minute limit.</p>
            <p><strong>Solution:</strong></p>
            <ul>
              <li>Agent respects rate limits automatically</li>
              <li>If still occurring, add delay: <code>REDDIT_API_DELAY=2</code> (2 seconds)</li>
            </ul>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="shadowban-detected" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">&quot;Shadowban risk detected - Agent halted&quot;</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Cause:</strong> High downvote rate detected (&gt;70%).</p>
            <p><strong>What to do:</strong></p>
            <ol>
              <li>Review recent comments for quality issues</li>
              <li>Check if you violated subreddit rules</li>
              <li>Wait 24-48 hours before resuming</li>
              <li>Consider adjusting persona or response style</li>
            </ol>
            <p><strong>Resume after fixing:</strong></p>
            <CodeBlock>{`# Check recent performance
python main.py check-engagement --limit 20

# If false alarm, clear warning and resume
# (Manual override - use cautiously)`}</CodeBlock>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="db-locked" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">Database is locked</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Cause:</strong> Multiple processes accessing SQLite simultaneously.</p>
            <p><strong>Solution:</strong></p>
            <CodeBlock>{`# Ensure only one agent runs at a time
pkill -f "python main.py run"

# Restart callback server
python main.py server`}</CodeBlock>
            <p><strong>Better solution:</strong> Use PostgreSQL for production:</p>
            <CodeBlock>{`DATABASE_URL=postgresql://user:pass@host:5432/reddit_agent`}</CodeBlock>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="module-not-found" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">&quot;ModuleNotFoundError&quot; on import</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Cause:</strong> Virtual environment not activated.</p>
            <p><strong>Solution:</strong></p>
            <CodeBlock>{`# ALWAYS activate venv first
source venv/bin/activate  # macOS/Linux
venv\\Scripts\\activate      # Windows

# Then run commands
python main.py run --once`}</CodeBlock>
            <Callout variant="error">
              <p><strong>Critical</strong>: ALL Python commands must run with venv activated.</p>
            </Callout>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <h2 className="text-2xl font-semibold mt-12 mb-4">Advanced Questions</h2>

      <Accordion type="single" collapsible className="w-full space-y-2">
        <AccordionItem value="multiple-accounts" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">Can I run multiple accounts?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Technically possible</strong> but <strong>not recommended</strong>:</p>
            <ul>
              <li>Each account needs separate <code>.env</code> and database</li>
              <li>Increases complexity and risk</li>
              <li>Reddit frowns upon multiple accounts</li>
            </ul>
            <p><strong>If you must:</strong></p>
            <CodeBlock>{`# Account 1
python main.py run --once --config .env.account1

# Account 2
python main.py run --once --config .env.account2`}</CodeBlock>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="migrate-postgres" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">How do I migrate from SQLite to PostgreSQL?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <CodeBlock>{`# 1. Export SQLite data
sqlite3 reddit_agent.db .dump > dump.sql

# 2. Update .env
DATABASE_URL=postgresql://user:pass@host:5432/reddit_agent

# 3. Run migrations on PostgreSQL
alembic upgrade head

# 4. Import data
psql reddit_agent < dump.sql`}</CodeBlock>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="customize-prompts" className="bg-card rounded-md border-b-0 shadow-md data-[state=open]:shadow-lg">
          <AccordionTrigger className="px-5 [&>svg]:rotate-90 [&[data-state=open]>svg]:rotate-0">Can I customize LLM prompts?</AccordionTrigger>
          <AccordionContent className="text-muted-foreground px-5">
            <p><strong>Yes</strong>, edit <code>prompts/templates.yaml</code>:</p>
            <CodeBlock>{`personas:
  helpful:
    system_prompt: "You are a helpful Reddit user..."
    few_shot_examples:
      - input: "How do I...?"
        output: "Great question! Here's how..."`}</CodeBlock>
            <p><strong>After editing:</strong></p>
            <CodeBlock>{`# Restart server to reload prompts
pkill -f "python main.py server"
python main.py server`}</CodeBlock>
          </AccordionContent>
        </AccordionItem>
      </Accordion>

      <h2 className="text-2xl font-semibold mt-12 mb-4">Need More Help?</h2>
      <ul>
        <li><strong>GitHub Issues</strong>: <a href="https://github.com/avisangle/reddit_agent/issues">github.com/avisangle/reddit_agent/issues</a></li>
        <li><strong>Documentation</strong>: <Link href="/getting-started">Getting Started</Link>, <Link href="/architecture">Architecture</Link>, <Link href="/features">Features</Link></li>
        <li><strong>Best Practices</strong>: <Link href="/getting-started#best-practices">Tips for optimal usage</Link></li>
        <li><strong>Logs</strong>: Check <code>reddit_agent.log</code> for detailed error messages</li>
      </ul>

      <hr className="my-8" />

      <Callout variant="success">
        <p><strong>Still stuck?</strong> Review the troubleshooting section above or check your logs at <code>reddit_agent.log</code> for detailed error messages.</p>
      </Callout>
    </article>
  )
}
