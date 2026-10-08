# AI Internship Email Automation

A Python-based automation system that fetches internship opportunities, analyzes their relevance using Google Gemini AI, and automatically sends email notifications for relevant opportunities.

## Tech Stack

- Python
- Google Gemini API
- Pydantic
- REST API
- Gmail SMTP
- python-dotenv

## Workflow

```text
Himalayas Jobs API
        ↓
Fetch Internship Listings
        ↓
Gemini AI Analysis
        ↓
   Relevant?
    ↙     ↘
  YES      NO
   ↓        ↓
 Email     Skip
   ↓
sent_jobs.txt
