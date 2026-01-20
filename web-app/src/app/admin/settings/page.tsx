'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Loader2, Eye, EyeOff, Save, RotateCcw } from 'lucide-react';
import { Toaster, toast } from 'sonner';
import { fetchWithAuth } from '@/lib/api-client';
import { AdminHeader } from '@/components/admin-header';

// Field groups for organization
const FIELD_GROUPS = {
    reddit: ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USERNAME', 'REDDIT_PASSWORD', 'REDDIT_USER_AGENT', 'ALLOWED_SUBREDDITS'],
    llm: ['GEMINI_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY'],
    notifications: ['NOTIFICATION_TYPE', 'SLACK_WEBHOOK_URL', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'WEBHOOK_URL', 'PUBLIC_URL'],
    safety: ['MAX_COMMENTS_PER_DAY', 'MAX_COMMENTS_PER_RUN', 'SHADOWBAN_RISK_THRESHOLD', 'COOLDOWN_PERIOD_HOURS', 'POST_REPLY_RATIO', 'DRY_RUN'],
};

const SECRET_FIELDS = ['REDDIT_CLIENT_SECRET', 'REDDIT_PASSWORD', 'GEMINI_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'SLACK_WEBHOOK_URL', 'TELEGRAM_BOT_TOKEN', 'WEBHOOK_SECRET'];

const LABELS: Record<string, string> = {
    REDDIT_CLIENT_ID: 'Client ID',
    REDDIT_CLIENT_SECRET: 'Client Secret',
    REDDIT_USERNAME: 'Username',
    REDDIT_PASSWORD: 'Password',
    REDDIT_USER_AGENT: 'User Agent',
    ALLOWED_SUBREDDITS: 'Allowed Subreddits',
    GEMINI_API_KEY: 'Gemini API Key',
    OPENAI_API_KEY: 'OpenAI API Key',
    ANTHROPIC_API_KEY: 'Anthropic API Key',
    NOTIFICATION_TYPE: 'Notification Type',
    SLACK_WEBHOOK_URL: 'Slack Webhook URL',
    TELEGRAM_BOT_TOKEN: 'Telegram Bot Token',
    TELEGRAM_CHAT_ID: 'Telegram Chat ID',
    WEBHOOK_URL: 'Webhook URL',
    PUBLIC_URL: 'Public URL',
    MAX_COMMENTS_PER_DAY: 'Max Comments / Day',
    MAX_COMMENTS_PER_RUN: 'Max Comments / Run',
    SHADOWBAN_RISK_THRESHOLD: 'Risk Threshold (0-1)',
    COOLDOWN_PERIOD_HOURS: 'Cooldown (Hours)',
    POST_REPLY_RATIO: 'Post Reply Ratio',
    DRY_RUN: 'Dry Run Mode',
};

export default function SettingsPage() {
    const [formData, setFormData] = useState<Record<string, any>>({});
    const [originalData, setOriginalData] = useState<Record<string, any>>({});
    const [revealed, setRevealed] = useState<Record<string, boolean>>({});
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);


    useEffect(() => {
        // Fetch current env vars from backend
        fetchWithAuth('/admin/api/env')
            .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    setFormData(data.env_vars || {});
                    setOriginalData(data.env_vars || {});
                } else {
                    toast.error(data.error || 'Failed to load settings');
                }
                setLoading(false);
            })
            .catch(err => {
                console.error('Failed to load settings:', err);
                toast.error('Failed to load settings. Is the backend running?');
                setLoading(false);
            });
    }, []);


    const handleChange = (field: string, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const toggleReveal = (field: string) => {
        setRevealed(prev => ({ ...prev, [field]: !prev[field] }));
    };

    const resetForm = () => {
        setFormData({ ...originalData });
        toast.info('Form reset to original values');
    };

    const saveSettings = async () => {
        setSaving(true);
        try {
            const response = await fetchWithAuth('/admin/api/env/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ env_vars: formData }),
            });

            const data = await response.json();
            if (data.success) {
                toast.success(data.message || 'Settings saved successfully!');
                toast.warning('Restart the server to apply changes: python main.py server');
                setOriginalData({ ...formData });
            } else {
                toast.error(data.error || 'Failed to save settings');
            }
        } catch (err: any) {
            toast.error('Error: ' + err.message);
        } finally {
            setSaving(false);
        }
    };

    const renderField = (field: string) => {
        const isSecret = SECRET_FIELDS.includes(field);
        const label = LABELS[field] || field;

        if (field === 'NOTIFICATION_TYPE') {
            return (
                <div key={field} className="space-y-2">
                    <Label>{label}</Label>
                    <Select value={formData[field] || ''} onValueChange={(val) => handleChange(field, val)}>
                        <SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger>
                        <SelectContent>
                            <SelectItem value="slack">Slack</SelectItem>
                            <SelectItem value="telegram">Telegram</SelectItem>
                            <SelectItem value="webhook">Webhook</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            );
        }

        if (field === 'DRY_RUN') {
            return (
                <div key={field} className="flex items-center justify-between space-x-2">
                    <Label>{label}</Label>
                    <Switch checked={formData[field] === 'true' || formData[field] === true} onCheckedChange={(val) => handleChange(field, val)} />
                </div>
            );
        }

        return (
            <div key={field} className="space-y-2">
                <Label>{label}</Label>
                <div className="flex gap-2">
                    <Input
                        type={isSecret && !revealed[field] ? 'password' : 'text'}
                        value={formData[field] || ''}
                        onChange={(e) => handleChange(field, e.target.value)}
                        className="font-mono text-sm"
                    />
                    {isSecret && (
                        <Button variant="ghost" size="icon" onClick={() => toggleReveal(field)}>
                            {revealed[field] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </Button>
                    )}
                </div>
            </div>
        );
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background">
            <AdminHeader />
            <main className="container mx-auto px-4 py-8">
                <Toaster richColors position="top-right" />

                <div className="mb-8 max-w-3xl mx-auto">
                    <h1 className="text-3xl font-bold tracking-tight text-foreground">Settings</h1>
                    <p className="text-muted-foreground mt-1">Edit environment variables with validation and automatic backups</p>
                </div>

                <Card className="max-w-3xl mx-auto">
                    <CardContent className="pt-6">
                        <Tabs defaultValue="reddit" className="w-full">
                            <TabsList className="grid w-full grid-cols-4">
                                <TabsTrigger value="reddit">Reddit API</TabsTrigger>
                                <TabsTrigger value="llm">LLM Keys</TabsTrigger>
                                <TabsTrigger value="notifications">Notifications</TabsTrigger>
                                <TabsTrigger value="safety">Safety</TabsTrigger>
                            </TabsList>

                            <TabsContent value="reddit" className="mt-6 space-y-4">
                                <p className="text-sm text-muted-foreground mb-4">Credentials for Reddit authentication</p>
                                {FIELD_GROUPS.reddit.map(renderField)}
                            </TabsContent>

                            <TabsContent value="llm" className="mt-6 space-y-4">
                                <p className="text-sm text-muted-foreground mb-4">At least one LLM key is required</p>
                                {FIELD_GROUPS.llm.map(renderField)}
                            </TabsContent>

                            <TabsContent value="notifications" className="mt-6 space-y-4">
                                <p className="text-sm text-muted-foreground mb-4">Configure how the agent notifies you</p>
                                {FIELD_GROUPS.notifications.map(renderField)}
                            </TabsContent>

                            <TabsContent value="safety" className="mt-6 space-y-4">
                                <p className="text-sm text-muted-foreground mb-4">Operational boundaries to prevent bans</p>
                                {FIELD_GROUPS.safety.map(renderField)}
                            </TabsContent>
                        </Tabs>

                        {/* Action Buttons */}
                        <div className="flex gap-4 pt-6 mt-6 border-t">
                            <Button onClick={saveSettings} disabled={saving}>
                                {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                                Save changes
                            </Button>
                            <Button variant="outline" onClick={resetForm} disabled={saving}>
                                <RotateCcw className="mr-2 h-4 w-4" /> Reset
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </main>
        </div>
    );
}
