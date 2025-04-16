
# 🛍️ ShopSmart.AI - Intelligent Shopping Assistant with CrewAi

Welcome to the **ShopSmart.AI** repository! This project is an **Intelligent Shopping Assistant** designed to enhance your shopping experience using CrewAi, providing personalized product recommendations and efficient assistance.

---
![Agentic Flow](flow.png)

## 🚀 Features

- **Personalized Recommendations**: Get smart shopping suggestions based on user preferences and behavior.
- **Multi-Agent System**: Powered by **CrewAi**, intelligent agents collaborate to streamline the shopping journey.
- **Voice & Text Input**: Use voice or text to interact with the assistant for seamless shopping.
- **Product Search & Comparison**: Search across multiple platforms and compare products.
- **Review Summarization**: Analyze and summarize reviews with **RAG** (Retrieval-Augmented Generation).
- **User-Friendly Interface**: Built with **Streamlit** for easy and intuitive navigation.

---
## 🛠️ Technologies, Tools & Gen AI Capabilities Mapping (Updated)

| Tool / Library                 | Purpose                                                                 | Gen AI Capability Demonstrated                         |
|-------------------------------|-------------------------------------------------------------------------|--------------------------------------------------------|
| `CrewAI`                      | Manages agents and orchestrates multi-step processes                    | ✅ Multi-Agent Collaboration                           |
| `SerperDevTool`               | Searches the web for product listings                                   | ✅ Information Retrieval for RAG                       |
| `ScrapeWebsiteTool`           | Scrapes data from product listing websites                              | ✅ Data Collection for downstream processing           |
| `WebsiteSearchTool + RAG`     | Retrieves and summarizes user reviews                                   | ✅ Retrieval-Augmented Generation (RAG)                |
| `Google Gemini LLM`           | Provides reasoning, analysis, and natural language output               | ✅ Structured Output / JSON Mode<br>✅ Review Summarization |
| `LiteLLM`                     | Runs Gemini LLMs efficiently                                            | ✅ Efficient LLM Inference                             |
| `Google Embeddings`           | Used for document retrieval in RAG setup                                | ✅ Vector Search for RAG                               |
| `Colab + Python`              | Development environment                                                 | ✅ Experimentation and Prototyping                     |
| `speech_recognition`          | Converts user voice into text                                           | ✅ Voice-to-Text Input (Integrated!)                   |

---

### 🔊 New Feature Added

**Voice Input Powered by `speech_recognition`:**  
Users can now *speak* their shopping queries instead of typing. The spoken query is transcribed and seamlessly passed to the input agent for further processing.

---

---

## 📦 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/SheemaMasood381/Intelligent-Shopping-Assistant-with-CrewAi.git
cd Intelligent-Shopping-Assistant-with-CrewAi
```

### 2. Install Dependencies

Ensure Python is installed, and then install the required libraries:

```bash
pip install -r requirements.txt
```

### 3. Run the Application

Start the application with:

```bash
python app.py
```

### 4. Open in Browser

Navigate to [http://localhost:5000](http://localhost:5000) in your browser to interact with ShopSmart.AI.

---

## 🗂️ Project Structure

```plaintext
.
├── agentic_flow.png          # Visual representation of the agentic flow
├── agents.py                 # Defines the intelligent agents
├── crew.py                   # Core integration with CrewAi
├── task.py                   # Task management and orchestration
├── ShopSmartAssistant.ipynb  # Jupyter Notebook for testing and analysis
├── app.py                    # Main application script
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

---

## 🌐 Agentic Flow

The flow diagram (`flow.png`) showcases how the agents collaborate to handle tasks like product search, comparison, review summarization, and recommendations.

---

## ⚡ Deployment with CrewAi Enterprise Framework

For deployment, the following files are crucial:

- **agents.py**: Defines the intelligent agents.
- **crew.py**: Integrates with the CrewAi framework for task orchestration.
- **task.py**: Manages task execution and agent interactions.

---

## 🤝 Contributions

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your changes.
3. Submit a pull request.

---

## 📝 License

This project is licensed under the MIT License.

---

Happy Shopping with ShopSmart.AI! 🚀
