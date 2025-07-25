#!/usr/bin/env python3
"""
Richmond AI Agent CLI

A command-line interface for interacting with the Richmond AI Agent.
Supports both local testing and deployed API endpoint interactions.
"""

import asyncio
import json
import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import logging

import click
import httpx
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

from agent import RichmondAgent, RichmondAgentConfig, QueryRequest

# Initialize Rich console
console = Console()

# Default API endpoint (can be overridden)
DEFAULT_API_ENDPOINT = "https://your-api-gateway-url.amazonaws.com/prod"
# Set LOCAL_MODE_DEFAULT to True to run locally by default
LOCAL_MODE_DEFAULT = True

# CLI configuration
class CLIConfig:
    def __init__(self):
        self.api_endpoint = os.getenv('RICHMOND_AGENT_API', DEFAULT_API_ENDPOINT)
        self.timeout = 30
        self.local_mode = LOCAL_MODE_DEFAULT
        self.debug = False


@click.group()
@click.option('--api-endpoint', '-e', 
              default=None,
              help='API Gateway endpoint URL')
@click.option('--local', '-l', 
              is_flag=True, 
              help='Run in local mode (direct agent interaction)')
@click.option('--debug', '-d', 
              is_flag=True, 
              help='Enable debug logging')
@click.pass_context
def cli(ctx, api_endpoint, local, debug):
    """Richmond AI Agent CLI - Query Richmond-specific information using AI"""
    
    # Initialize CLI configuration
    config = CLIConfig()
    if api_endpoint:
        config.api_endpoint = api_endpoint
    # Override local mode if --local flag is provided
    if local:
        config.local_mode = True
    # If API endpoint is set to non-default, switch to API mode unless --local is explicit
    elif api_endpoint and api_endpoint != DEFAULT_API_ENDPOINT:
        config.local_mode = False
    config.debug = debug
    
    # Setup logging
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    
    # Store config in context
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    
    # Display banner
    if not ctx.invoked_subcommand:
        display_banner()


def display_banner():
    """Display CLI banner"""
    banner = """
[bold blue]Richmond AI Agent CLI[/bold blue]
[dim]MCP + Strands AI Agent Demo for Richmond, VA[/dim]

Query Richmond-specific information including:
• Tech meetups and events
• Local companies and startups  
• Venues and locations
• Community information

Type --help for available commands.
"""
    console.print(Panel(banner, border_style="blue"))


@cli.command()
@click.argument('query', required=False)
@click.option('--context', '-c', 
              help='Additional context as JSON string')
@click.option('--format', '-f', 
              type=click.Choice(['text', 'json', 'table']), 
              default='text',
              help='Output format')
@click.pass_context
def ask(ctx, query, context, format):
    """Ask the Richmond AI agent a question"""
    
    config = ctx.obj['config']
    
    # Get query if not provided
    if not query:
        query = Prompt.ask("[bold blue]What would you like to know about Richmond?[/bold blue]")
    
    # Parse context if provided
    context_dict = {}
    if context:
        try:
            context_dict = json.loads(context)
        except json.JSONDecodeError:
            console.print("[red]Error: Invalid JSON format for context[/red]")
            sys.exit(1)
    
    # Process query
    if config.local_mode:
        response = asyncio.run(process_local_query(query, context_dict))
    else:
        response = asyncio.run(process_api_query(config, query, context_dict))
    
    # Display response
    display_response(response, format)


@cli.command()
@click.pass_context
def health(ctx):
    """Check the health status of the agent"""
    
    config = ctx.obj['config']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking health status...", total=None)
        
        if config.local_mode:
            health_data = asyncio.run(check_local_health())
        else:
            health_data = asyncio.run(check_api_health(config))
    
    display_health_status(health_data)


@cli.command()
@click.pass_context
def interactive(ctx):
    """Start interactive chat session"""
    
    config = ctx.obj['config']
    
    console.print(Panel(
        "[bold green]Interactive Chat Mode[/bold green]\n"
        "Ask questions about Richmond, VA. Type 'quit', 'exit', or press Ctrl+C to end.",
        border_style="green"
    ))
    
    try:
        while True:
            query = Prompt.ask("\n[bold blue]You[/bold blue]")
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query.strip():
                continue
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Processing query...", total=None)
                
                if config.local_mode:
                    response = asyncio.run(process_local_query(query, {}))
                else:
                    response = asyncio.run(process_api_query(config, query, {}))
            
            # Display agent response
            if response.get('error'):
                console.print(f"[red]Agent: {response['error']}[/red]")
            else:
                console.print(f"[green]Agent:[/green] {response.get('response', 'No response')}")
                
                # Show tools used if any
                tools_used = response.get('tools_used', [])
                if tools_used:
                    console.print(f"[dim]Tools used: {', '.join(tools_used)}[/dim]")
    
    except KeyboardInterrupt:
        pass
    
    console.print("\n[dim]Goodbye![/dim]")


