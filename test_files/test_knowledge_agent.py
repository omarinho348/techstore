"""
test_knowledge_agent.py

Standalone test for the Knowledge Agent alone, per the PDF's suggested
approach: confirm one specialist works correctly before building the
rest. Run this directly (from anywhere, including test_files/):

    uv run python test_files/test_knowledge_agent.py

Delete this file once confirmed -- it's a debugging tool, not part of
the final application.
"""

import os
import sys

# This script lives in test_files/, one level below the project root,
# but imports project modules (agent_team.py) that live at the root.
# Insert the root into sys.path so the import works regardless of
# which directory the script is run from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import Runner

from agent_team import knowledge_agent

if __name__ == "__main__":
    result = Runner.run_sync(knowledge_agent, "What's your return policy?")
    print("Final output:", result.final_output)
    print("Handled by:", result.last_agent.name)