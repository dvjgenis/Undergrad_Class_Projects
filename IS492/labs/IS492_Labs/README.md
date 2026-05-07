# IS 492 — AI & LLM Development
### Building Intelligent Agents, Multi-Agent Systems & LLM Applications

---

## 📋 Course Overview

**IS 492** focuses on practical AI development using Large Language Models (LLMs) and multi-agent systems. The course covers building intelligent agents, prompt engineering, agent orchestration frameworks, and deploying LLM-powered applications.

---

## 📁 Project Structure

```
IS492_Labs/
├── lab-1-vibe-coding-101-dgeni2/          # AI Coding Assistants Comparison
├── lab-2-fullstack-1-dgeni2/               # Full-Stack Development
├── lab-3-building-agent-with-langgraph-dgeni2/  # LangGraph Agent Development
├── lab-4-tts-stt-dgeni2/                  # Text-to-Speech & Speech-to-Text
├── lab-5-llm-eval-safety-dgeni2/          # LLM Evaluation & Safety
├── lab-6-mcp-chrome-devtools-dgeni2/       # Model Context Protocol (MCP)
├── lab-7-multi-agent-systems-dgeni2/      # Multi-Agent Systems (AutoGen & CrewAI)
├── v0-personal-website-design/            # Personal Website Project
├── v0-prompt-engineering-app/             # Prompt Engineering Learning Platform
└── README.md
```

---

## 🧪 Labs Overview

### Lab 1: Vibe Coding 101 - AI Coding Assistants
**Focus:** Comparing AI coding tools (GitHub Copilot vs. Gemini CLI)

| Aspect | Comparison |
|--------|------------|
| **Code Quality** | Both produce clean, functional code (~100 lines) |
| **Speed** | GitHub Copilot faster (integrated IDE) vs Gemini (terminal-based) |
| **Ease of Use** | Copilot more seamless; Gemini requires context switching |
| **Debugging** | Copilot better IDE integration for iterative refinement |

**Deliverables:**
- `pong_pygame.py` - Base implementation
- `pong_GitHub_Copilot.py` - Copilot-generated version
- `pong_Gemini_CLI.py` - Gemini-generated version

---

### Lab 2: Full-Stack Development
**Focus:** Building full-stack applications with modern frameworks

**Technologies:** Next.js, React, TypeScript

---

### Lab 3: Building Agents with LangGraph
**Focus:** Creating intelligent agents using LangGraph framework

**Key Concepts:**
- Agent state management
- Tool integration
- Workflow orchestration
- Memory and context handling

**Deliverable:** `IS492_lab3_Building_Agents_in_LangGraph_Dulf_Genis.ipynb`

---

### Lab 4: Text-to-Speech & Speech-to-Text
**Focus:** Audio processing with LLMs

**Technologies:**
- TTS (Text-to-Speech) APIs
- STT (Speech-to-Text) APIs
- Audio processing pipelines

**Deliverable:** `Lab_4_demo.ipynb`

---

### Lab 5: LLM Evaluation & Safety
**Focus:** Evaluating LLM performance and ensuring safe outputs

**Topics:**
- Evaluation metrics
- Safety guardrails
- Bias detection
- Performance benchmarking

**Deliverable:** `IS492_lab5_LLM_Eval_and_Safety.ipynb`

---

### Lab 6: Model Context Protocol (MCP) with Chrome DevTools
**Focus:** Integrating LLMs with browser automation

**Technologies:**
- Model Context Protocol (MCP)
- Chrome DevTools Protocol
- Browser automation
- Context-aware agent interactions

**Deliverables:**
- `buggy-app/` - Sample web application
- `mcp.json` - MCP configuration
- Integration examples

---

### Lab 7: Multi-Agent Systems (AutoGen & CrewAI)
**Focus:** Building collaborative multi-agent workflows

**Frameworks:**

#### AutoGen (Microsoft)
- **Style:** Conversational, iterative
- **Use Case:** Problems requiring debate/refinement
- **Agents:** ResearchAgent, AnalysisAgent, BlueprintAgent, ReviewerAgent

#### CrewAI (Crew Framework)
- **Style:** Task-based, sequential
- **Use Case:** Structured workflows with clear inputs/outputs
- **Agents:** FlightAgent, HotelAgent, ItineraryAgent, BudgetAgent

**Deliverables:**
- `autogen/` - AutoGen implementations (5 demos)
- `crewai/` - CrewAI implementations
- Multiple workflow outputs demonstrating agent collaboration