@cli.command()
@click.option('--endpoint', '-e', help='API endpoint to test')
@click.pass_context  
def test(ctx, endpoint):
    """Test the agent with sample queries"""
    
    config = ctx.obj['config']
    if endpoint:
        config.api_endpoint = endpoint
    
    test_queries = [
        "What's the next tech meetup in Richmond?",
        "Tell me about local Richmond tech companies",
        "What venues host events in Richmond?",
        "What's happening in the Richmond startup scene?"
    ]
    
    console.print(Panel(
        "[bold yellow]Running Test Queries[/bold yellow]\n"
        f"Mode: {'Local' if config.local_mode else 'API'}\n"
        f"Endpoint: {config.api_endpoint if not config.local_mode else 'Direct agent'}",
        border_style="yellow"
    ))
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        console.print(f"\n[bold blue]Test {i}/4:[/bold blue] {query}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing...", total=None)
            
            try:
                if config.local_mode:
                    response = asyncio.run(process_local_query(query, {}))
                else:
                    response = asyncio.run(process_api_query(config, query, {}))
                
                success = not response.get('error')
                results.append((query, success, response))
                
                if success:
                    console.print(f"[green]✓ Success[/green]")
                    console.print(f"Response: {response.get('response', '')[:100]}...")
                    if response.get('tools_used'):
                        console.print(f"Tools: {', '.join(response['tools_used'])}")
                else:
                    console.print(f"[red]✗ Failed: {response.get('error', 'Unknown error')}[/red]")
                    
            except Exception as e:
                console.print(f"[red]✗ Exception: {str(e)}[/red]")
                results.append((query, False, {"error": str(e)}))
    
    # Summary
    successful = sum(1 for _, success, _ in results if success)
    console.print(f"\n[bold]Test Results: {successful}/{len(test_queries)} successful[/bold]")


async def process_local_query(query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Process query using local agent"""
    try:
        config = RichmondAgentConfig()
        agent = RichmondAgent(config)
        agent.initialize()  # Not async
        
        request = QueryRequest(query=query, context=context)
        response = agent.process_query(request)  # Not async
        
        agent.cleanup()  # Not async
        return response.model_dump()
        
    except Exception as e:
        return {"error": str(e), "response": "", "tools_used": []}


async def process_api_query(config: CLIConfig, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Process query using API endpoint"""
    try:
        async with httpx.AsyncClient(timeout=config.timeout) as client:
            response = await client.post(
                f"{config.api_endpoint}/ask",
                json={"query": query, "context": context},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API error: {response.status_code} - {response.text}",
                    "response": "",
                    "tools_used": []
                }
                
    except Exception as e:
        return {"error": f"Connection error: {str(e)}", "response": "", "tools_used": []}


async def check_local_health() -> Dict[str, Any]:
    """Check local agent health"""
    try:
        config = RichmondAgentConfig()
        agent = RichmondAgent(config)
        agent.initialize()  # Not async
        
        health = agent.health_check()  # Not async
        agent.cleanup()  # Not async
        return health
        
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


async def check_api_health(config: CLIConfig) -> Dict[str, Any]:
    """Check API endpoint health"""
    try:
        async with httpx.AsyncClient(timeout=config.timeout) as client:
            response = await client.get(f"{config.api_endpoint}/health")
            
            if response.status_code in [200, 503]:
                return response.json()
            else:
                return {
                    "status": "unhealthy", 
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
    except Exception as e:
        return {"status": "unhealthy", "error": f"Connection error: {str(e)}"}


def display_response(response: Dict[str, Any], format: str):
    """Display agent response in specified format"""
    
    if format == 'json':
        console.print(Syntax(json.dumps(response, indent=2), "json"))
        return
    
    # Text format (default)
    if response.get('error'):
        console.print(Panel(
            f"[red]Error: {response['error']}[/red]",
            title="Agent Response",
            border_style="red"
        ))
        return
    
    agent_response = response.get('response', 'No response available')
    tools_used = response.get('tools_used', [])
    metadata = response.get('metadata', {})
    
    # Main response
    console.print(Panel(
        agent_response,
        title="[bold blue]Agent Response[/bold blue]",
        border_style="blue"
    ))
    
    # Additional info if available
    if tools_used or metadata:
        info_table = Table(title="Query Information")
        info_table.add_column("Field", style="cyan")
        info_table.add_column("Value", style="green")
        
        if tools_used:
            info_table.add_row("Tools Used", ", ".join(tools_used))
        
        if metadata.get('model'):
            info_table.add_row("Model", metadata['model'])
        
        if metadata.get('tokens_used'):
            info_table.add_row("Tokens Used", str(metadata['tokens_used']))
        
        if metadata.get('processing_time'):
            info_table.add_row("Processing Time", f"{metadata['processing_time']:.2f}s")
        
        console.print(info_table)


def display_health_status(health_data: Dict[str, Any]):
    """Display health status information"""
    
    status = health_data.get('status', 'unknown')
    components = health_data.get('components', {})
    
    # Status panel
    if status == 'healthy':
        status_color = "green"
        status_icon = "✓"
    elif status == 'degraded':
        status_color = "yellow"
        status_icon = "⚠"
    else:
        status_color = "red"
        status_icon = "✗"
    
    console.print(Panel(
        f"[{status_color}]{status_icon} Status: {status.upper()}[/{status_color}]",
        title="Health Check",
        border_style=status_color
    ))
    
    # Components table
    if components:
        table = Table(title="Component Status")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="white")
        
        for component, component_status in components.items():
            if 'healthy' in component_status:
                status_style = "green"
            elif 'unhealthy' in component_status:
                status_style = "red"
            else:
                status_style = "yellow"
            
            table.add_row(component, f"[{status_style}]{component_status}[/{status_style}]")
        
        console.print(table)
    
    # Error information
    if health_data.get('error'):
        console.print(Panel(
            f"[red]{health_data['error']}[/red]",
            title="Error Details",
            border_style="red"
        ))


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted by user[/dim]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)