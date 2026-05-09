"""LLM prompt templates for all agents.

Source of truth for every prompt used in the system.
Imported from here — never hardcoded in agent files.
See .agent/PROMPTS.md for documentation and versioning.
"""

# ============================================================
# Planner Agent
# ============================================================

PLANNER_DECOMPOSE_QUERY: str = """You are a research planning assistant.

Given a research topic, your job is to decompose it into 3-5 specific,
searchable sub-topics that will help retrieve relevant academic papers.

Each sub-topic should be:
- Specific enough to return focused results
- Different enough from the others to maximize coverage
- Phrased as a short search query (2-6 words)

Research topic: {query}

Respond ONLY with a JSON array of strings. No explanation, no markdown.
Example: ["autonomous AI agents", "LLM tool use", "agent memory systems"]"""


# ============================================================
# Search Agent
# ============================================================

SEARCH_REFINE_QUERY: str = """You are an academic search specialist.

Given the following search query and a list of paper abstracts,
determine which papers are most relevant to the original research topic.

Original topic: {original_topic}
Search query used: {search_query}

Papers found:
{paper_list}

Return the indices of the top {top_n} most relevant papers as a JSON array.
Example: [0, 2, 4]
Respond with ONLY the JSON array."""


# ============================================================
# Analysis Agent
# ============================================================

ANALYSIS_SUMMARIZE_PAPER: str = """You are an expert research analyst. Analyze the following research paper
and extract structured information.

Paper title: {title}
Paper content:
{content}

Return a JSON object with exactly these fields:
{{
  "summary": "2-3 sentence plain English summary",
  "methodology": "What approach/technique did the authors use?",
  "datasets": "What datasets or benchmarks were used? (list or 'Not specified')",
  "key_findings": "What are the 2-3 most important findings?",
  "limitations": "What limitations do the authors acknowledge?",
  "contribution": "What is the novel contribution of this paper?"
}}

Respond with ONLY the JSON object. No explanation, no markdown fences."""

ANALYSIS_COMPARE_PAPERS: str = """You are a research analyst comparing multiple academic papers.

Papers to compare:
{paper_summaries}

Analyze these papers and return a JSON object with:
{{
  "common_themes": ["theme1", "theme2"],
  "key_differences": ["difference1", "difference2"],
  "methodology_comparison": "A paragraph comparing the methodologies used",
  "strongest_paper": "Title of the most rigorous/impactful paper and why"
}}

Respond with ONLY the JSON object."""


# ============================================================
# Insight Agent
# ============================================================

INSIGHT_FIND_GAPS: str = """You are a senior research scientist identifying research gaps.

Below are summaries of {paper_count} papers on the topic: "{topic}"

Paper summaries:
{summaries}

Identify research gaps, contradictions, and future directions.
Return a JSON object with:
{{
  "research_gaps": [
    "Gap 1: description",
    "Gap 2: description"
  ],
  "contradictions": [
    "Contradiction between Paper A and Paper B: description"
  ],
  "trends": [
    "Trend 1: description"
  ],
  "future_directions": [
    "Direction 1: description",
    "Direction 2: description"
  ]
}}

Respond with ONLY the JSON object."""


# ============================================================
# Writer Agent
# ============================================================

WRITER_LITERATURE_REVIEW: str = """You are an academic writing assistant producing a literature review.

Topic: {topic}
Number of papers analyzed: {paper_count}

Research data:
- Paper summaries: {summaries}
- Comparison analysis: {comparison}
- Research gaps and insights: {insights}

Write a structured literature review with the following sections:

1. Introduction (2-3 paragraphs: context, scope, significance)
2. Overview of Research Landscape (group papers by theme/approach)
3. Methodology Comparison (compare approaches used across papers)
4. Key Findings and Contributions
5. Research Gaps and Contradictions
6. Future Research Directions
7. Conclusion

Writing style:
- Academic but readable
- Third person
- Cite papers by [Author et al., Year] format when referencing specific papers
- Each section 2-4 paragraphs

Do NOT use bullet points in the review body — use flowing prose."""

WRITER_PAPER_SUMMARY_SHORT: str = """Summarize the following research paper in 3 sentences for a general
technical audience. Focus on: what was done, how it was done, and
what the result was.

Title: {title}
Abstract: {abstract}
Key findings: {key_findings}

Respond with ONLY the 3-sentence summary. No labels, no formatting."""


# ============================================================
# Retrieval Agent
# ============================================================

RETRIEVAL_ANSWER_QUESTION: str = """You are a research assistant answering questions using retrieved paper excerpts.

Question: {question}

Relevant excerpts from research papers:
{context}

Answer the question based ONLY on the provided excerpts.
If the answer is not found in the excerpts, say "The retrieved papers do not
directly address this question."

Be specific, cite the paper titles when referencing specific information,
and keep the answer under 200 words."""
