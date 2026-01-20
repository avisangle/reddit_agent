# Reddit Agent Documentation Site

Static documentation site for the Reddit Comment Engagement Agent, built with Next.js and MDX.

## Features

- 📖 **Comprehensive Documentation** - Getting Started, Architecture, Features, Configuration, and FAQ
- 🎨 **Warm Minimalist Design** - Clean, readable interface with amber accents
- 🔍 **Syntax Highlighting** - Code blocks with GitHub Dark theme
- 📱 **Fully Responsive** - Works on desktop, tablet, and mobile
- ⚡ **Static Export** - Deploy anywhere (Vercel, Netlify, GitHub Pages)

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### Build for Production

```bash
# Build static site
npm run build

# Output in `out/` directory
```

### Preview Production Build

```bash
# After building
npx serve out
```

## Project Structure

```
reddit-agent-docs/
├── app/
│   ├── layout.tsx              # Root layout with navigation
│   ├── page.tsx                # Landing page
│   ├── globals.css             # Warm minimalist design system
│   ├── getting-started/
│   │   └── page.mdx            # Getting Started guide
│   ├── architecture/
│   │   └── page.mdx            # Architecture overview
│   ├── features/
│   │   └── page.mdx            # Features deep dive
│   ├── configuration/
│   │   └── page.mdx            # Configuration reference
│   └── faq/
│       └── page.mdx            # FAQ
├── next.config.ts              # Next.js config (static export)
├── mdx-components.tsx          # MDX configuration
└── package.json
```

## Documentation Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Overview and quick start |
| Getting Started | `/getting-started` | Installation and setup guide |
| Architecture | `/architecture` | 13-node workflow and system design |
| Features | `/features` | Quality scoring, diversity, etc. |
| Configuration | `/configuration` | Complete `.env` reference |
| FAQ | `/faq` | Common questions and troubleshooting |

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### GitHub Pages

```bash
# Build
npm run build

# Push `out/` directory to gh-pages branch
```

### Custom Server

```bash
# Build
npm run build

# Serve static files from `out/` directory
npx serve out
```

## Technologies

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **MDX** - Markdown with React components
- **rehype-highlight** - Code syntax highlighting
- **remark-gfm** - GitHub Flavored Markdown

## License

Private project - All rights reserved

---

**Part of**: Reddit Comment Engagement Agent v2.5
