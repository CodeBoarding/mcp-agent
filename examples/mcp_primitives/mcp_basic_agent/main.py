import asyncio
import time

from mcp_agent.app import MCPApp
from mcp_agent.config import (
    Settings,
    LoggerSettings,
    MCPSettings,
    MCPServerSettings,
    OpenAISettings,
)
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

settings = Settings(
    execution_engine="asyncio",
    logger=LoggerSettings(type="console", level="debug"),
    mcp=MCPSettings(
        servers={
            "demo_server": MCPServerSettings(
                command="uvx", args=["run", "demo_server.py"]
            )
        }
    ),
    openai=OpenAISettings(
        api_key="sk-my-openai-api-key",
        default_model="gpt-4o-mini",
    ),
)

# Settings can either be specified programmatically,
# or loaded from mcp_agent.config.yaml/mcp_agent.secrets.yaml
app = MCPApp(name="mcp_basic_agent")  # settings=settings)


async def example_usage():
    async with app.run() as agent_app:
        logger = agent_app.logger
        context = agent_app.context

        logger.info("Current config:", data=context.config.model_dump())

        # --- Example: Using the demo_server MCP server ---
        agent = Agent(
            name="agent",
            instruction="Demo agent for MCP resource and prompt primitives",
            server_names=["demo_server"],
        )

        async with agent:
            # List all resources from demo_server server
            resources = await agent.list_resources("demo_server")
            resource_uris = {
                resource.name: str(resource.uri) for resource in resources.resources
            }
            logger.info(
                "Resources available from demo_server:",
                data=resource_uris,
            )

            # List all prompts from demo_server server
            prompts = await agent.list_prompts("demo_server")
            logger.info(
                "Prompts available from demo_server:",
                data=prompts.model_dump(),
            )

            resource_messages = await agent.get_resource_messages(
                resource_uris["demo_server_get_readme"],
                "demo_server",
            )

            prompt_messages = await agent.get_prompt_messages(
                "demo_server_echo",
                {"message": "My name is John Doe."},
            )

            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            message = [
                "Summarise what are my prompts and resources?",
                *resource_messages,
                *prompt_messages,
            ]
            res = await llm.generate_str(message)
            logger.info(f"Summary: {res}")


if __name__ == "__main__":
    start = time.time()
    asyncio.run(example_usage())
    end = time.time()
    t = end - start

    print(f"Total run time: {t:.2f}s")
