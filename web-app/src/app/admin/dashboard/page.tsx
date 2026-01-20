'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Bar, BarChart, Line, LineChart, ResponsiveContainer, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, Legend } from 'recharts';
import { ArrowUpRight, CheckCircle, Clock, FileText, Ban, AlertCircle, Loader2 } from 'lucide-react';
import { fetchWithAuth } from '@/lib/api-client';
import { Toaster, toast } from 'sonner';
import { AdminHeader } from '@/components/admin-header';

// Mock Data (Replace with API fetch to /api/stats)
const MOCK_STATS = {
    status_counts: { PENDING: 5, APPROVED: 12, PUBLISHED: 34, REJECTED: 3 },
    daily_count: { count: 3, limit: 8, percentage: 37.5 },
    performance: { approval_rate: 85, publish_rate: 92 },
    recent_drafts: [
        { subreddit: 'sysadmin', status: 'PENDING', quality_score: 0.85, created_at: '2025-06-15 10:30', context_url: '#' },
        { subreddit: 'python', status: 'APPROVED', quality_score: 0.92, created_at: '2025-06-15 09:15', context_url: '#' },
        { subreddit: 'startups', status: 'PUBLISHED', quality_score: 0.78, created_at: '2025-06-14 16:45', context_url: '#' },
        { subreddit: 'reactjs', status: 'REJECTED', quality_score: 0.45, created_at: '2025-06-14 14:20', context_url: '#' },
    ],
    weekly_trend: [
        { date: 'Mon', count: 4 },
        { date: 'Tue', count: 6 },
        { date: 'Wed', count: 3 },
        { date: 'Thu', count: 8 },
        { date: 'Fri', count: 5 },
        { date: 'Sat', count: 2 },
        { date: 'Sun', count: 7 },
    ],
    subreddit_distribution: [
        { subreddit: 'python', count: 12 },
        { subreddit: 'sysadmin', count: 8 },
        { subreddit: 'reactjs', count: 5 },
        { subreddit: 'startups', count: 3 },
    ]
};


