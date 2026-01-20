"""
Workflow visualizer service.

Generates interactive SVG diagram of the 13-node LangGraph pipeline.
"""
from typing import Dict, List, Tuple


# Node metadata extracted from workflow/graph.py and workflow/nodes.py
NODE_METADATA = {
    "fetch_candidates": {
        "label": "Fetch Candidates",
        "description": "Fetch inbox replies (HIGH priority) and rising posts/comments from Reddit",
        "inputs": [],
        "outputs": ["post_candidates", "comment_candidates"],
        "node_type": "fetch"
    },
    "select_by_ratio": {
        "label": "Select by Ratio",
        "description": "Apply post/comment ratio distribution (30% posts, 70% comments)",
        "inputs": ["post_candidates", "comment_candidates"],
        "outputs": ["candidates"],
        "node_type": "filter"
    },
    "score_candidates": {
        "label": "Score Candidates",
        "description": "AI-powered 7-factor quality scoring (upvote ratio, karma, freshness, velocity, question signal, depth, historical)",
        "inputs": ["candidates"],
        "outputs": ["candidates with quality_score"],
        "node_type": "ai"
    },
    "filter_candidates": {
        "label": "Filter Candidates",
        "description": "Remove already-replied items and those in cooldown (6h inbox, 24h rising)",
        "inputs": ["candidates"],
        "outputs": ["candidates (filtered)"],
        "node_type": "filter"
    },
    "check_rules": {
        "label": "Check Rules",
        "description": "Verify subreddit compliance with allow-list",
        "inputs": ["candidates"],
        "outputs": ["candidates (compliant)"],
        "node_type": "filter"
    },
    "sort_by_score": {
        "label": "Sort by Score",
        "description": "Sort by (priority, quality_score) with 25% exploration randomization",
        "inputs": ["candidates"],
        "outputs": ["candidates (sorted)"],
        "node_type": "sort"
    },
    "diversity_select": {
        "label": "Diversity Select",
        "description": "Apply diversity limits (max 2/subreddit, max 1/post) with quality override (≥0.75)",
        "inputs": ["candidates"],
        "outputs": ["candidates (diverse)"],
        "node_type": "filter"
    },
    "check_daily_limit": {
        "label": "Check Daily Limit",
        "description": "Enforce ≤8 comments/day limit",
        "inputs": ["daily_stats"],
        "outputs": ["should_continue"],
        "node_type": "conditional"
    },
    "select_candidate": {
        "label": "Select Candidate",
        "description": "Pick next candidate from sorted list to process",
        "inputs": ["candidates"],
        "outputs": ["current_candidate"],
        "node_type": "conditional"
    },
    "build_context": {
        "label": "Build Context",
        "description": "Load vertical context chain (post + parent comments)",
        "inputs": ["current_candidate"],
        "outputs": ["context"],
        "node_type": "process"
    },
    "generate_draft": {
        "label": "Generate Draft",
        "description": "Generate reply with Gemini 2.5 Flash using persona templates",
        "inputs": ["context"],
        "outputs": ["draft"],
        "node_type": "ai"
    },
    "notify_human": {
        "label": "Notify Human",
        "description": "Send to Slack/Telegram for human-in-the-loop approval",
        "inputs": ["draft"],
        "outputs": ["approval_token"],
        "node_type": "notify"
    },
    "END": {
        "label": "End",
        "description": "Workflow complete",
        "inputs": [],
        "outputs": [],
        "node_type": "end"
    }
}

# Workflow edges (from workflow/graph.py)
EDGES = [
    ("fetch_candidates", "select_by_ratio", "linear"),
    ("select_by_ratio", "score_candidates", "linear"),
    ("score_candidates", "filter_candidates", "linear"),
    ("filter_candidates", "check_rules", "linear"),
    ("check_rules", "sort_by_score", "linear"),
    ("sort_by_score", "diversity_select", "linear"),
    ("diversity_select", "check_daily_limit", "linear"),
    ("check_daily_limit", "select_candidate", "conditional:continue"),
    ("check_daily_limit", "END", "conditional:end"),
    ("select_candidate", "build_context", "conditional:process"),
    ("select_candidate", "END", "conditional:end"),
    ("build_context", "generate_draft", "linear"),
    ("generate_draft", "notify_human", "linear"),
    ("notify_human", "check_daily_limit", "loop"),
]

