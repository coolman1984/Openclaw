#!/bin/bash
# multi-agent-coding.sh - Multi-agent coding workflow using OpenCode Go

API_KEY="sk-yFM0tEe6Acx5OcFsczYnpRXSwwl3XNZf9FXy1meOircPD3NjdJInOl3n7kuKc528"
BASE_URL="https://opencode.ai/zen/go/v1/chat/completions"

# Parse response without jq
parse_response() {
    local response="$1"
    # Extract content from JSON response
    echo "$response" | grep -o '"content":"[^"]*"' | head -1 | sed 's/"content":"//;s/"$//' | sed 's/\\n/\n/g; s/\\t/\t/g; s/\\"/"/g'
}

# Agent: Architect (Kimi K2.5) - Planning and Design
architect() {
    local prompt="$1"
    echo "Calling Architect (Kimi K2.5)..." >&2
    
    response=$(curl -s -X POST "$BASE_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $API_KEY" \
        -d "{
            \"model\": \"kimi-k2.5\",
            \"messages\": [
                {\"role\": \"system\", \"content\": \"You are an expert Software Architect with 15+ years of experience. Your role is to analyze requirements, design system architecture, and create detailed implementation plans. Think step-by-step.\"},
                {\"role\": \"user\", \"content\": \"$prompt\"}
            ],
            \"max_tokens\": 2000
        }")
    
    parse_response "$response"
}

# Agent: Developer (GLM-5) - Writing Code
developer() {
    local prompt="$1"
    echo "Calling Developer (GLM-5)..." >&2
    
    response=$(curl -s -X POST "$BASE_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $API_KEY" \
        -d "{
            \"model\": \"glm-5\",
            \"messages\": [
                {\"role\": \"system\", \"content\": \"You are an Expert Senior Software Engineer. You write clean, maintainable, production-ready code with comprehensive error handling and clear comments. Follow best practices.\"},
                {\"role\": \"user\", \"content\": \"$prompt\"}
            ],
            \"max_tokens\": 3000
        }")
    
    parse_response "$response"
}

# Agent: Reviewer (MiniMax M2.7) - Code Review and Testing
reviewer() {
    local prompt="$1"
    echo "Calling Reviewer (MiniMax M2.7)..." >&2
    
    response=$(curl -s -X POST "$BASE_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $API_KEY" \
        -d "{
            \"model\": \"minimax-m2.7\",
            \"messages\": [
                {\"role\": \"system\", \"content\": \"You are a meticulous Code Reviewer. Identify bugs, security issues, and suggest improvements. Be thorough but constructive.\"},
                {\"role\": \"user\", \"content\": \"$prompt\"}
            ],
            \"max_tokens\": 2000
        }")
    
    parse_response "$response"
}

# Show usage
show_help() {
    echo "Multi-Agent Coding System using OpenCode Go"
    echo ""
    echo "Agents:"
    echo "  🏗️  Architect (Kimi K2.5)   - Planning & Design"
    echo "  👨‍💻 Developer (GLM-5)       - Writing Code"
    echo "  🔍 Reviewer (MiniMax M2.7)  - Review & Testing"
    echo ""
    echo "Usage:"
    echo "  architect <prompt>   - Ask the Architect agent"
    echo "  developer <prompt>   - Ask the Developer agent"
    echo "  reviewer <prompt>    - Ask the Reviewer agent"
    echo "  demo                 - Run a demo workflow"
    echo ""
    echo "Examples:"
    echo "  $0 architect 'Design a REST API for user authentication'"
    echo "  $0 developer 'Write a Python function to validate email addresses'"
    echo "  $0 reviewer 'Review this Python code for security issues: def login(user, pwd): ...'"
}

# Demo workflow
demo() {
    echo "🚀 MULTI-AGENT DEMO: Building a Task Manager CLI"
    echo "================================================"
    echo ""
    
    local task="Create a Python CLI task manager with argparse that can add tasks, list tasks, mark complete, and save to JSON"
    
    # Step 1: Architect
    echo "📋 STEP 1: Architect (Kimi K2.5) - Planning"
    echo "-------------------------------------------"
    plan=$(architect "Design a plan for: $task. Include: 1) File structure, 2) Core classes/functions, 3) CLI commands, 4) Data model")
    echo "$plan"
    echo ""
    
    # Step 2: Developer
    echo "💻 STEP 2: Developer (GLM-5) - Implementation"
    echo "---------------------------------------------"
    code=$(developer "Write complete Python code for a task manager CLI based on this plan: $plan")
    echo "$code"
    echo ""
    
    # Step 3: Reviewer
    echo "🔍 STEP 3: Reviewer (MiniMax M2.7) - Code Review"
    echo "------------------------------------------------"
    review=$(reviewer "Review this code for bugs, security issues, and improvements: $code")
    echo "$review"
    echo ""
    
    echo "✅ Demo complete!"
}

# Main
case "$1" in
    architect|a)
        shift
        architect "$*"
        ;;
    developer|d)
        shift
        developer "$*"
        ;;
    reviewer|r)
        shift
        reviewer "$*"
        ;;
    demo)
        demo
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        ;;
esac