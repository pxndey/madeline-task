# madeline-task

Task Submission for AI Engineer Role at Madeline & co.

## Setup

- Clone the repository

```bash
git clone git@github.com:pxndey/madeline-task.git
```

- Install dependencies

```bash
conda create madeline-task python=3.9 -y
conda activate madeline-task
cd madeline-task
pip install -r app/requirements.txt
```

- Specify Environment Variables in the format provided in .env.example

- Run the app and set up the database schema

```bash
docker compose up
docker cp ./data/init_db.sql postgres_db:/tmp/init_db.sql
docker exec -it postgres_db psql -U youruser -d yourdatabase -f /tmp/init_db.sql
```

- Send a POST Request to http://localhost:8000/analyze-competitor to use the Agent

Sample Query

```json
{
    "user_id": "123456789",
    "query": "What is Duolingo's marketing strategy?",
}
```

Sample Response

```json
response_obj = {
    "respone": {
        "original_question": "Analyze Competitor X's digital strategy",
        "expanded_question": "How does Competitor X use social media?",
        "search_queries": [
            "Competitor X digital marketing",
            "Competitor X SEO",
            "Competitor X PPC"
        ],
        "search_results": [ 
            {"title": "SEO Analysis", "url": "https://example.com/seo", "content": "SEO data", "score": 0.85},
            {"title": "Social Media", "url": "https://example.com/social", "content": "Social insights", "score": 0.78},
            {"title": "PPC Strategy", "url": "https://example.com/ppc", "content": "PPC campaigns", "score": 0.82}
        ],
        "messages": [ 
            {"content": "Competitor X uses aggressive SEO.", "id": "msg_001"}
        ]
    }
}
```


### Database Schema

![Schema](./data/image.png)