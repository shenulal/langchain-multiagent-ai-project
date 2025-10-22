# 🤖 LangChain Multi-Agent AI System

A sophisticated multi-agent AI system built with LangChain that provides intelligent assistance through specialized agents. The system supports both text and voice input/output and integrates with external APIs for real-time data.

## 🌟 Features

### Multi-Agent Architecture
- **Weather Agent**: Real-time weather information and forecasts
- **Research Agent**: Web search, news, and information gathering
- **General Agent**: Calculations, date/time, and general assistance
- **Smart Routing**: Automatically selects the best agent for each query

### Input/Output Modes
- **Text Interface**: Type your questions and get text responses
- **Voice Interface**: Speak your questions and receive audio responses
- **Web Interface**: Modern, responsive web UI with real-time chat

### External Integrations
- **OpenWeatherMap API**: Current weather and forecasts
- **NewsAPI**: Latest news and headlines
- **DuckDuckGo**: Web search capabilities
- **Speech Recognition**: Voice-to-text conversion
- **Text-to-Speech**: Audio response generation

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Optional: Weather API key, News API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd langchain-sample-project
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the application**
```bash
python main.py
```

5. **Open your browser**
Navigate to `http://localhost:8000` to access the web interface.

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for enhanced functionality)
WEATHER_API_KEY=your_openweathermap_api_key_here
NEWS_API_KEY=your_newsapi_key_here

# Application Settings
APP_HOST=localhost
APP_PORT=8000
LOG_LEVEL=INFO

# Speech Settings
SPEECH_RATE=200
SPEECH_VOLUME=0.9
```

### API Keys Setup

1. **OpenAI API Key** (Required)
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Create an API key in your dashboard

2. **Weather API Key** (Optional)
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Get a free API key

3. **News API Key** (Optional)
   - Sign up at [NewsAPI](https://newsapi.org/)
   - Get a free API key

## 📖 Usage Examples

### Text Queries

**Weather Queries:**
```
"What's the weather in London?"
"Will it rain tomorrow in New York?"
"Temperature in Tokyo"
```

**Research Queries:**
```
"What is artificial intelligence?"
"Latest technology news"
"Tell me about quantum computing"
```

**General Queries:**
```
"Calculate 15% of 250"
"What time is it?"
"Hello, how are you?"
```

### Voice Interaction

1. Click the "🎤 Voice Input" button
2. Speak your question clearly
3. Click "🛑 Stop Recording" when done
4. Receive both text and audio responses

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │    │  Agent Coordinator│    │  External APIs  │
│                 │    │                  │    │                 │
│ • HTML/CSS/JS   │◄──►│ • Route queries  │◄──►│ • Weather API   │
│ • Voice I/O     │    │ • Manage agents  │    │ • News API      │
│ • Real-time UI  │    │ • Handle errors  │    │ • Search API    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
            ┌───────▼──┐ ┌──────▼──┐ ┌──────▼──────┐
            │ Weather  │ │Research │ │  General    │
            │ Agent    │ │ Agent   │ │  Agent      │
            │          │ │         │ │             │
            │• Weather │ │• Search │ │• Calculator │
            │• Forecast│ │• News   │ │• DateTime   │
            └──────────┘ └─────────┘ └─────────────┘
```

### Agent Selection Logic

The system uses confidence scoring to select the most appropriate agent:

1. **Query Analysis**: Each agent analyzes the query and returns a confidence score (0.0-1.0)
2. **Agent Selection**: The agent with the highest confidence score is selected
3. **Fallback**: If no agent has sufficient confidence, the General Agent handles the query
4. **Execution**: The selected agent processes the query using its specialized tools

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/
```

### Run Example Queries
```bash
python examples/example_queries.py
```

### Manual Testing
1. Start the application: `python main.py`
2. Open `http://localhost:8000`
3. Try various queries to test different agents

## 📁 Project Structure

```
langchain-sample-project/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
│
├── src/                   # Source code
│   ├── agents/           # Agent implementations
│   │   ├── base_agent.py     # Abstract base agent class
│   │   ├── coordinator.py    # Multi-agent coordinator
│   │   ├── weather_agent.py  # Weather specialist agent
│   │   ├── research_agent.py # Research specialist agent
│   │   └── general_agent.py  # General purpose agent
│   │
│   ├── tools/            # External API tools
│   │   ├── weather_tool.py   # Weather API integration
│   │   ├── news_tool.py      # News API integration
│   │   └── search_tool.py    # Search and utility tools
│   │
│   ├── voice/            # Voice processing
│   │   └── speech_handler.py # Speech-to-text and text-to-speech
│   │
│   └── utils/            # Utilities
│       └── logger.py         # Logging configuration
│
├── static/               # Static web assets
│   ├── style.css            # CSS styles
│   └── script.js            # JavaScript functionality
│
├── templates/            # HTML templates
│   └── index.html           # Main web interface
│
├── tests/                # Test files
│   └── test_agents.py       # Agent unit tests
│
├── examples/             # Example scripts
│   └── example_queries.py   # Example usage
│
└── logs/                 # Application logs
    └── app.log              # Main log file
```

## 🔌 API Endpoints

### REST API

- `GET /` - Web interface
- `POST /query/text` - Process text query
- `POST /query/voice` - Process voice query
- `GET /health` - Health check and agent status

### Example API Usage

```python
import requests

# Text query
response = requests.post('http://localhost:8000/query/text', 
                        json={'query': 'Weather in London'})
result = response.json()

# Voice query (with audio file)
files = {'audio_file': open('recording.wav', 'rb')}
response = requests.post('http://localhost:8000/query/voice', files=files)
result = response.json()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**1. API Key Errors**
- Ensure all required API keys are set in `.env`
- Check API key validity and quotas

**2. Voice Input Not Working**
- Check microphone permissions in browser
- Ensure PyAudio is properly installed

**3. Agent Not Responding**
- Check internet connection for external APIs
- Verify OpenAI API key and credits

**4. Installation Issues**
- Use Python 3.8+ 
- Install system dependencies for audio processing

### Getting Help

- Check the logs in `logs/app.log`
- Run tests to identify issues: `pytest tests/`
- Review example queries: `python examples/example_queries.py`

## 🎯 Future Enhancements

- [ ] Add more specialized agents (Finance, Health, etc.)
- [ ] Implement conversation memory across sessions
- [ ] Add support for file uploads and processing
- [ ] Integrate with more external APIs
- [ ] Add user authentication and personalization
- [ ] Implement agent learning and improvement
- [ ] Add support for multiple languages
- [ ] Create mobile app interface
