from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Azure GPT-4.1 setup
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"
token = os.getenv("GITHUB_TOKEN")

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token)
)

@app.route("/", methods=["GET", "POST"])
def index():
    output = None

    if request.method == "POST":
        grade = request.form.get("grade", "")
        subject = request.form.get("subject", "")
        exams = request.form.getlist("exam")
        exam_text = ", ".join(exams)
        topics = request.form.get("topics", "")
        objectives = request.form.get("objectives", "")
        materials = request.form.get("materials", "")

        prompt = f"""
        Create a detailed and structured lesson plan for a {grade} class on the subject: {subject}.
        Align the content with the exams: {exam_text}. I want the lesson plan to not sound like AI and to be 
        very encompassing. Feel free to search the web.

        Topics to be covered:
        {topics}

        Learning Objectives:
        {objectives}

        Instructional Materials to be used:
        {materials}

        The lesson plan should include:
        - Lesson Objectives (rephrased and organized if needed)
        - Prescribed learning outcomes (short-term and long-term)
        - Before the lesson (materials to prepare, including links to useful videos, images, or mind maps)
        - Materials needed
        - Engage (an engaging introduction)
        - Explore (main lesson content)
        - Closure (recap of key points or in-class activity based on exams)
        - Reflection (3 bullets: what learner knew before, knows now, and should know)
        - Take-home assignment (3 versions: high, medium, and low ability learners)
        """

        try:
            response = client.complete(
                messages=[
                    SystemMessage(""),
                    UserMessage(prompt),
                ],
                temperature=1,
                top_p=1,
                model=model
            )
            output = response.choices[0].message.content

        except Exception as e:
            output = f"An error occurred: {str(e)}"

    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)