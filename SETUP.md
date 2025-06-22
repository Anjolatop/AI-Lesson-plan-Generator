# Setup Guide for AI Lesson Plan Generator

## 🚀 Quick Setup

### 1. Install Dependencies
All required modules have been installed. You can verify by running:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with the following content:

```env
# Flask Secret Key (you can generate a random one)
SECRET_KEY=your-super-secret-key-change-this-in-production

# Azure AI Configuration
# You need to get a GitHub token from: https://github.com/settings/tokens
GITHUB_TOKEN=your-github-token-here

# Optional: Azure endpoint and model (these have defaults)
AZURE_ENDPOINT=https://models.github.ai/inference
AZURE_MODEL=openai/gpt-4.1
```

### 3. Get a GitHub Token

To enable AI features, you need a GitHub token:

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a name like "AI Lesson Plan Generator"
4. Select scopes: `read:user` and `repo` (if needed)
5. Copy the generated token
6. Replace `your-github-token-here` in the `.env` file with your actual token

### 4. Run the Application

```bash
python app.py
```

The application will be available at: http://localhost:5000

## 🔧 Alternative: Set Environment Variables in PowerShell

If you prefer to set environment variables directly in PowerShell:

```powershell
$env:SECRET_KEY="your-super-secret-key-change-this-in-production"
$env:GITHUB_TOKEN="your-github-token-here"
python app.py
```

## 🎯 What Works Without AI

Even without the GitHub token, you can:
- ✅ Register and login users
- ✅ Access the dashboard
- ✅ View the beautiful UI
- ✅ Navigate through all pages
- ❌ Generate lesson plans (requires AI token)

## 🆘 Troubleshooting

### "AI service is not available" Error
This means your `GITHUB_TOKEN` is not set or invalid. Make sure:
1. The `.env` file exists in the project root
2. The `GITHUB_TOKEN` value is correct
3. The token has the necessary permissions

### "Module not found" Errors
Run this to install all dependencies:
```bash
pip install -r requirements.txt
```

### Database Issues
The SQLite database will be created automatically when you first run the app.

## 📱 Testing the Application

1. **Without AI Token**: You can test the UI and user management
2. **With AI Token**: You can create actual lesson plans

The application is fully functional for UI testing even without the AI token! 