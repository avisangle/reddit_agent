'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogClose } from '@/components/ui/dialog';
import { AdminHeader } from '@/components/admin-header';

// --- Workflow Node Data (mirroring metadata.nodes) ---
const WORKFLOW_NODES: Record<string, { label: string; description: string; node_type: string; inputs?: string[]; outputs?: string[] }> = {
    fetch_candidates: { label: 'Fetch Candidates', description: 'Retrieves new posts and comments from allowed subreddits via the Reddit API.', node_type: 'Fetch', inputs: ['subreddits'], outputs: ['candidates'] },
    check_candidates: { label: 'Check Candidates', description: 'Conditional: checks if any candidates were found.', node_type: 'Conditional', inputs: ['candidates'], outputs: [] },
    filter_duplicates: { label: 'Filter Duplicates', description: 'Removes candidates that have already been processed or replied to.', node_type: 'Filter', inputs: ['candidates', 'history'], outputs: ['filtered_candidates'] },
    score_relevance: { label: 'Score Relevance', description: 'Uses LLM to score how relevant each candidate is for engagement.', node_type: 'AI', inputs: ['candidates'], outputs: ['scored_candidates'] },
    filter_by_score: { label: 'Filter by Score', description: 'Removes candidates below the quality threshold.', node_type: 'Filter', inputs: ['scored_candidates'], outputs: ['quality_candidates'] },
    sort_candidates: { label: 'Sort Candidates', description: 'Sorts remaining candidates by score (highest first).', node_type: 'Sort', inputs: ['quality_candidates'], outputs: ['sorted_candidates'] },
    check_daily_limit: { label: 'Check Daily Limit', description: 'Verifies the daily comment limit has not been exceeded.', node_type: 'Conditional', inputs: ['daily_count', 'limit'], outputs: [] },
    generate_draft: { label: 'Generate Draft', description: 'Uses LLM to create a human-like reply draft for approval.', node_type: 'AI', inputs: ['candidate', 'context'], outputs: ['draft'] },
    assess_risk: { label: 'Assess Risk', description: 'Evaluates shadowban/spam risk of the generated draft.', node_type: 'AI', inputs: ['draft'], outputs: ['risk_score'] },
    send_for_approval: { label: 'Send for Approval', description: 'Sends draft to user via Slack/Telegram for human-in-the-loop review.', node_type: 'Notify', inputs: ['draft'], outputs: ['approval_request'] },
    await_approval: { label: 'Await Approval', description: 'Pauses and waits for user to approve/reject the draft.', node_type: 'Process', inputs: ['approval_request'], outputs: ['decision'] },
    publish_comment: { label: 'Publish Comment', description: 'Posts the approved comment to Reddit.', node_type: 'Process', inputs: ['draft', 'decision'], outputs: ['published'] },
    end: { label: 'End', description: 'Workflow terminates (daily limit reached or no more candidates).', node_type: 'Process', inputs: [], outputs: [] },
};

const NODE_TYPE_COLORS: Record<string, { bg: string; border: string }> = {
    Fetch: { bg: '#fef3c7', border: '#92400e' },
    Filter: { bg: '#fed7aa', border: '#c2410c' },
    Sort: { bg: '#fde68a', border: '#ca8a04' },
    Conditional: { bg: '#fca5a5', border: '#dc2626' },
    Process: { bg: '#d1fae5', border: '#059669' },
    AI: { bg: '#dbeafe', border: '#2563eb' },
    Notify: { bg: '#e9d5ff', border: '#9333ea' },
};


