import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import MCPServerAdapter

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# Define MCP server parameters
MCP_SERVERS = [
    {
        "outlook-mcp-server": {
            "command": "uv",
            "args": [
                "--directory",
                "/Users/koushald/OutlookForMac-mcp-server/src/OutlookForMac-mcp-server",
                "run",
                "outlook_mcp.py"
            ],
            "env": {
                "USER_EMAIL": "koushald@amazon.ae",
                "OUTLOOK_MCP_LOG_LEVEL": "INFO"
            }
        }
    },
    {
        "apple-reminders": {
            "args": [],
            "command": "mcp-server-apple-reminders"
        }
    }
]

@CrewBase
class EmailScan():
    """EmailScan crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = '/Users/koushald/email_scan/src/email_scan/config/agents.yaml'
    tasks_config = '/Users/koushald/email_scan/src/email_scan/config/tasks.yaml'
    
    def __init__(self):
        self.aggregated_tools = []
        try:
            # Try to connect to MCP servers
            self.aggregated_tools = self._setup_mcp_tools()
            if self.aggregated_tools:
                print(f"Available aggregated tools: {[tool.name for tool in self.aggregated_tools]}")
        except Exception as e:
            print(f"Error connecting to or using multiple MCP servers (Managed): {e}")
            print("Ensure all MCP servers are running and accessible with correct configurations.")
            print("Continuing without MCP tools...")
    
    def _setup_mcp_tools(self):
        """Set up MCP tools for email and reminders"""
        try:
            # Import required modules
            from mcp import StdioServerParameters
            
            # Create MCP server adapter
            with MCPServerAdapter(MCP_SERVERS) as tools:
                return tools
        except ImportError:
            print("MCP package not available. Installing...")
            try:
                import subprocess
                subprocess.check_call(["pip", "install", "mcp"])
                from mcp import StdioServerParameters
                with MCPServerAdapter(MCP_SERVERS) as tools:
                    return tools
            except Exception as e:
                print(f"Failed to set up MCP tools: {e}")
                return []

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def email_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['email_reviewer'],
            tools=self.aggregated_tools,
            verbose=True
        )

    @agent
    def actions_updater(self) -> Agent:
        return Agent(
            config=self.agents_config['actions_updater'],
            tools=self.aggregated_tools,
            verbose=True
        )

    # To learn more about structured task outputs, 
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def email_review_task(self) -> Task:
        return Task(
            config=self.tasks_config['email_review_task'],
        )

    @task
    def reminder_creation_task(self) -> Task:
        email_task = self.email_review_task()
        return Task(
            config=self.tasks_config['reminder_creation_task'],
            output_file='report.md',
            context=[email_task]  # Add context from the first task
        )

    @crew
    def crew(self) -> Crew:
        """Creates the EmailScan crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        
        # Import Bedrock for LLM
        import boto3
        from langchain_aws import BedrockLLM
               
        # Create Bedrock LLM
        llm = LLM(
            provider="bedrock",
            model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            config={
                "region_name": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
                "credentials_profile_name": None,  # Use environment variables
            }
        )

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            llm=llm,  # Specify the LLM to use
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )