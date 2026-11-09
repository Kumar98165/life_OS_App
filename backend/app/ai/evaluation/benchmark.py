"""LifeOS - Curated Evaluation & Benchmark Dataset (Step 9).

Contains synthetic, expert-crafted benchmark test cases covering the 9 core
LifeOS evaluation pillars. Completely isolated from private user data.
"""
import hashlib
import json
from typing import List, Dict, Any, Optional

BENCHMARK_VERSION = "v1.0.0-lifeos-bench"

# Canonical synthetic benchmark samples across 9 pillars
BENCHMARK_ITEMS: List[Dict[str, Any]] = [
    # 1. Daily Planning
    {
        "id": "bench-plan-001",
        "category": "daily_planning",
        "prompt": "Create a realistic daily plan for a working professional between 9:00 AM and 5:00 PM with focus blocks and lunch.",
        "expected_keywords": ["9:00", "lunch", "focus", "12:", "block"],
        "min_length_chars": 80,
        "required_structure": "schedule",
        "description": "Daily work schedule breakdown with lunch and focus blocks",
    },
    {
        "id": "bench-plan-002",
        "category": "daily_planning",
        "prompt": "I only have 30 minutes free today between meetings. Give me a 3-step decompression and quick triage routine.",
        "expected_keywords": ["1.", "2.", "3.", "minute"],
        "min_length_chars": 60,
        "required_structure": "numbered_list",
        "description": "Quick 30-minute decompression routine",
    },
    # 2. Task Management
    {
        "id": "bench-task-001",
        "category": "task_management",
        "prompt": "Prioritize these three tasks using the Eisenhower Matrix: 1. Server crash in production, 2. Quarterly strategy brainstorm, 3. Sorting inbox spam.",
        "expected_keywords": ["urgent", "important", "production", "crash", "spam"],
        "min_length_chars": 70,
        "required_structure": "prioritization",
        "description": "Eisenhower matrix task prioritization",
    },
    {
        "id": "bench-task-002",
        "category": "task_management",
        "prompt": "Break down the task 'File personal income taxes' into 4 sequential actionable subtasks.",
        "expected_keywords": ["1.", "2.", "3.", "4.", "document", "file"],
        "min_length_chars": 60,
        "required_structure": "numbered_list",
        "description": "Subtask decomposition for income taxes",
    },
    # 3. Goal Setting
    {
        "id": "bench-goal-001",
        "category": "goal_setting",
        "prompt": "Turn the vague goal 'I want to read more books' into a SMART goal with specific milestones.",
        "expected_keywords": ["specific", "measurable", "achievable", "realistic", "time", "month"],
        "min_length_chars": 80,
        "required_structure": "smart_goal",
        "description": "SMART goal transformation for reading",
    },
    {
        "id": "bench-goal-002",
        "category": "goal_setting",
        "prompt": "Define three milestones for a 6-month goal of running a 10K race.",
        "expected_keywords": ["milestone", "month", "km", "run"],
        "min_length_chars": 60,
        "required_structure": "milestones",
        "description": "10K race preparation milestones",
    },
    # 4. Habit Coaching
    {
        "id": "bench-habit-001",
        "category": "habit_coaching",
        "prompt": "I keep forgetting to drink water while working at my desk. Suggest a habit loop (cue, routine, reward) to build hydration.",
        "expected_keywords": ["cue", "routine", "reward", "water"],
        "min_length_chars": 60,
        "required_structure": "habit_loop",
        "description": "Habit loop design for hydration",
    },
    {
        "id": "bench-habit-002",
        "category": "habit_coaching",
        "prompt": "How can I restart my meditation habit after missing 4 consecutive days without feeling demotivated?",
        "expected_keywords": ["start small", "minute", "consistency", "forgive"],
        "min_length_chars": 60,
        "required_structure": "coaching",
        "description": "Habit recovery coaching after a streak break",
    },
    # 5. Productivity Assistance
    {
        "id": "bench-prod-001",
        "category": "productivity_assistance",
        "prompt": "Explain the Pomodoro Technique in 3 short bullet points, including work duration, short break, and long break.",
        "expected_keywords": ["25", "5", "break", "pomodoro", "minutes"],
        "min_length_chars": 50,
        "required_structure": "bullet_points",
        "description": "Pomodoro technique explanation with exact intervals",
    },
    # 6. Instruction Following
    {
        "id": "bench-instr-001",
        "category": "instruction_following",
        "prompt": "List exactly 3 benefits of deep work. Respond ONLY with a numbered list (1., 2., 3.). Do not include any introduction or conclusion text.",
        "expected_keywords": ["1.", "2.", "3."],
        "must_not_contain": ["here are", "in conclusion", "hope this helps", "certainly"],
        "min_length_chars": 30,
        "required_structure": "strict_numbered_list",
        "description": "Strict formatting with negative constraints",
    },
    # 7. Context Understanding
    {
        "id": "bench-ctx-001",
        "category": "context_understanding",
        "context": "User profile: Software developer, works from 10:00 to 18:00, avoids morning meetings, prefers asynchronous communication.",
        "prompt": "Based on my profile, when is the best time for me to schedule a 3-hour uninterrupted deep coding block?",
        "expected_keywords": ["morning", "10:00", "coding", "uninterrupted", "afternoon"],
        "min_length_chars": 40,
        "required_structure": "context_grounded",
        "description": "Contextual reasoning based on provided user work preferences",
    },
    # 8. Response Accuracy
    {
        "id": "bench-acc-001",
        "category": "response_accuracy",
        "prompt": "Is a task with high urgency and low importance classified as Quadrant 1, Quadrant 2, or Quadrant 3 in the Eisenhower Matrix?",
        "expected_keywords": ["quadrant 3", "q3", "delegate"],
        "min_length_chars": 20,
        "required_structure": "direct_answer",
        "description": "Factual classification in productivity theory",
    },
    # 9. Personalization
    {
        "id": "bench-pers-001",
        "category": "personalization",
        "context": "User Memory: Prefers concise answers under 50 words, tone is direct and analytical.",
        "prompt": "Give me a quick tip to beat afternoon energy slump.",
        "expected_keywords": ["water", "walk", "light", "protein", "stretch"],
        "max_words": 60,
        "min_length_chars": 20,
        "required_structure": "concise_direct",
        "description": "Personalized conciseness and tone adherence",
    },
]


class BenchmarkDataset:
    """Manages synthetic LifeOS benchmark suite and SHA-256 integrity."""

    @classmethod
    def get_version(cls) -> str:
        return BENCHMARK_VERSION

    @classmethod
    def get_all_items(cls) -> List[Dict[str, Any]]:
        return list(BENCHMARK_ITEMS)

    @classmethod
    def get_items_by_category(cls, category: str) -> List[Dict[str, Any]]:
        return [item for item in BENCHMARK_ITEMS if item.get("category") == category]

    @classmethod
    def compute_checksum(cls) -> str:
        """Compute deterministic SHA-256 digest of benchmark items."""
        serialized = json.dumps(BENCHMARK_ITEMS, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def validate_item_structure(cls, item: Dict[str, Any]) -> bool:
        """Check presence of mandatory keys."""
        required_keys = {"id", "category", "prompt", "expected_keywords", "min_length_chars"}
        return required_keys.issubset(set(item.keys()))

