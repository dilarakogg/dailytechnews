# DAILY TECH-NEWS


This project is a personal automation tool designed to optimize daily technology tracking, manage information overload, and make productive use of transition time.

## Project Motivation

In an era of rapid AI evolution, staying updated has become a time-consuming task due to the sheer volume of data across multiple platforms. This project aims to solve this by:
- **Time Optimization:** Eliminating the need for manual searching by delivering filtered content directly to the inbox every morning.
- **Focused Insights:** Filtering noise by targeting specific keywords such as AI, LLM, Robotics, and Computer Vision.
- **Efficient Summarization:** Utilizing OpenAI's GPT-4o model to convert long-form articles into concise, professional reports for quick reading during busy schedules.

## Technical Architecture & Tooling

The project is built on a Python-based data processing loop and leverages the following components:

- **Python 3.10+**: The core engine of the system.
- **OpenAI API (GPT-4o)**: Powers the Natural Language Processing (NLP) capabilities to analyze and summarize articles in a professional tone.
- **Feedparser & BeautifulSoup4**: Manages data extraction from academic and technical RSS feeds (MIT News, Science Daily, Google News, etc.) and cleanses HTML content.
- **GitHub Actions**: Serves as a cloud-based scheduler (Cron Job), allowing the script to run autonomously every morning without requiring a local machine.
- **Deduplication Logic**: A file-based logging system (`sent_articles.txt`) ensures that previously sent news articles are not delivered multiple times.



## Project Structure


├── .github/workflows/

│   └── daily_run.yml    # GitHub Actions workflow configuration


├── dailytechnews.py     # Main processing engine and logic


├── requirements.txt     # Project dependencies


├── sent_articles.txt    # Record of previously sent articles (Memory)


