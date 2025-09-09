# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains a Claude Code configuration setup and a WhatsApp Chat Analyzer MVP - a Python application that analyzes WhatsApp conversations from multiple perspectives (linguistic, psychological, communication consultant, and relationship coaching).

## Project Structure

### Configuration Files
- `.claude/settings.local.json` - Local permissions configuration allowing Python and mkdir bash commands
- `.claude/agents/spare-parts-quote-requester.md` - Custom agent for procurement and spare parts quote requests

### Application Files
- `app.py` - Streamlit web dashboard (main interface)
- `whatsapp_analyzer.py` - Core chat analysis engine with statistical analysis
- `ai_analyzer.py` - Enhanced analysis using OpenAI API for deeper insights
- `visualizations.py` - Visualization module with charts and word clouds
- `main.py` - Command line interface script
- `run_local.py` - Quick start script with dependency checking
- `requirements.txt` - Python dependencies
- `spec_analista_chat.md` - Original specification for the analyzer
- `conversa1.txt` / `conversa2.txt` - Sample conversation files for testing

### Deployment Files
- `Dockerfile` - Container configuration for deployment
- `.streamlit/config.toml` - Streamlit app configuration
- `.gitignore` - Git ignore patterns
- `README.md` - Comprehensive documentation

## Running the Application

### Installation
```bash
pip install -r requirements.txt
```

### Streamlit Web Dashboard (Recommended)
```bash
streamlit run app.py
```
- Access at: http://localhost:8501
- Interactive web interface with visualizations
- Upload files, paste text, or use sample data
- Export reports and visualizations

### Command Line Interface
```bash
python main.py
```

The CLI offers multiple input options:
1. Load conversation from file
2. Use sample data
3. Manual text input
4. Test with conversa1.txt
5. Test with conversa2.txt

### Quick Start Script
```bash
python run_local.py
```
- Checks dependencies automatically
- Tests all modules
- Launches Streamlit dashboard

### AI Integration
For enhanced AI analysis, provide an OpenAI API key:
- In Streamlit: Enter key in the sidebar
- Via environment variable: `OPENAI_API_KEY=your_key_here`
- The application works without AI, providing statistical analysis

### Deployment Options
- **Local**: `streamlit run app.py`
- **Streamlit Cloud**: Connect GitHub repo for one-click deploy
- **Docker**: `docker build -t whatsapp-analyzer . && docker run -p 8501:8501 whatsapp-analyzer`
- **Heroku/Railway**: Deploy directly from repository

## Analysis Features

### Statistical Analysis
- **Linguistic Analysis**: Message counts, word statistics, activity patterns, conversation span
- **Psychological Analysis**: Emotional tone indicators, response times, interaction patterns
- **Communication Analysis**: Question/exclamation patterns, conversation starters vs responses, politeness indicators
- **Relationship Insights**: Engagement balance, conversation flow, relationship health scoring

### AI-Enhanced Analysis (with OpenAI API)
- **Sentiment Analysis**: Deep emotional pattern recognition
- **Relationship Dynamics**: Communication style assessment and compatibility analysis
- **Communication Insights**: Professional consultation-level recommendations

### Interactive Visualizations
- **Timeline Charts**: Interactive message evolution over time (Plotly)
- **Activity Heatmaps**: Hour/day activity patterns with drill-down
- **Word Clouds**: Customizable word frequency visualizations
- **Participant Comparisons**: Side-by-side metrics and statistics
- **Emotion Charts**: Sentiment distribution across participants
- **Response Time Analysis**: Communication timing patterns

## Input Format

The analyzer expects WhatsApp export format:
```
DD/MM/YYYY HH:MM - Name: Message content
```

## Custom Agents

### Spare Parts Quote Requester
A specialized procurement agent that handles industrial component sourcing and quote requests from suppliers.

## Available Tools and Permissions

- `Bash(python:*)` - All Python-related commands
- `Bash(mkdir:*)` - Directory creation commands