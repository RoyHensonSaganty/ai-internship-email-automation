from google import genai
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import requests
import time
from email.message import EmailMessage
import smtplib

load_dotenv()

gmail_address=os.getenv("GMAIL_ADDRESS")
gmail_app_pass=os.getenv("GMAIL_APP_PASSWORD")
g_api_key=os.getenv("GEMINI_API_KEY")
email=os.getenv("RECIPIENT_EMAIL")

j_url="https://himalayas.app/jobs/api/search"

params={
    "q":"React",
    "employment_type":"intern",
    "sort":"recent"
}

client=genai.Client(api_key=g_api_key)

class InternshipAnalysis(BaseModel):
    relevant:bool
    reason:str

j_response=requests.get(j_url,params=params)

print("Status Code:",j_response.status_code)


if j_response.status_code==200:
    print("Request successfull!")
    data=j_response.json()
else:
    print("Something wrong!")
    print(j_response.text)


def send_email(to,subject,body):
    try:

        msg=EmailMessage()

        msg["From"]=gmail_address
        msg["To"]=to
        msg["Subject"]=subject

        msg.set_content("A relevant internship was found. Please view this email in an AI Engineer-capable email client.")


        msg.add_alternative(body, subtype="html")

        server=smtplib.SMTP_SSL("smtp.gmail.com",465)
        server.login(gmail_address,gmail_app_pass)

        server.send_message(msg)
        server.quit()

        print("EMAIL SENT SUCCESSFULLY!")
        return True
    
    except Exception as error:
        print("Error: ",error)
        return False


if os.path.exists("sent_jobs.txt"):
    with open("sent_jobs.txt","r") as file:
        sent_jobs=file.read().splitlines()
else:
    sent_jobs=[]

for job in data["jobs"][:10]:
    try:

        job_id=str(job["guid"])
        if job_id in sent_jobs:
            print("Already Processed!")
            continue

        title=job["title"]
        company=job["companyName"]
        description=job["description"]
        application_link=job["applicationLink"]
        location=", ".join(job["locationRestrictions"])
        employment_type=job["employmentType"]

        g_response=client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=f"""
                Analyze this internship

                Title:{title}
                Company:{company}
                Description:{description}

                Determine whether this is relevant to a student who is in interested in AI engineer.""",
            config={
                "response_mime_type":"application/json",
                "response_schema":InternshipAnalysis
            }
        )
    except Exception as g_error:
        print("Gemini Error: ",g_error)
        time.sleep(10)
        continue

    g_result=g_response.parsed

    if g_result.relevant:
        print("-------------------------")
        print("Relevant Intership found!")
        print()
        print("Title: ",title)
        print("Company: ",company)
        print("Employment: ",employment_type)
        print("Location: ",location)
        print("Apply: ",application_link)
        
        e_response=email_response = send_email(
            f"{email}",

            f"🚀 Relevant Internship: {title}",

            f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px;">
                <h1>🚀 Relevant Internship Found!</h1>
                <hr>
                <h2>{title}</h2>
                <p><strong>🏢 Company:</strong> {company}</p>
                <p><strong>💼 Employment:</strong> {employment_type}</p>
                <p><strong>📍 Location:</strong> {location}</p>
                <h3>🧠 Why is it relevant?</h3>
                <p>{g_result.reason}</p>
                <h3>📝 Job Description</h3>
                <p>{description}</p>
                <br>
                <a href="{application_link}"style="display: inline-block;padding: 12px 24px;background-color: #007bff;color: white;text-decoration: none;border-radius: 6px;font-weight: bold;">
                🔗 APPLY NOW
                </a>
                <br><br>
                <p style="color: gray; font-size: 12px;">
                    This internship was automatically identified
                    as relevant using Gemini AI.
                </p>
            </div>
            """)

        if e_response:
            with open("sent_jobs.txt","a") as file:
                file.write(job_id + "\n")
            sent_jobs.append(job_id)
            print("-----------------------")
    else:
        print("Not relevant")
        print("Title: ",title)
        print("Company: ",company)
        print("------------------------")