**Key Implementations:**
- Product planning workflow (4 agents)
- E-learning platform design (4 agents)
- Conference planning (4 agents)
- 5-agent pricing strategy workflow
- Travel planning (Iceland, Paris)

---

## 🏆 Personal Projects

### v0 Personal Website Design
**Technology Stack:** Next.js, React, TypeScript, Tailwind CSS, Supabase

**Features:**
- Responsive design
- Component-based architecture
- Theme provider
- Contact form integration
- Project showcase

**Structure:**
- `app/` - Next.js app directory
- `components/` - React components
- `lib/` - Utilities and Supabase client

---

### v0 Prompt Engineering App
**Platform:** Interactive learning platform for prompt engineering

**Features:**
- **4 Core Techniques:**
  - Few-Shot Learning
  - Chain-of-Thought (CoT)
  - RAG (Retrieval-Augmented Generation)
  - Self-Reflection

- **Learning System:**
  - 5 levels per technique (Amateur → Professional)
  - Guided learning hub
  - Challenge arena with efficacy scoring
  - Progress tracking dashboard

**Technology:** Next.js, TypeScript, React

**Deployment:** [Live on Vercel](https://v0-prompt-engineering-app-beta.vercel.app/)

---

## 🛠️ Tools & Concepts Toolkit

### Python Libraries

| Library | Purpose |
|---------|---------|
| `langchain` | LLM application framework |
| `langgraph` | Agent workflow orchestration |
| `autogen` | Multi-agent conversational systems |
| `crewai` | Task-based multi-agent framework |
| `openai` | OpenAI API client |
| `anthropic` | Claude API client |
| `pyttsx3` / `gTTS` | Text-to-speech |
| `speech_recognition` | Speech-to-text |

### Web Technologies

| Technology | Use Case |
|------------|----------|
| **Next.js** | React framework for full-stack apps |
| **TypeScript** | Type-safe JavaScript |
| **React** | UI component library |
| **Tailwind CSS** | Utility-first CSS framework |
| **Supabase** | Backend-as-a-Service |
| **Vercel** | Deployment platform |

### AI/LLM Concepts

| Concept | Description |
|---------|-------------|
| **Prompt Engineering** | Crafting effective prompts for LLMs |
| **Few-Shot Learning** | Providing examples in prompts |
| **Chain-of-Thought** | Step-by-step reasoning |
| **RAG** | Retrieval-Augmented Generation |
| **Agent Orchestration** | Coordinating multiple AI agents |
| **Tool Use** | LLMs calling external functions |
| **Memory Management** | Maintaining context across interactions |
| **Safety & Evaluation** | Ensuring reliable, safe outputs |

### Multi-Agent Patterns

| Pattern | Description |
|---------|-------------|
| **Conversational** | Agents chat and iterate (AutoGen) |
| **Sequential** | Agents complete tasks in order (CrewAI) |
| **Parallel** | Multiple agents work simultaneously |
| **Hierarchical** | Manager-agent coordination |
| **Swarm** | Many agents with simple rules |

---

## 🎯 Key Takeaways

1. **AI Coding Assistants:** Integrated tools (Copilot) > CLI tools for iterative development
2. **Agent Frameworks:** Choose AutoGen for flexibility, CrewAI for structure
3. **Prompt Engineering:** Systematic learning improves LLM interaction quality
4. **Multi-Agent Systems:** Specialization and collaboration solve complex problems
5. **Full-Stack Integration:** LLMs work best when integrated into complete applications
6. **Evaluation Matters:** Always measure and validate LLM outputs

---

## 🚀 Quick Start Examples

### AutoGen Agent Setup
```python
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(
    name="assistant",
    llm_config={"config_list": [{"model": "gpt-4", "api_key": "..."}]}
)
user_proxy = UserProxyAgent(name="user_proxy", human_input_mode="NEVER")
user_proxy.initiate_chat(assistant, message="Your task here")
```

### CrewAI Crew Setup
```python
from crewai import Agent, Task, Crew

agent = Agent(
    role="Researcher",
    goal="Research and analyze information",
    backstory="You are an expert researcher..."
)
task = Task(
    description="Research topic X",
    agent=agent,
    expected_output="Detailed research report"
)
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

### LangGraph Agent
```python
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

# Define agent state
# Build graph with nodes
# Add edges and tools
# Compile and run
```

---

## 📚 Additional Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

*Part of the UIUC Information Sciences curriculum*

