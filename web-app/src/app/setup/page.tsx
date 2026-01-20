'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Check, ChevronRight, ChevronLeft, Loader2, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function SetupWizard() {
    const [currentStep, setCurrentStep] = useState(1);
    const [completing, setCompleting] = useState(false);
    const [setupError, setSetupError] = useState('');

    // Configuration State
    const [config, setConfig] = useState({
        REDDIT_CLIENT_ID: '',
        REDDIT_CLIENT_SECRET: '',
        REDDIT_USERNAME: '',
        REDDIT_PASSWORD: '',
        REDDIT_USER_AGENT: '',
        ALLOWED_SUBREDDITS: '',

        GEMINI_API_KEY: '',
        OPENAI_API_KEY: '',
        ANTHROPIC_API_KEY: '',

        NOTIFICATION_TYPE: '',
        SLACK_WEBHOOK_URL: '',
        SLACK_CHANNEL: '',
        TELEGRAM_BOT_TOKEN: '',
        TELEGRAM_CHAT_ID: '',
        WEBHOOK_URL: '',
        WEBHOOK_SECRET: '',
        PUBLIC_URL: '',

        MAX_COMMENTS_PER_DAY: 8,
        MAX_COMMENTS_PER_RUN: 3,
        SHADOWBAN_RISK_THRESHOLD: 0.7,
        COOLDOWN_PERIOD_HOURS: 24,
        POST_REPLY_RATIO: 0.3,
        MAX_POST_REPLIES_PER_RUN: 1,
        MAX_COMMENT_REPLIES_PER_RUN: 2
    });

    // Test States
    const [testingReddit, setTestingReddit] = useState(false);
    const [redditTestResult, setRedditTestResult] = useState<{ success: boolean; message: string } | null>(null);

    const [testingGemini, setTestingGemini] = useState(false);
    const [geminiTestResult, setGeminiTestResult] = useState<{ success: boolean; message: string } | null>(null);

    const [testingSlack, setTestingSlack] = useState(false);
    const [slackTestResult, setSlackTestResult] = useState<{ success: boolean; message: string } | null>(null);

    const [testingTelegram, setTestingTelegram] = useState(false);
    const [telegramTestResult, setTelegramTestResult] = useState<{ success: boolean; message: string } | null>(null);

    // Status State
    const [isConfigured, setIsConfigured] = useState(false);
    const API_BASE = 'http://localhost:8000';

    useEffect(() => {
        // Check if already configured
        fetch(`${API_BASE}/api/setup/status`)
            .then(res => res.json())
            .then(data => {
                if (data.is_configured) {
                    setIsConfigured(true);
                }
            })
            .catch(err => console.error("Failed to check status", err));
    }, []);

    const handleInputChange = (field: string, value: string | number) => {
        setConfig(prev => ({ ...prev, [field]: value }));
    };

    if (isConfigured) {
        return (
            <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
                <Card className="w-full max-w-md text-center">
                    <CardHeader>
                        <div className="mx-auto w-12 h-12 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4">
                            <Check className="w-6 h-6" />
                        </div>
                        <CardTitle className="text-xl">Setup Already Complete</CardTitle>
                        <CardDescription>
                            The application has already been configured. You can modify settings in the admin dashboard.
                        </CardDescription>
                    </CardHeader>
                    <CardFooter className="flex justify-center">
                        <Button onClick={() => window.location.href = '/admin/login'}>
                            Go to Admin Login
                        </Button>
                    </CardFooter>
                </Card>
            </div>
        );
    }

    // API Callers (Mocked for now, needs proxy setup)

    const testReddit = async () => {
        setTestingReddit(true);
        setRedditTestResult(null);
        try {
            const response = await fetch(`${API_BASE}/api/setup/test-reddit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    client_id: config.REDDIT_CLIENT_ID,
                    client_secret: config.REDDIT_CLIENT_SECRET,
                    username: config.REDDIT_USERNAME,
                    password: config.REDDIT_PASSWORD,
                    user_agent: config.REDDIT_USER_AGENT
                })
            });
            const data = await response.json();
            if (data.success) {
                setRedditTestResult({ success: true, message: `Connected as u/${data.username} (${data.karma} karma)` });
            } else {
                setRedditTestResult({ success: false, message: data.error });
            }
        } catch (error: any) {
            setRedditTestResult({ success: false, message: error.message });
        } finally {
            setTestingReddit(false);
        }
    };

    const testGemini = async () => {
        setTestingGemini(true);
        setGeminiTestResult(null);
        try {
            const response = await fetch(`${API_BASE}/api/setup/test-gemini`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: config.GEMINI_API_KEY })
            });
            const data = await response.json();
            if (data.success) {
                setGeminiTestResult({ success: true, message: 'Gemini API key is valid' });
            } else {
                setGeminiTestResult({ success: false, message: data.error });
            }
        } catch (error: any) {
            setGeminiTestResult({ success: false, message: error.message });
        } finally {
            setTestingGemini(false);
        }
    };

    const testSlack = async () => {
        setTestingSlack(true);
        setSlackTestResult(null);
        try {
            const response = await fetch(`${API_BASE}/api/setup/test-slack`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ webhook_url: config.SLACK_WEBHOOK_URL })
            });
            const data = await response.json();
            if (data.success) {
                setSlackTestResult({ success: true, message: 'Test message sent to Slack' });
            } else {
                setSlackTestResult({ success: false, message: data.error });
            }
        } catch (error: any) {
            setSlackTestResult({ success: false, message: error.message });
        } finally {
            setTestingSlack(false);
        }
    };

    const testTelegram = async () => {
        setTestingTelegram(true);
        setTelegramTestResult(null);
        try {
            const response = await fetch(`${API_BASE}/api/setup/test-telegram`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    bot_token: config.TELEGRAM_BOT_TOKEN,
                    chat_id: config.TELEGRAM_CHAT_ID
                })
            });
            const data = await response.json();
            if (data.success) {
                setTelegramTestResult({ success: true, message: 'Test message sent to Telegram' });
            } else {
                setTelegramTestResult({ success: false, message: data.error });
            }
        } catch (error: any) {
            setTelegramTestResult({ success: false, message: error.message });
        } finally {
            setTestingTelegram(false);
        }
    };

    const completeSetup = async () => {
        setCompleting(true);
        setSetupError('');
        try {
            const response = await fetch(`${API_BASE}/api/setup/complete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            const data = await response.json();
            if (data.success) {
                setCurrentStep(5);
                if (!data.migrations_success) {
                    setSetupError(data.migrations_message);
                }
            } else {
                setSetupError(data.error);
            }
        } catch (error: any) {
            setSetupError(error.message);
        } finally {
            setCompleting(false);
        }
    };

    const canProceed = () => {
        if (currentStep === 1) {
            return !!(config.REDDIT_CLIENT_ID && config.REDDIT_CLIENT_SECRET && config.REDDIT_USERNAME && config.REDDIT_PASSWORD && config.REDDIT_USER_AGENT && config.ALLOWED_SUBREDDITS && redditTestResult?.success);
        }
        if (currentStep === 2) {
            return !!(config.GEMINI_API_KEY || config.OPENAI_API_KEY || config.ANTHROPIC_API_KEY);
        }
        if (currentStep === 3) {
            return !!(config.NOTIFICATION_TYPE && config.PUBLIC_URL && (
                (config.NOTIFICATION_TYPE === 'slack' && config.SLACK_WEBHOOK_URL) ||
                (config.NOTIFICATION_TYPE === 'telegram' && config.TELEGRAM_BOT_TOKEN && config.TELEGRAM_CHAT_ID) ||
                (config.NOTIFICATION_TYPE === 'webhook' && config.WEBHOOK_URL)
            ));
        }
        return true;
    };

    const steps = [
        { id: 1, title: 'Reddit API' },
        { id: 2, title: 'LLM Keys' },
        { id: 3, title: 'Notifications' },
        { id: 4, title: 'Safety Limits' }
    ];

    return (
        <div className="min-h-screen bg-background flex flex-col items-center py-10 px-4">
            <div className="text-center mb-8">
                <h1 className="text-3xl font-bold tracking-tight text-foreground">Reddit Agent Setup</h1>
                <p className="text-gray-500 mt-2">Configure your agent in 4 easy steps</p>
            </div>

            {/* Progress Steps */}
            <div className="w-full max-w-3xl mb-10">
                <div className="relative flex justify-between">
                    <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-200 -z-10 -translate-y-1/2 rounded" />
                    {steps.map((step) => (
                        <div key={step.id} className="flex flex-col items-center bg-background px-2">
                            <div
                                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors duration-200 
                  ${currentStep >= step.id ? 'bg-primary border-primary text-white' : 'bg-white border-gray-300 text-gray-400'}`}
                            >
                                {currentStep > step.id ? <Check className="w-5 h-5" /> : step.id}
                            </div>
                            <span className={`text-xs mt-2 font-medium ${currentStep >= step.id ? 'text-foreground' : 'text-muted-foreground'}`}>
                                {step.title}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            <Card className="w-full max-w-2xl shadow-lg border-0 ring-1 ring-gray-200">
                <CardHeader>
                    <CardTitle className="text-2xl">
                        {currentStep === 1 && 'Reddit API Credentials'}
                        {currentStep === 2 && 'LLM API Keys'}
                        {currentStep === 3 && 'Notification Settings'}
                        {currentStep === 4 && 'Safety Limits'}
                        {currentStep === 5 && 'Setup Complete!'}
                    </CardTitle>
                    <CardDescription>
                        {currentStep === 1 && 'Enter your Reddit App credentials defined in reddit.com/prefs/apps'}
                        {currentStep === 2 && 'Configure at least one LLM provider.'}
                        {currentStep === 3 && 'How should the agent notify you for approvals?'}
                        {currentStep === 4 && 'Define operational boundaries to prevent bans.'}
                        {currentStep === 5 && 'Your agent is ready to run.'}
                    </CardDescription>
                </CardHeader>

                <CardContent className="space-y-6">
                    {/* Step 1: Reddit */}
                    {currentStep === 1 && (
                        <div className="space-y-4">
                            <div className="grid gap-2">
                                <Label htmlFor="client_id">Client ID <span className="text-red-500">*</span></Label>
                                <Input id="client_id" value={config.REDDIT_CLIENT_ID} onChange={(e) => handleInputChange('REDDIT_CLIENT_ID', e.target.value)} placeholder="Enter Client ID" />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="client_secret">Client Secret <span className="text-red-500">*</span></Label>
                                <Input id="client_secret" type="password" value={config.REDDIT_CLIENT_SECRET} onChange={(e) => handleInputChange('REDDIT_CLIENT_SECRET', e.target.value)} placeholder="Enter Client Secret" />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="username">Username <span className="text-red-500">*</span></Label>
                                <Input id="username" value={config.REDDIT_USERNAME} onChange={(e) => handleInputChange('REDDIT_USERNAME', e.target.value)} placeholder="Reddit Username" />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="password">Password <span className="text-red-500">*</span></Label>
                                <Input id="password" type="password" value={config.REDDIT_PASSWORD} onChange={(e) => handleInputChange('REDDIT_PASSWORD', e.target.value)} placeholder="Reddit Password" />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="user_agent">User Agent <span className="text-red-500">*</span></Label>
                                <Input id="user_agent" value={config.REDDIT_USER_AGENT} onChange={(e) => handleInputChange('REDDIT_USER_AGENT', e.target.value)} placeholder="android:com.app.id:v1.0 (by /u/username)" />
                                <p className="text-xs text-muted-foreground">Format: platform:appname:version (by /u/username)</p>
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="subreddits">Allowed Subreddits <span className="text-red-500">*</span></Label>
                                <Input id="subreddits" value={config.ALLOWED_SUBREDDITS} onChange={(e) => handleInputChange('ALLOWED_SUBREDDITS', e.target.value)} placeholder="technology, python, ai" />
                            </div>

                            <div className="pt-2">
                                <Button variant="outline" onClick={testReddit} disabled={testingReddit} className="w-full">
                                    {testingReddit && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                    {testingReddit ? 'Testing Connection...' : 'Test Connection'}
                                </Button>
                                {redditTestResult && (
                                    <Alert className={`mt-4 ${redditTestResult.success ? 'bg-green-50 text-green-900 border-green-200' : 'bg-red-50 text-red-900 border-red-200'}`}>
                                        <AlertTitle>{redditTestResult.success ? 'Success' : 'Error'}</AlertTitle>
                                        <AlertDescription>{redditTestResult.message}</AlertDescription>
                                    </Alert>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Step 2: LLM */}
                    {currentStep === 2 && (
                        <div className="space-y-4">
                            <div className="grid gap-2">
                                <Label htmlFor="gemini">Gemini API Key (Recommended)</Label>
                                <div className="flex gap-2">
                                    <Input id="gemini" type="password" value={config.GEMINI_API_KEY} onChange={(e) => handleInputChange('GEMINI_API_KEY', e.target.value)} placeholder="Enter Gemini Key" className="flex-1" />
                                    <Button variant="outline" onClick={testGemini} disabled={!config.GEMINI_API_KEY || testingGemini}>
                                        {testingGemini ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Test'}
                                    </Button>
                                </div>
                                {geminiTestResult && (
                                    <p className={`text-sm ${geminiTestResult.success ? 'text-green-600' : 'text-red-600'}`}>{geminiTestResult.message}</p>
                                )}
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="openai">OpenAI API Key (Optional)</Label>
                                <Input id="openai" type="password" value={config.OPENAI_API_KEY} onChange={(e) => handleInputChange('OPENAI_API_KEY', e.target.value)} placeholder="sk-..." />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="anthropic">Anthropic API Key (Optional)</Label>
                                <Input id="anthropic" type="password" value={config.ANTHROPIC_API_KEY} onChange={(e) => handleInputChange('ANTHROPIC_API_KEY', e.target.value)} placeholder="sk-ant-..." />
                            </div>
                        </div>
                    )}

                    {/* Step 3: Notifications */}
                    {currentStep === 3 && (
                        <div className="space-y-4">
                            <div className="grid gap-2">
                                <Label>Notification Type <span className="text-red-500">*</span></Label>
                                <Select value={config.NOTIFICATION_TYPE} onValueChange={(val) => handleInputChange('NOTIFICATION_TYPE', val)}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select type" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="slack">Slack</SelectItem>
                                        <SelectItem value="telegram">Telegram</SelectItem>
                                        <SelectItem value="webhook">Webhook</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            {config.NOTIFICATION_TYPE === 'slack' && (
                                <div className="space-y-4 border-l-2 border-slate-200 pl-4">
                                    <div className="grid gap-2">
                                        <Label htmlFor="slack_url">Slack Webhook URL <span className="text-red-500">*</span></Label>
                                        <Input id="slack_url" value={config.SLACK_WEBHOOK_URL} onChange={(e) => handleInputChange('SLACK_WEBHOOK_URL', e.target.value)} placeholder="https://hooks.slack.com/..." />
                                    </div>
                                    <Button variant="outline" size="sm" onClick={testSlack} disabled={!config.SLACK_WEBHOOK_URL || testingSlack}>
                                        {testingSlack ? 'Testing...' : 'Test Slack'}
                                    </Button>
                                    {slackTestResult && (
                                        <p className={`text-sm ${slackTestResult.success ? 'text-green-600' : 'text-red-600'}`}>{slackTestResult.message}</p>
                                    )}
                                </div>
                            )}

                            {config.NOTIFICATION_TYPE === 'telegram' && (
                                <div className="space-y-4 border-l-2 border-slate-200 pl-4">
                                    <div className="grid gap-2">
                                        <Label htmlFor="tg_token">Bot Token <span className="text-red-500">*</span></Label>
                                        <Input id="tg_token" type="password" value={config.TELEGRAM_BOT_TOKEN} onChange={(e) => handleInputChange('TELEGRAM_BOT_TOKEN', e.target.value)} placeholder="123456:ABC..." />
                                    </div>
                                    <div className="grid gap-2">
                                        <Label htmlFor="tg_chat">Chat ID <span className="text-red-500">*</span></Label>
                                        <Input id="tg_chat" value={config.TELEGRAM_CHAT_ID} onChange={(e) => handleInputChange('TELEGRAM_CHAT_ID', e.target.value)} placeholder="12345678" />
                                    </div>
                                    <Button variant="outline" size="sm" onClick={testTelegram} disabled={!config.TELEGRAM_BOT_TOKEN || !config.TELEGRAM_CHAT_ID || testingTelegram}>
                                        {testingTelegram ? 'Testing...' : 'Test Telegram'}
                                    </Button>
                                    {telegramTestResult && (
                                        <p className={`text-sm ${telegramTestResult.success ? 'text-green-600' : 'text-red-600'}`}>{telegramTestResult.message}</p>
                                    )}
                                </div>
                            )}

                            {config.NOTIFICATION_TYPE === 'webhook' && (
                                <div className="space-y-4 border-l-2 border-slate-200 pl-4">
                                    <div className="grid gap-2">
                                        <Label htmlFor="webhook_url">Webhook URL <span className="text-red-500">*</span></Label>
                                        <Input id="webhook_url" value={config.WEBHOOK_URL} onChange={(e) => handleInputChange('WEBHOOK_URL', e.target.value)} placeholder="https://..." />
                                    </div>
                                </div>
                            )}

                            <div className="grid gap-2 pt-2">
                                <Label htmlFor="public_url">Public URL <span className="text-red-500">*</span></Label>
                                <Input id="public_url" value={config.PUBLIC_URL} onChange={(e) => handleInputChange('PUBLIC_URL', e.target.value)} placeholder="https://your-public-url.com" />
                                <p className="text-xs text-muted-foreground">Required for approval callbacks (e.g. ngrok)</p>
                            </div>
                        </div>
                    )}

                    {/* Step 4: Safety Limits */}
                    {currentStep === 4 && (
                        <div className="grid gap-4 sm:grid-cols-2">
                            <div className="grid gap-2">
                                <Label htmlFor="max_daily">Max Comments / Day</Label>
                                <Input type="number" id="max_daily" value={config.MAX_COMMENTS_PER_DAY} onChange={(e) => handleInputChange('MAX_COMMENTS_PER_DAY', parseInt(e.target.value))} />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="max_run">Max Comments / Run</Label>
                                <Input type="number" id="max_run" value={config.MAX_COMMENTS_PER_RUN} onChange={(e) => handleInputChange('MAX_COMMENTS_PER_RUN', parseInt(e.target.value))} />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="shadowban">Risk Threshold (0-1)</Label>
                                <Input type="number" step="0.1" id="shadowban" value={config.SHADOWBAN_RISK_THRESHOLD} onChange={(e) => handleInputChange('SHADOWBAN_RISK_THRESHOLD', parseFloat(e.target.value))} />
                            </div>
                            <div className="grid gap-2">
                                <Label htmlFor="cooldown">Cooldown (Hours)</Label>
                                <Input type="number" id="cooldown" value={config.COOLDOWN_PERIOD_HOURS} onChange={(e) => handleInputChange('COOLDOWN_PERIOD_HOURS', parseInt(e.target.value))} />
                            </div>
                        </div>
                    )}

                    {/* Success Step */}
                    {currentStep === 5 && (
                        <div className="flex flex-col items-center justify-center py-6 text-center space-y-4">
                            <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4">
                                <Check className="w-8 h-8" />
                            </div>
                            <p className="text-lg text-gray-600">Your Reddit engagement agent is now configured.</p>

                            {setupError && (
                                <Alert variant="destructive">
                                    <AlertCircle className="h-4 w-4" />
                                    <AlertTitle>Warning</AlertTitle>
                                    <AlertDescription>{setupError}</AlertDescription>
                                </Alert>
                            )}

                            <div className="bg-slate-50 p-4 rounded-lg text-left w-full text-sm space-y-2 border border-slate-200">
                                <p className="font-semibold">Next Steps:</p>
                                <ol className="list-decimal pl-4 space-y-1 text-gray-600">
                                    <li>Set admin password in <code>.env</code> (ADMIN_PASSWORD_HASH)</li>
                                    <li>Start server: <code>python main.py server</code></li>
                                    <li>Run agent: <code>python main.py run --once</code></li>
                                </ol>
                            </div>
                        </div>
                    )}
                </CardContent>

                <CardFooter className="flex justify-between pt-6 border-t border-gray-100">
                    {currentStep < 5 && (
                        <>
                            <Button variant="ghost" onClick={() => setCurrentStep(prev => Math.max(1, prev - 1))} disabled={currentStep === 1}>
                                <ChevronLeft className="w-4 h-4 mr-2" /> Back
                            </Button>
                            <Button onClick={() => currentStep === 4 ? completeSetup() : setCurrentStep(prev => prev + 1)} disabled={!canProceed() || completing}>
                                {completing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                                {currentStep === 4 ? 'Complete Setup' : 'Next'}
                                {!completing && currentStep < 4 && <ChevronRight className="w-4 h-4 ml-2" />}
                            </Button>
                        </>
                    )}
                    {currentStep === 5 && (
                        <Button className="w-full" onClick={() => window.location.href = '/admin/login'}>
                            Go to Admin Login
                        </Button>
                    )}
                </CardFooter>
            </Card>
        </div>
    );
}
