#!/usr/bin/env python3
"""
Richmond AI Agent CLI Demo

A simple CLI for querying Richmond tech community information using AI.
"""
import click
import requests
import json
import os
from typing import Optional

API_BASE_URL = os.getenv('RICHMOND_API_URL', 'https://api.richmond-demo.aws.com')

@click.group()
@click.option('--api-url', help='Override API base URL')
@click.pass_context
def cli(ctx, api_url):
    """Richmond AI Agent CLI - Query Richmond tech community with AI"""
    ctx.ensure_object(dict)
    ctx.obj['api_url'] = api_url or API_BASE_URL

@cli.command()
@click.argument('query')
@click.option('--json-output', is_flag=True, help='Output raw JSON response')
@click.pass_context
def ask(ctx, query: str, json_output: bool):
    """Ask the AI agent about Richmond tech community"""
    
    try:
        response = requests.post(
            f"{ctx.obj['api_url']}/ask",
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        if json_output:
            click.echo(json.dumps(data, indent=2))
        else:
            if 'response' in data:
                click.echo(f"🤖 {data['response']}")
                
                if 'context' in data and data['context']:
                    click.echo(f"\n📊 Context: {data['context']}")
                    
                if 'sources' in data and data['sources']:
                    click.echo(f"\n📚 Sources: {', '.join(data['sources'])}")
            else:
                click.echo(f"❌ Unexpected response format: {data}")
                
    except requests.exceptions.RequestException as e:
        click.echo(f"❌ API Error: {e}", err=True)
        exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"❌ JSON Error: {e}", err=True)
        exit(1)

@cli.command()
@click.pass_context
def health(ctx):
    """Check API health status"""
    try:
        response = requests.get(f"{ctx.obj['api_url']}/health", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        status = "🟢" if data.get('status') == 'healthy' else "🔴"
        click.echo(f"{status} API Status: {data.get('status', 'unknown')}")
        
        if 'timestamp' in data:
            click.echo(f"⏰ Last check: {data['timestamp']}")
            
    except Exception as e:
        click.echo(f"🔴 API Health Check Failed: {e}", err=True)

@cli.command()
@click.pass_context
def demo(ctx):
    """Run interactive demo with sample queries"""
    
    sample_queries = [
        "What's the next tech meetup in Richmond?",
        "Tell me about the Richmond Python group",
        "What companies are hiring in Richmond?",
        "Where can I find AWS events this month?",
        "Tell me about the Richmond tech scene"
    ]
    
    click.echo("🎯 Richmond AI Agent Demo")
    click.echo("=" * 40)
    
    for i, query in enumerate(sample_queries, 1):
        click.echo(f"\n{i}. Query: {query}")
        click.echo("-" * 50)
        
        ctx.invoke(ask, query=query)
        
        if i < len(sample_queries):
            click.confirm("\nContinue to next query?", abort=True)

if __name__ == '__main__':
    cli()