# Bureaucracy Navigator Agent - Simple Setup Guide

## 🚀 Quick Start for Beginners

This guide will help you set up the Bureaucracy Navigator Agent on your computer, even if you're not a technical expert.

## 📋 What You'll Need

### Required Software (Free)
1. **Docker Desktop** - A tool that runs applications in containers
2. **Git** - A tool to download the project code
3. **API Keys** - Two free API keys for AI features

### Optional but Recommended
- **VS Code** - A code editor (free)
- **Basic understanding of using command prompt/terminal**

---

## 🔧 Step 1: Install Docker Desktop

### What is Docker?
Think of Docker as a magic box that contains everything the application needs to run. You don't have to install databases, Python, or other complicated software separately.

### How to Install:

**For Windows:**
1. Go to https://www.docker.com/products/docker-desktop/
2. Click "Download for Windows"
3. Run the downloaded file (Docker Desktop Installer.exe)
4. Follow the installation wizard (click "Next" on all screens)
5. Restart your computer when prompted
6. After restart, Docker Desktop will start automatically

**For Mac:**
1. Go to https://www.docker.com/products/docker-desktop/
2. Click "Download for Mac"
3. Open the downloaded file (Docker.dmg)
4. Drag Docker to your Applications folder
5. Open Docker from Applications
6. Follow the setup instructions

**How to Check if Docker is Working:**
1. Open Command Prompt (Windows) or Terminal (Mac)
   - **Windows**: Press `Win + R`, type `cmd`, press Enter
   - **Mac**: Press `Cmd + Space`, type `Terminal`, press Enter
2. Type: `docker --version`
3. If you see version information, Docker is working!

---

## 🔑 Step 2: Get API Keys

You need two API keys to make the AI features work. Both have free tiers.

### 2.1 OpenAI API Key (for ChatGPT features)

1. Go to https://platform.openai.com/
2. Click "Sign up" (create a free account)
3. After signing up, go to https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Give it a name like "Bureaucracy Navigator"
6. Copy the key (it starts with `sk-...`)
7. Save it somewhere safe (you'll need it later)

### 2.2 SerpAPI Key (for web search)

1. Go to https://serpapi.com/
2. Click "Sign up" (free account)
3. After signing up, go to your dashboard
4. Find your API key (it's on the main dashboard)
5. Copy the key
6. Save it with your OpenAI key

---

## 📥 Step 3: Download the Project

### What is Git?
Git is a tool that downloads code from the internet. It's like a special download manager for code.

### How to Install Git:

**Windows:**
1. Go to https://git-scm.com/download/win
2. Download and run the installer
3. Click "Next" on all screens (use default settings)

**Mac:**
1. Open Terminal and type: `git --version`
2. If it's not installed, it will prompt you to install it

### How to Download the Project:

1. Open Command Prompt (Windows) or Terminal (Mac)
2. Navigate to where you want to save the project:
   ```bash
   # For Windows (saves to your Desktop)
   cd Desktop
   
   # For Mac (saves to your Desktop)
   cd ~/Desktop
   ```
3. Download the project:
   ```bash
   git clone https://github.com/your-username/Bureaucracy_Navigator.git
   ```
4. Go into the project folder:
   ```bash
   cd Bureaucracy_Navigator
   ```

---

## ⚙️ Step 4: Configure the Application

### 4.1 Create Environment File

1. In your project folder, find the file called `.env.example`
2. Make a copy of it and rename the copy to `.env`
3. **Windows**: Right-click on `.env.example` → Copy → Right-click → Paste → Rename to `.env`
4. **Mac**: In Terminal, type: `cp .env.example .env`

### 4.2 Add Your API Keys

1. Open the `.env` file with any text editor (Notepad, VS Code, etc.)
2. Find these lines:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SERPAPI_KEY=your_serpapi_key_here
   ```
3. Replace them with your actual API keys:
   ```
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   SERPAPI_KEY=your-actual-serpapi-key-here
   ```
4. Save the file and close it

---

## 🚀 Step 5: Start the Application

This is the exciting part! We'll use Docker to start everything automatically.

### 5.1 Start All Services

1. Make sure Docker Desktop is running on your computer
2. In your Command Prompt/Terminal (still in the Bureaucracy_Navigator folder), run:
   ```bash
   docker-compose up -d
   ```
3. Wait for 2-5 minutes while it downloads and starts everything
4. You'll see lots of text - that's normal!

### 5.2 Check if Everything is Working

1. Open your web browser
2. Go to: http://localhost:3000
3. You should see the Bureaucracy Navigator interface!

### 5.3 Initialize Demo Data

1. In your Command Prompt/Terminal, run:
   ```bash
   docker-compose exec backend python app/core/demo_data.py
   ```
2. This adds sample data so you can test the system immediately

---

## 🎯 Step 6: Test the Application

### Try These Sample Questions:

1. **Income Certificate**: Type "Apply for income certificate in Telangana"
2. **Driving License**: Type "How to get driving license"
3. **Document Upload**: Click the Documents tab and upload a PDF or image

### What You Should See:
- The AI will create a step-by-step plan
- You can track progress in the Tasks tab
- Upload documents in the Documents tab
- Chat with the AI assistant

---

## 🔧 Common Issues & Solutions

### Problem: "Docker command not found"
**Solution**: Make sure Docker Desktop is installed and running. Restart your computer.

### Problem: "Port already in use"
**Solution**: Something else is using port 3000 or 8000. Try:
```bash
docker-compose down
docker-compose up -d
```

### Problem: "API key error"
**Solution**: Check your `.env` file. Make sure the API keys are correct and have no extra spaces.

### Problem: "Can't access localhost:3000"
**Solution**: Wait 2-3 minutes after starting Docker. Sometimes it needs time to initialize.

---

## 📱 How to Use the Application

### Main Features:

1. **Chat Tab** 💬
   - Ask questions about government procedures
   - The AI creates automatic plans
   - Example: "Apply for income certificate"

2. **Tasks Tab** 📋
   - See all your ongoing tasks
   - Track progress
   - Retry failed tasks

3. **Documents Tab** 📄
   - Upload PDFs or images
   - AI extracts text automatically
   - Use documents in your applications

### Sample Workflow:

1. **Start a Request**: In Chat, type "Apply for income certificate"
2. **Review Plan**: The AI shows you step-by-step instructions
3. **Track Progress**: Check Tasks tab to see what's completed
4. **Upload Documents**: Add required documents in Documents tab
5. **Get Help**: Ask follow-up questions in Chat

---

## 🔄 Stopping and Starting

### To Stop the Application:
```bash
docker-compose down
```

### To Start Again:
```bash
docker-compose up -d
```

### To View Logs (if something goes wrong):
```bash
docker-compose logs -f
```
Press `Ctrl + C` to stop viewing logs

---

## 📞 Getting Help

If you run into issues:

1. **Check the logs**: Run `docker-compose logs` to see error messages
2. **Restart everything**: `docker-compose down` then `docker-compose up -d`
3. **Check API keys**: Make sure they're correctly entered in `.env`
4. **Ensure Docker is running**: Check Docker Desktop is open

---

## 🎉 Success!

You've successfully set up the Bureaucracy Navigator Agent! 

**What you now have:**
- ✅ A working AI assistant for government procedures
- ✅ Document upload and processing
- ✅ Task tracking and progress monitoring
- ✅ A complete system running on your computer

**Next steps:**
- Try different government procedure questions
- Upload some documents to test the parser
- Explore the task management features

The system is now ready to help you navigate government bureaucracy efficiently! 🏛️