export default function DashboardPage() {
    const [stats, setStats] = useState(MOCK_STATS);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch real dashboard data from backend
    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                setLoading(true);
                const response = await fetchWithAuth('/admin/api/dashboard');
                const result = await response.json();

                if (result.success && result.data) {
                    setStats(result.data);
                    setError(null);
                } else {
                    setError(result.error || 'Failed to load dashboard data');
                    toast.error('Failed to load dashboard data');
                }
            } catch (err: any) {
                console.error('Dashboard fetch error:', err);
                setError(err.message || 'Failed to connect to backend');
                toast.error('Failed to load dashboard. Using cached data.');
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);


    const pieData = [
        { name: 'Pending', value: stats.status_counts.PENDING, color: '#fef3c7' }, // yellow
        { name: 'Approved', value: stats.status_counts.APPROVED, color: '#d1fae5' }, // green
        { name: 'Published', value: stats.status_counts.PUBLISHED, color: '#dbeafe' }, // blue
        { name: 'Rejected', value: stats.status_counts.REJECTED, color: '#fee2e2' }, // red
    ];

    const COLORS = ['#f59e0b', '#10b981', '#3b82f6', '#ef4444'];

    // Show loading spinner while fetching data
    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
                    <p className="text-muted-foreground">Loading dashboard data...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background">
            <AdminHeader />
            <main className="container mx-auto px-4 py-8">
                <Toaster richColors position="top-right" />

                <div className="max-w-5xl mx-auto">
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold tracking-tight text-foreground">Dashboard</h1>
                        <p className="text-muted-foreground mt-1">Reddit Comment Engagement Agent v2.5</p>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Pending Drafts</CardTitle>
                                <Clock className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.status_counts.PENDING}</div>
                                <p className="text-xs text-muted-foreground">Requires attention</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Today's Comments</CardTitle>
                                <FileText className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.daily_count.count} / {stats.daily_count.limit}</div>
                                <p className="text-xs text-muted-foreground">{stats.daily_count.percentage}% of daily limit</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Approval Rate</CardTitle>
                                <CheckCircle className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.performance.approval_rate}%</div>
                                <p className="text-xs text-muted-foreground">Last 7 days</p>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Publish Rate</CardTitle>
                                <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.performance.publish_rate}%</div>
                                <p className="text-xs text-muted-foreground">Last 7 days</p>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Charts Section */}
                    <div className="grid gap-4 md:grid-cols-7 mb-8">
                        <Card className="md:col-span-3">
                            <CardHeader>
                                <CardTitle>Status Distribution</CardTitle>
                                <CardDescription>Breakdown of comment statuses</CardDescription>
                            </CardHeader>
                            <CardContent className="h-[250px] flex items-center justify-center">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={pieData}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={60}
                                            outerRadius={80}
                                            paddingAngle={5}
                                            dataKey="value"
                                        >
                                            {pieData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip />
                                        <Legend verticalAlign="bottom" height={36} />
                                    </PieChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>

                        <Card className="md:col-span-4">
                            <CardHeader>
                                <CardTitle>7-Day Trend</CardTitle>
                                <CardDescription>Comments published over the last week</CardDescription>
                            </CardHeader>
                            <CardContent className="h-[250px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={stats.weekly_trend}>
                                        <XAxis dataKey="date" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                                        <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}`} />
                                        <Tooltip
                                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                        />
                                        <Line type="monotone" dataKey="count" stroke="#f59e0b" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 8 }} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="grid gap-4 md:grid-cols-7">
                        {/* Recent Drafts */}
                        <Card className="md:col-span-4">
                            <CardHeader>
                                <CardTitle>Recent Drafts</CardTitle>
                                <CardDescription>Latest generated comments</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Subreddit</TableHead>
                                            <TableHead>Status</TableHead>
                                            <TableHead>Quality</TableHead>
                                            <TableHead>Created</TableHead>
                                            <TableHead className="text-right">Action</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {stats.recent_drafts && stats.recent_drafts.length > 0 ? (
                                            stats.recent_drafts.map((draft, i) => (
                                                <TableRow key={i}>
                                                    <TableCell className="font-medium">r/{draft.subreddit}</TableCell>
                                                    <TableCell>
                                                        <Badge variant={
                                                            draft.status === 'APPROVED' ? 'default' :
                                                                draft.status === 'PUBLISHED' ? 'secondary' :
                                                                    draft.status === 'REJECTED' ? 'destructive' : 'outline'
                                                        }>
                                                            {draft.status}
                                                        </Badge>
                                                    </TableCell>
                                                    <TableCell>{draft.quality_score}</TableCell>
                                                    <TableCell className="text-xs text-muted-foreground">{draft.created_at}</TableCell>
                                                    <TableCell className="text-right">
                                                        {draft.status === 'PENDING' && (
                                                            <Button variant="ghost" size="sm" asChild>
                                                                <a href={draft.context_url} className="text-blue-600 hover:text-blue-800">View</a>
                                                            </Button>
                                                        )}
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        ) : (
                                            <TableRow>
                                                <TableCell colSpan={5} className="text-center text-muted-foreground py-8">
                                                    No drafts yet. Run the agent to generate comments.
                                                </TableCell>
                                            </TableRow>
                                        )}
                                    </TableBody>
                                </Table>
                            </CardContent>
                        </Card>

                        {/* Subreddit Distribution */}
                        <Card className="md:col-span-3">
                            <CardHeader>
                                <CardTitle>Subreddit Distribution</CardTitle>
                                <CardDescription>Activity by community</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {stats.subreddit_distribution && stats.subreddit_distribution.length > 0 ? (
                                        stats.subreddit_distribution.map((item, i) => {
                                            const maxCount = Math.max(...stats.subreddit_distribution.map(d => d.count), 1);
                                            return (
                                                <div key={i} className="flex items-center gap-2">
                                                    <div className="w-[80px] text-sm text-gray-500 truncate" title={item.subreddit}>r/{item.subreddit}</div>
                                                    <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                                                        <div
                                                            className="h-full bg-primary rounded-full"
                                                            style={{ width: `${(item.count / maxCount) * 100}%` }}
                                                        />
                                                    </div>
                                                    <div className="w-[30px] text-right text-sm font-medium">{item.count}</div>
                                                </div>
                                            );
                                        })
                                    ) : (
                                        <div className="text-center text-muted-foreground py-8">
                                            No activity yet. Run the agent to start engaging.
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </main>
        </div>
    );
}