# Node colors by type (warm palette)
NODE_COLORS = {
    "fetch": "#fef3c7",      # Warm yellow
    "filter": "#fed7aa",     # Warm orange light
    "sort": "#fde68a",       # Yellow
    "conditional": "#fca5a5",  # Warm red light
    "process": "#d1fae5",    # Green light
    "ai": "#dbeafe",         # Blue light
    "notify": "#e9d5ff",     # Purple light
    "end": "#e7e5e4"         # Gray
}

NODE_BORDER_COLORS = {
    "fetch": "#92400e",
    "filter": "#c2410c",
    "sort": "#ca8a04",
    "conditional": "#dc2626",
    "process": "#059669",
    "ai": "#2563eb",
    "notify": "#9333ea",
    "end": "#57534e"
}


class WorkflowVisualizer:
    """Generate interactive SVG diagram of the workflow."""

    def __init__(self):
        self.node_width = 180
        self.node_height = 60
        self.horizontal_spacing = 220
        self.vertical_spacing = 100
        self.margin = 40

    def generate_svg(self) -> str:
        """
        Generate complete SVG diagram.

        Returns:
            SVG string with embedded JavaScript for interactivity
        """
        # Calculate node positions (vertical flow)
        positions = self._calculate_positions()

        # Calculate SVG dimensions
        max_x = max(x for x, y in positions.values()) + self.node_width + self.margin
        max_y = max(y for x, y in positions.values()) + self.node_height + self.margin

        # Start SVG
        svg_parts = [
            f'<svg width="{max_x}" height="{max_y}" xmlns="http://www.w3.org/2000/svg" style="font-family: var(--font-sans, -apple-system, sans-serif);">',
            '<defs>',
            # Arrow marker for edges
            '<marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">',
            '<polygon points="0 0, 10 3, 0 6" fill="#d97706" />',
            '</marker>',
            # Conditional arrow marker (red)
            '<marker id="arrowhead-conditional" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">',
            '<polygon points="0 0, 10 3, 0 6" fill="#dc2626" />',
            '</marker>',
            # Loop arrow marker (purple)
            '<marker id="arrowhead-loop" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">',
            '<polygon points="0 0, 10 3, 0 6" fill="#9333ea" />',
            '</marker>',
            '</defs>',
        ]

        # Draw edges first (so they appear behind nodes)
        svg_parts.append(self._render_edges(positions))

        # Draw nodes
        svg_parts.append(self._render_nodes(positions))

        # End SVG
        svg_parts.append('</svg>')

        return '\n'.join(svg_parts)

    def _calculate_positions(self) -> Dict[str, Tuple[int, int]]:
        """
        Calculate (x, y) positions for each node in a vertical flow layout.

        Returns:
            Dict mapping node_id to (x, y) position
        """
        positions = {}

        # Vertical flow with conditional branches
        layout = [
            ["fetch_candidates"],
            ["select_by_ratio"],
            ["score_candidates"],
            ["filter_candidates"],
            ["check_rules"],
            ["sort_by_score"],
            ["diversity_select"],
            ["check_daily_limit"],
            ["select_candidate", "END"],  # Conditional split
            ["build_context"],
            ["generate_draft"],
            ["notify_human"],
        ]

        y = self.margin
        for row in layout:
            if len(row) == 1:
                # Single node - center it
                x = self.margin + 100
                positions[row[0]] = (x, y)
            else:
                # Multiple nodes - spread horizontally
                total_width = len(row) * self.node_width + (len(row) - 1) * 50
                start_x = self.margin + (400 - total_width) // 2
                for i, node in enumerate(row):
                    x = start_x + i * (self.node_width + 50)
                    positions[node] = (x, y)

            y += self.vertical_spacing

        return positions

    def _render_nodes(self, positions: Dict[str, Tuple[int, int]]) -> str:
        """Render all nodes as SVG rectangles."""
        parts = []

        for node_id, (x, y) in positions.items():
            metadata = NODE_METADATA.get(node_id, {})
            label = metadata.get("label", node_id)
            node_type = metadata.get("node_type", "process")
            description = metadata.get("description", "")

            fill_color = NODE_COLORS.get(node_type, "#e7e5e4")
            border_color = NODE_BORDER_COLORS.get(node_type, "#57534e")

            # Node rectangle with hover effect
            parts.append(
                f'<g class="workflow-node" data-node-id="{node_id}" '
                f'data-description="{description}" '
                f'style="cursor: pointer;">'
            )

            # Rectangle
            parts.append(
                f'<rect x="{x}" y="{y}" width="{self.node_width}" height="{self.node_height}" '
                f'fill="{fill_color}" stroke="{border_color}" stroke-width="2" rx="8" />'
            )

            # Label text (centered)
            text_x = x + self.node_width // 2
            text_y = y + self.node_height // 2 + 5
            parts.append(
                f'<text x="{text_x}" y="{text_y}" '
                f'text-anchor="middle" font-size="14" font-weight="600" fill="#292524">'
                f'{label}</text>'
            )

            parts.append('</g>')

        return '\n'.join(parts)

    def _render_edges(self, positions: Dict[str, Tuple[int, int]]) -> str:
        """Render all edges as SVG paths."""
        parts = []

        for from_node, to_node, edge_type in EDGES:
            if from_node not in positions or to_node not in positions:
                continue

            from_x, from_y = positions[from_node]
            to_x, to_y = positions[to_node]

            # Calculate start and end points
            start_x = from_x + self.node_width // 2
            start_y = from_y + self.node_height
            end_x = to_x + self.node_width // 2
            end_y = to_y

            # Determine edge color and marker
            if edge_type.startswith("conditional"):
                stroke_color = "#dc2626"
                marker = "arrowhead-conditional"
                stroke_dasharray = "5,5"
            elif edge_type == "loop":
                stroke_color = "#9333ea"
                marker = "arrowhead-loop"
                stroke_dasharray = "3,3"
            else:
                stroke_color = "#d97706"
                marker = "arrowhead"
                stroke_dasharray = "none"

            # Draw path
            if from_node == "notify_human" and to_node == "check_daily_limit":
                # Loop back - curved arrow
                control_x = start_x - 150
                control_y = (start_y + end_y) // 2
                path = f'M {start_x},{start_y} C {control_x},{start_y} {control_x},{end_y} {end_x},{end_y}'
            elif abs(start_x - end_x) > 50:
                # Horizontal offset - use curved path
                mid_y = (start_y + end_y) // 2
                path = f'M {start_x},{start_y} L {start_x},{mid_y} L {end_x},{mid_y} L {end_x},{end_y}'
            else:
                # Straight vertical line
                path = f'M {start_x},{start_y} L {end_x},{end_y}'

            parts.append(
                f'<path d="{path}" stroke="{stroke_color}" stroke-width="2" '
                f'fill="none" marker-end="url(#{marker})" stroke-dasharray="{stroke_dasharray}" />'
            )

            # Add edge label for conditional edges
            if edge_type.startswith("conditional:"):
                label = edge_type.split(":")[1]
                label_x = (start_x + end_x) // 2 + 10
                label_y = (start_y + end_y) // 2
                parts.append(
                    f'<text x="{label_x}" y="{label_y}" font-size="11" fill="#78716c" '
                    f'font-style="italic">{label}</text>'
                )

        return '\n'.join(parts)


def get_workflow_metadata() -> Dict:
    """
    Get workflow metadata for API responses.

    Returns:
        Dict with nodes and edges metadata
    """
    return {
        "nodes": NODE_METADATA,
        "edges": [
            {
                "from": from_node,
                "to": to_node,
                "type": edge_type
            }
            for from_node, to_node, edge_type in EDGES
        ],
        "total_nodes": len(NODE_METADATA) - 1,  # Exclude END
        "node_types": list(set(n["node_type"] for n in NODE_METADATA.values()))
    }
