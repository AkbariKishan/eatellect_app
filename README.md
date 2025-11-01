# 🥗 Eatellect

**An AI-powered barcode scanner that provides instant health insights about food products**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Known Issues](#known-issues)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## 🎯 Overview

Eatellect is an intelligent food product analyzer that helps consumers make informed health decisions. By simply scanning a product barcode, users receive AI-powered nutritional analysis, health recommendations, and ingredient insights powered by LangGraph's agentic AI framework.

### Motivation
Reading and understanding nutrition labels can be overwhelming. Eatellect eliminates this friction by providing instant, personalized health insights using advanced AI agents.

### Problem Solved
- **Manual label reading**: No more squinting at tiny ingredient lists
- **Nutritional complexity**: AI translates complex data into actionable insights
- **Health decision-making**: Get personalized recommendations based on product analysis

## ✨ Features

- 📸 **Real-time Barcode Scanning**: Powered by OpenCV for accurate barcode detection
- 🌐 **Product Data Retrieval**: Integration with Open Food Facts database
- 🤖 **Agentic AI Analysis**: Multi-agent LangGraph workflow for comprehensive health insights
- 💡 **Smart Recommendations**: LLM-powered health advice tailored to product composition
- ⚡ **Token-Optimized**: Intelligent message trimming to stay within API limits
- 🔄 **Multi-turn Conversations**: Stateful interactions for follow-up questions

## 🛠️ Technology Stack

- **LangGraph**: Agentic AI workflow orchestration and state management
- **Groq API** (llama-3.3-70b-versatile): Fast LLM inference for health analysis
- **OpenCV (cv2)**: Image processing and barcode detection
- **Python 3.13**: Core backend development
- **Open Food Facts API**: Comprehensive product database
- **NumPy**: Efficient array operations for image handling

## 🏗️ Architecture

Eatellect uses a multi-agent LangGraph architecture:

```
User Image → Barcode Detection → Product Lookup → Nutrition Extraction → LLM Analysis → Health Insights
                (OpenCV)        (Open Food Facts)    (Structured Data)     (Groq/Llama)   (User Output)
```

### Agent Workflow
1. **Vision Agent**: Processes uploaded image using cv2.imdecode()
2. **Data Agent**: Retrieves product information from Open Food Facts
3. **Analysis Agent**: Performs LLM-based health evaluation with token optimization
4. **Response Agent**: Formats insights for user consumption

## 📦 Installation

### Prerequisites
- Python 3.13+
- pip package manager
- Groq API key ([Get one here](https://console.groq.com))

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/AkbariKishan/eatellect_app.git
cd eatellect_app
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your credentials:
# GROQ_API_KEY=your_groq_api_key_here
# MAX_TOKENS=10000
# LOG_LEVEL=INFO
```

5. **Run the application**
```bash
python main.py
```

## 🚀 Usage

### Basic Usage

```python
from eatellect import ProductAnalyzer

# Initialize analyzer
analyzer = ProductAnalyzer()

# Scan product barcode
result = analyzer.scan_barcode("path/to/product_image.jpg")

# Get health analysis
print(result['health_analysis'])
print(result['nutrition_info'])
print(result['recommendations'])
```

### API Endpoint (if web service)

```bash
curl -X POST http://localhost:8000/analyze \
  -F "image=@product_image.jpg"
```

### Expected Output

```json
{
  "product_name": "Organic Almond Butter",
  "barcode": "123456789012",
  "nutrition_info": {
    "calories": 190,
    "protein": "7g",
    "fat": "16g"
  },
  "health_analysis": "This product is a good source of healthy fats and protein...",
  "recommendations": "Suitable for high-protein diets. Watch portion sizes due to calorie density."
}
```

## 📁 Project Structure

```
eatellect_app/
├── agents/              # LangGraph agent definitions
│   ├── vision_agent.py
│   ├── data_agent.py
│   └── analysis_agent.py
├── tools/               # Custom tools for barcode scanning, API calls
│   ├── barcode_scanner.py
│   └── api_client.py
├── models/              # Data models and state schemas
│   └── state.py
├── utils/               # Helper functions (cv2.imdecode, image processing)
│   ├── image_utils.py
│   └── token_utils.py
├── config/              # Configuration files
│   └── settings.py
├── tests/               # Unit and integration tests
├── .env.example         # Example environment variables
├── requirements.txt     # Python dependencies
├── main.py             # Application entry point
└── README.md           # This file
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# API Keys
GROQ_API_KEY=your_groq_api_key

# Token Management
MAX_TOKENS=10000              # Maximum tokens per LLM request
TOKEN_BUFFER=2000             # Safety buffer for responses

# Logging
LOG_LEVEL=INFO                # Options: DEBUG, INFO, WARNING, ERROR

# Database (if applicable)
OPEN_FOOD_FACTS_URL=https://world.openfoodfacts.org/api/v0
```

### Model Configuration

The app uses `llama-3.3-70b-versatile` by default. To change models, update `config/settings.py`:

```python
MODEL_NAME = "llama-3.3-70b-versatile"
TEMPERATURE = 0.7
MAX_RETRIES = 3
```

## ⚠️ Known Issues

- **Groq API Rate Limits**: Free tier limited to 12,000 tokens per minute. Consider upgrading for production use
- **Image Quality**: Barcode detection requires clear, well-lit images
- **Database Coverage**: Limited to products available in Open Food Facts database
- **Token Overflow**: Large conversation histories may trigger 413 errors; message trimming is implemented

## 🗺️ Roadmap

- [ ] **Multi-product Comparison**: Side-by-side nutritional analysis
- [ ] **User Preference Memory**: Personalized recommendations based on dietary restrictions
- [ ] **Mobile App Interface**: React Native or Flutter frontend
- [ ] **Restaurant Menu Analysis**: Extend beyond packaged products
- [ ] **Advanced Vision**: Support for nutrition label OCR without barcodes
- [ ] **Multilingual Support**: Product analysis in multiple languages

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add unit tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR


---


⭐ **If you find this project helpful, please consider giving it a star!**

---

## 🙏 Acknowledgments

- [Open Food Facts](https://world.openfoodfacts.org/) for comprehensive product database
- [LangGraph](https://github.com/langchain-ai/langgraph) for agentic AI framework
- [Groq](https://groq.com/) for lightning-fast LLM inference
- [OpenCV](https://opencv.org/) for computer vision capabilities