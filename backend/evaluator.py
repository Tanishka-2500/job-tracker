import os
from typing import List, Dict
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
import asyncio

load_dotenv()

class JobEvaluation(BaseModel):
    is_valid_job: bool = Field(description="True if this is a genuine fresher-level job posting for the requested role. False if it is a podcast, blog, or a Senior/Lead/Manager role requiring >1 year experience.")
    cleaned_title: str = Field(description="The clean, professional job title. E.g. 'Data Analyst' instead of 'Data Analyst - Urgent Hiring India'")

class JobEvaluationList(BaseModel):
    evaluations: List[JobEvaluation]

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    # Using a typical Groq Qwen model identifier. 
    # You can change this to qwen-2.5-coder-32b or similar depending on what Groq exposes.
    return ChatGroq(model="qwen-2.5-32b", groq_api_key=api_key, temperature=0)

async def evaluate_jobs_batch(jobs: List[dict], role_category: str = "") -> List[dict]:
    """Passes a list of scraped jobs to Groq Qwen to filter out non-jobs, seniors, and clean titles."""
    llm = get_llm()
    if not llm:
        print("[Evaluator] GROQ_API_KEY not found in .env. Skipping AI evaluation.")
        return jobs
        
    if not jobs:
        return []

    parser = PydanticOutputParser(pydantic_object=JobEvaluationList)
    
    prompt = PromptTemplate(
        template="""You are an expert technical recruiter filtering jobs for a FRESHER.
We are specifically looking for roles related to: {role_category}

I am giving you a list of URLs and raw extracted titles from a corporate website.
For each item in the list, determine:
1. Is it actually a job posting? (Reject podcasts, blogs, press releases, etc).
2. Is it a Fresher level role? (Maximum 0-1 years experience). Reject ANY title containing words like Senior, Sr, Lead, Manager, Principal, Director, Head, Staff, or II/III.
3. Does it roughly match the {role_category} profile? (It doesn't have to be exact, but it shouldn't be completely unrelated like 'Nurse' if the category is 'Software Engineer').
4. What is the clean, official job title? (Remove locations, IDs, or extra fluff).

IMPORTANT: Return exactly the same number of evaluations as there are items provided.

Here are the items:
{items}

{format_instructions}
""",
        input_variables=["items", "role_category"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    
    print(f"[Evaluator] Processing {len(jobs)} jobs through Groq Qwen for cleaning...")
    
    try:
        # We process in chunks of 15 to avoid context limit confusion and ensure reliable structured output length mapping
        chunk_size = 15
        valid_jobs = []
        
        for i in range(0, len(jobs), chunk_size):
            chunk = jobs[i:i+chunk_size]
            chunk_text = ""
            for j, job in enumerate(chunk):
                chunk_text += f"{j+1}. Title: {job.get('title')} | URL: {job.get('url')}\n"
                
            response = await chain.ainvoke({
                "items": chunk_text, 
                "role_category": role_category or "Technical Fresher"
            })
            
            # Match evaluations back to the chunk
            for j, eval_res in enumerate(response.evaluations):
                if j < len(chunk):
                    if eval_res.is_valid_job:
                        job = chunk[j]
                        job["title"] = eval_res.cleaned_title
                        valid_jobs.append(job)
                    else:
                        print(f"  [AI Removed] '{chunk[j].get('title')}' - Not a valid fresher {role_category} job")
                        
            await asyncio.sleep(1) # small pause to respect rate limits
            
        print(f"[Evaluator] AI kept {len(valid_jobs)} real jobs out of {len(jobs)}")
        return valid_jobs
        
    except Exception as e:
        print(f"[Evaluator] AI Evaluation failed, falling back to original jobs. Error: {e}")
        return jobs
