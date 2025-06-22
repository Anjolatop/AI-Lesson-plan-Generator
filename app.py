from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your-secret-key-here")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lesson_plans.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database setup
db = SQLAlchemy(app)

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Azure GPT-4.1 setup (conditional)
client = None
try:
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential
    
    endpoint = os.getenv("AZURE_ENDPOINT", "https://models.github.ai/inference")
    model = os.getenv("AZURE_MODEL", "openai/gpt-4.1")
    token = os.getenv("GITHUB_TOKEN")
    
    if token:
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(token)
        )
    else:
        print("Warning: GITHUB_TOKEN not found. AI features will be disabled.")
except ImportError as e:
    print(f"Warning: Azure AI modules not available. AI features will be disabled. Error: {e}")
except Exception as e:
    print(f"Warning: Failed to initialize Azure client. AI features will be disabled. Error: {e}")

# Demo lesson plan generator
def generate_demo_lesson_plan(grade, subject, exam_text, topics, objectives, materials):
    return f"""
# Lesson Plan: {subject} - {grade}

## Lesson Objectives
- Students will understand the key concepts of {topics.split(',')[0] if topics else subject}
- Students will be able to apply their knowledge to solve related problems
- Students will develop critical thinking skills through hands-on activities

## Prescribed Learning Outcomes

### Short-term Outcomes:
- Students can define and explain key terms
- Students can complete basic exercises independently
- Students can participate in class discussions

### Long-term Outcomes:
- Students develop a deeper understanding of {subject}
- Students can apply concepts to real-world situations
- Students build confidence in their academic abilities

## Before the Lesson
### Materials to Prepare:
- {materials if materials else 'Textbook, whiteboard, markers, worksheets'}
- Digital resources: Educational videos and interactive simulations
- Assessment materials for formative evaluation

### Useful Resources:
- Khan Academy videos on {subject}
- Interactive online simulations
- Mind maps for visual learners

## Materials Needed
- {materials if materials else 'Textbook, notebooks, pens, whiteboard, markers'}
- Digital devices for online resources
- Worksheets and assessment materials

## Engage (Introduction - 10 minutes)
Begin with an engaging question: "How does {topics.split(',')[0] if topics else subject} relate to our everyday lives?"
- Show a short video clip or demonstration
- Ask students to share their prior knowledge
- Create excitement about the topic

## Explore (Main Content - 30 minutes)
### Activity 1: Direct Instruction (15 minutes)
- Present key concepts using visual aids
- Use real-world examples to illustrate points
- Encourage student questions and discussion

### Activity 2: Hands-on Practice (15 minutes)
- Students work in pairs or small groups
- Complete guided practice exercises
- Teacher circulates to provide support

## Closure (Recap - 10 minutes)
- Review key points learned today
- Connect back to learning objectives
- Preview what's coming next lesson
- Quick formative assessment

## Assessment
### Higher Ability Learner:
- Research project on advanced {subject} topics
- Create a presentation or report
- Explore connections to other subjects

### Medium Ability Learner:
- Complete practice problems from textbook
- Write a summary of key concepts
- Prepare questions for next lesson

### Lower Ability Learner:
- Review class notes and highlight key points
- Complete simplified practice exercises
- Create flashcards for important terms

## Reflection
### What learner knew before:
- Basic understanding of {subject} concepts
- Some familiarity with related topics

### What learner knows now:
- Detailed understanding of {topics if topics else subject}
- Ability to apply concepts practically
- Confidence in their knowledge

### What learner should know:
- How to extend learning independently
- Connections to other subjects
- Real-world applications

## Notes for Teacher
- Monitor student engagement throughout the lesson
- Provide additional support where needed
- Adjust pace based on student understanding
- Prepare extension activities for fast learners
"""

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lesson_plans = db.relationship('LessonPlan', backref='user', lazy=True)

class LessonPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    exams = db.Column(db.String(200), nullable=False)
    topics = db.Column(db.Text, nullable=False)
    objectives = db.Column(db.Text, nullable=False)
    materials = db.Column(db.Text, nullable=False)
    generated_plan = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template("register.html")
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template("register.html")
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/dashboard")
@login_required
def dashboard():
    lesson_plans = LessonPlan.query.filter_by(user_id=current_user.id).order_by(LessonPlan.created_at.desc()).all()
    return render_template("dashboard.html", lesson_plans=lesson_plans)

