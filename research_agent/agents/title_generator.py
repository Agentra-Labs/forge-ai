from agno.agent import Agent
from agno.models.aws import AwsBedrock

TITLE_SYSTEM_PROMPT = """You are a title generator for a research chat.
- Generate a short, descriptive title based on the user's message.
- The title should be less than 30 characters long.
- Do not use quotes, colons, or any punctuation.
- Output ONLY the plain text title, nothing else.
"""

title_generator = Agent(
    id="title-generator",
    name="Title Generator",
    model=AwsBedrock(id="amazon.nova-micro-v1:0"),
    instructions=TITLE_SYSTEM_PROMPT,
)
