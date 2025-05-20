from flask import Flask, render_template, request
import openai
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    output = None
    if request.method == "POST":
        grade = request.form["grade"]
        subject = request.form["subject"]
        exams = request.form.getlist("exam")
        exam_text = ", ".join(exams)
        topics = request.form["topics"]
        objectives = request.form["objectives"]
        materials = request.form["materials"]

        prompt = f"""
        Create a detailed and structured lesson plan for a {grade} class on the subject: {subject}.
        Align the content with the exams : {exam_text}. I want the lesson plan to not sound like ai and to be 
        very encompassing. fel free to search 

        Topics to be covered:
        {topics}

        Learning Objectives:
        {objectives}

        Instructional Materials to be used:
        {materials}

        The lesson plan should include:
        - Lesson Objectives (rephrased and organized if needed)
        - Prescribed learning outcomes (short-term learnign outcomes and long-term learnig outcomes)
        - Before the lesson (things to prepare, should include instructional materials, maybe links to useful videos on Youtube, images, mind maps)
        - Materials needed)
        - Engage (Lesson Introduction: an interesting way to begin the lesson to grab learners attention)
        - Explore: Main Content to be taught
        - Closure: Closure for the lesson: short recap of important points or class exercise and in-class excercise modelling past questions from the exam type or types specified earlier
        - Reflection: Three bullet points: What learner knew before, what learner knows after lesson, what learner should know
        - Take-home assignment:Three models of this should be provided: one for the high- ability learner, another for the medium ability learner, another for the low ability learner
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        output = response.choices[0].message.content

    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)