@app.route("/create_lesson", methods=["GET", "POST"])
@login_required
def create_lesson():
    if request.method == "POST":
        grade = request.form.get("grade", "")
        subject = request.form.get("subject", "")
        exams = request.form.getlist("exam")
        exam_text = ", ".join(exams)
        topics = request.form.get("topics", "")
        objectives = request.form.get("objectives", "")
        materials = request.form.get("materials", "")
        title = request.form.get("title", f"{subject} - {grade}")

        if client:
            # Use real AI with more encompassing prompt
            prompt = f"""
            Create a comprehensive, detailed, and highly structured lesson plan for a {grade} class on the subject: {subject}.
            Align the content with the exams: {exam_text}. 
            
            You should also search for instructional materials such as: {materials}, which are in line with the grade, subject, and exam type given.
            
            The lesson plan should be very encompassing and include:
            
            **Lesson Objectives** (rephrased and organized if needed):
            - Clear, measurable learning objectives
            - Specific skills and knowledge students will acquire
            - Alignment with curriculum standards
            
            **Prescribed Learning Outcomes** (both short-term and long-term):
            - What students will achieve by the end of the lesson
            - What they will be able to do in the future
            - How this connects to broader educational goals
            
            **Before the Lesson** (materials to prepare):
            - Specific resources, videos, images, or mind maps
            - Links to useful educational content
            - Preparation checklist for the teacher
            - Digital and physical materials needed
            
            **Materials Needed**:
            - Complete list of all required materials
            - Technology requirements
            - Student and teacher resources
            
            **Instructional Sequence**:
            - **Engage**: An engaging introduction that hooks students
            - **Explore**: Main lesson content with detailed activities
            - **Closure**: Recap of key points and assessment
            
            **Assessment** (three versions for different ability levels):
            - Higher Ability Learner: Advanced, challenging tasks
            - Medium Ability Learner: Standard practice and application
            - Lower Ability Learner: Basic reinforcement and support
            
            **Reflection** (three key areas):
            - What learner knew before: Prior knowledge assessment
            - What learner knows now: Current understanding
            - What learner should know: Future learning goals
            
            Make the lesson plan comprehensive, engaging, and practical and the content should be specific to the scheme of work and past questions of the exams: {exam_text}. Include specific examples, activities, and resources that teachers can immediately use in their classrooms. The content should be detailed enough that a substitute teacher could follow it effectively.
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
                generated_plan = response.choices[0].message.content
            except Exception as e:
                flash(f"AI service error: {str(e)}. Using demo mode instead.", 'warning')
                generated_plan = generate_demo_lesson_plan(grade, subject, exam_text, topics, objectives, materials)
        else:
            # Use demo mode
            flash('AI service not available. Using demo mode with sample lesson plan.', 'info')
            generated_plan = generate_demo_lesson_plan(grade, subject, exam_text, topics, objectives, materials)

        # Save to database
        lesson_plan = LessonPlan(
            title=title,
            grade=grade,
            subject=subject,
            exams=exam_text,
            topics=topics,
            objectives=objectives,
            materials=materials,
            generated_plan=generated_plan,
            user_id=current_user.id
        )
        db.session.add(lesson_plan)
        db.session.commit()

        return render_template("lesson_result.html", lesson_plan=lesson_plan)

    return render_template("create_lesson.html")

@app.route("/lesson/<int:lesson_id>")
@login_required
def view_lesson(lesson_id):
    lesson_plan = LessonPlan.query.get_or_404(lesson_id)
    if lesson_plan.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    return render_template("lesson_result.html", lesson_plan=lesson_plan)

@app.route("/edit_lesson/<int:lesson_id>", methods=["GET", "POST"])
@login_required
def edit_lesson(lesson_id):
    lesson_plan = LessonPlan.query.get_or_404(lesson_id)
    if lesson_plan.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        lesson_plan.generated_plan = request.form.get("edited_plan")
        db.session.commit()
        flash('Lesson plan updated successfully!', 'success')
        return redirect(url_for('view_lesson', lesson_id=lesson_id))
    
    return render_template("edit_lesson.html", lesson_plan=lesson_plan)

@app.route("/feedback/<int:lesson_id>", methods=["POST"])
@login_required
def feedback(lesson_id):
    lesson_plan = LessonPlan.query.get_or_404(lesson_id)
    if lesson_plan.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    satisfaction = request.form.get("satisfaction")
    feedback_text = request.form.get("feedback_text", "")
    
    if satisfaction == "satisfied":
        flash('Thank you for your feedback! Your lesson plan is ready to use.', 'success')
        return redirect(url_for('view_lesson', lesson_id=lesson_id))
    else:
        flash('We\'ll use your feedback to improve future lesson plans. You can edit this one manually.', 'info')
        return redirect(url_for('edit_lesson', lesson_id=lesson_id))

@app.route("/delete_lesson/<int:lesson_id>", methods=["POST"])
@login_required
def delete_lesson(lesson_id):
    lesson_plan = LessonPlan.query.get_or_404(lesson_id)
    if lesson_plan.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    db.session.delete(lesson_plan)
    db.session.commit()
    flash('Lesson plan deleted successfully', 'success')
    return redirect(url_for('dashboard'))

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)