export default function WorkflowPage() {
    const [selectedNode, setSelectedNode] = useState<string | null>(null);

    const handleNodeClick = (nodeId: string) => {
        setSelectedNode(nodeId);
    };

    const nodeData = selectedNode ? WORKFLOW_NODES[selectedNode] : null;

    return (
        <div className="min-h-screen bg-background">
            <AdminHeader />
            <main className="container mx-auto px-4 py-8">
                <div className="max-w-5xl mx-auto">
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold tracking-tight text-foreground">Workflow Visualizer</h1>
                        <p className="text-muted-foreground mt-1">Interactive diagram of the 13-node LangGraph pipeline</p>
                    </div>

                    {/* Stats */}
                    <div className="grid gap-4 md:grid-cols-3 mb-8">
                        <Card>
                            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Total Nodes</CardTitle></CardHeader>
                            <CardContent><div className="text-3xl font-bold text-primary">{Object.keys(WORKFLOW_NODES).length}</div></CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Total Edges</CardTitle></CardHeader>
                            <CardContent><div className="text-3xl font-bold text-primary">14</div></CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Node Types</CardTitle></CardHeader>
                            <CardContent><div className="text-3xl font-bold text-primary">{Object.keys(NODE_TYPE_COLORS).length}</div></CardContent>
                        </Card>
                    </div>

                    {/* Legend */}
                    <Card className="mb-8">
                        <CardContent className="pt-4">
                            <div className="flex flex-wrap gap-4">
                                {Object.entries(NODE_TYPE_COLORS).map(([type, colors]) => (
                                    <div key={type} className="flex items-center gap-2 text-sm">
                                        <div className="w-5 h-5 rounded-sm border-2" style={{ backgroundColor: colors.bg, borderColor: colors.border }} />
                                        <span>{type}</span>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* SVG Diagram (Simplified Static Version) */}
                    <Card className="mb-8">
                        <CardHeader>
                            <CardTitle>Pipeline Flow</CardTitle>
                            <CardDescription>Click any node to see details</CardDescription>
                        </CardHeader>
                        <CardContent className="overflow-x-auto">
                            <svg viewBox="0 0 1000 700" className="w-full min-w-[800px]" style={{ maxHeight: '600px' }}>
                                {/* Edges (simplified) */}
                                <defs>
                                    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto" fill="#94a3b8">
                                        <polygon points="0 0, 10 3.5, 0 7" />
                                    </marker>
                                </defs>

                                {/* Flow lines */}
                                <path d="M 150 90 L 150 130" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrowhead)" />
                                <path d="M 150 190 L 150 230" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrowhead)" />
                                <path d="M 150 290 L 150 340" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrowhead)" />
                                <path d="M 150 400 L 150 440" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrowhead)" />
                                <path d="M 150 500 L 150 540" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrowhead)" />
                                <path d="M 220 570 L 400 570" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrowhead)" />
                                <path d="M 560 570 L 700 570" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrowhead)" />
                                <path d="M 860 570 L 920 570 L 920 350" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrowhead)" />
                                <path d="M 920 290 L 920 130 L 800 130" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrowhead)" />
                                <path d="M 640 130 L 560 130 L 560 230" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrowhead)" />
                                <path d="M 560 290 L 560 340" stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrowhead)" />

                                {/* Nodes */}
                                {Object.entries(WORKFLOW_NODES).map(([nodeId, node], i) => {
                                    const x = (i % 3) * 300 + 80;
                                    const y = Math.floor(i / 3) * 110 + 50;
                                    const colors = NODE_TYPE_COLORS[node.node_type] || { bg: '#e5e7eb', border: '#6b7280' };
                                    return (
                                        <g key={nodeId} className="cursor-pointer hover:opacity-80 transition-opacity" onClick={() => handleNodeClick(nodeId)}>
                                            <rect x={x} y={y} width="140" height="60" rx="8" fill={colors.bg} stroke={colors.border} strokeWidth="2" />
                                            <text x={x + 70} y={y + 35} textAnchor="middle" fontSize="12" fontWeight="600" fill="#1f2937">{node.label}</text>
                                        </g>
                                    );
                                })}
                            </svg>
                        </CardContent>
                    </Card>

                    {/* How to Read */}
                    <Card>
                        <CardHeader><CardTitle>How to Read This Diagram</CardTitle></CardHeader>
                        <CardContent>
                            <ul className="list-disc pl-5 space-y-1 text-muted-foreground">
                                <li><strong>Solid arrows</strong> - Linear flow between nodes</li>
                                <li><strong>Dashed red arrows</strong> - Conditional branches (if/else logic)</li>
                                <li><strong>Dashed purple arrow</strong> - Loop back to previous node</li>
                                <li><strong>Click any node</strong> - View detailed description and metadata</li>
                                <li><strong>Node colors</strong> - Indicate node type (fetch, filter, AI, etc.)</li>
                            </ul>
                        </CardContent>
                    </Card>

                    {/* Node Detail Modal */}
                    <Dialog open={!!selectedNode} onOpenChange={() => setSelectedNode(null)}>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>{nodeData?.label}</DialogTitle>
                                <DialogDescription>{nodeData?.description}</DialogDescription>
                            </DialogHeader>
                            <div className="space-y-2 text-sm mt-4 border rounded-md p-4 bg-muted/50">
                                <div className="flex gap-2"><span className="font-semibold w-20">Node ID:</span><code className="text-muted-foreground">{selectedNode}</code></div>
                                <div className="flex gap-2"><span className="font-semibold w-20">Type:</span><span className="text-muted-foreground">{nodeData?.node_type}</span></div>
                                {nodeData?.inputs && nodeData.inputs.length > 0 && (
                                    <div className="flex gap-2"><span className="font-semibold w-20">Inputs:</span><span className="text-muted-foreground">{nodeData.inputs.join(', ')}</span></div>
                                )}
                                {nodeData?.outputs && nodeData.outputs.length > 0 && (
                                    <div className="flex gap-2"><span className="font-semibold w-20">Outputs:</span><span className="text-muted-foreground">{nodeData.outputs.join(', ')}</span></div>
                                )}
                            </div>
                        </DialogContent>
                    </Dialog>
                </div>
            </main>
        </div>
    );
}
