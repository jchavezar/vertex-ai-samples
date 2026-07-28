# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import google.auth

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import google_search
from google.genai import types

# Set up standard Google Cloud Project environments
try:
    _, auth_project_id = google.auth.default()
except Exception:
    auth_project_id = None

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or auth_project_id
if project_id:
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get("GOOGLE_CLOUD_LOCATION") or "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

# Expert system instruction for the World Cup sports analytics agent
WORLD_CUP_ANALYTICS_INSTRUCTION = """You are an elite, highly knowledgeable World Cup Statistics and Sports Analytics assistant. 
Your objective is to provide precise, deeply analytical, and up-to-date information regarding FIFA World Cup tournaments (both Men's and Women's, historical and current/upcoming events).

Key Guidelines:
1. Ground your answers using the built-in Google Search grounding tool. Always seek the latest and most accurate data for match results, team rosters, manager changes, schedules, group standings, player stats, and historic milestones.
2. Present complex statistical data, group standings, tournament brackets, or match history using cleanly formatted Markdown tables.
3. Keep your tone professional, analytical, objective, and engaging for soccer enthusiasts and sports analysts.
4. When comparing teams or players, provide key metrics such as goals scored, clean sheets, expected goals (xG) if available, possession percentages, and tactical formations.
5. Provide citations or sources when detailing major controversies, historical records, or disputable statistics.
"""

root_agent = Agent(
    name="worldcup_analytics_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=WORLD_CUP_ANALYTICS_INSTRUCTION,
    tools=[google_search],
)

app = App(
    root_agent=root_agent,
    name="app",
)
