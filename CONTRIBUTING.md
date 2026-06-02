# 🤝 Contributing to Climate Shield

Thank you for your interest in contributing to **Climate Shield**.

We welcome contributions that improve:

* Climate risk analysis
* Weather intelligence
* Frontend design
* AI chatbot features
* Performance and scalability
* Documentation and deployment

---

# 📌 Before You Start

Please:

* Read the README carefully
* Check existing issues and pull requests
* Keep contributions focused and clean
* Follow the project structure

---

# 🚀 Getting Started

## 1️⃣ Fork the Repository

Click the **Fork** button on GitHub.

---

## 2️⃣ Clone Your Fork

```bash id="8u8e6g"
git clone https://github.com/your-username/Climate-Shield.git

cd Climate-Shield
```

---

## 3️⃣ Create Virtual Environment

### Windows

```bash id="d7czhs"
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash id="mfe0ll"
python3 -m venv venv

source venv/bin/activate
```

---

## 4️⃣ Install Dependencies

```bash id="pp8e1x"
pip install -r requirements.txt
```

---

## 5️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```env id="j9p4qq"
OPENWEATHER_API_KEY=your_api_key_here
```

Get a free API key from:

https://openweathermap.org/api

---

# 📂 Project Structure

```bash id="c5kz4k"
Climate-Shield/
├── AI-chatbot/
├── backend/
├── Frontend/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── requirements.txt
```

---

# 🌱 Creating a Branch

Create a new feature branch before making changes:

```bash id="q4f7tw"
git checkout -b feature/your-feature-name
```

Examples:

* `feature/chatbot-improvements`
* `feature/flood-visualization`
* `fix/api-error`

---

# 🛠 Contribution Guidelines

## ✅ Code Style

* Use meaningful variable names
* Keep functions modular
* Write readable code
* Add comments where necessary

---

## ✅ Frontend Guidelines

* Keep UI responsive
* Maintain existing design consistency
* Avoid unnecessary libraries
* Use clean animations

---

## ✅ Backend Guidelines

* Handle exceptions properly
* Validate API responses
* Avoid hardcoded secrets
* Keep APIs lightweight

---

# 🔐 Security Rules

## NEVER commit:

* `.env`
* API keys
* secret credentials
* tokens

Make sure `.gitignore` includes:

```gitignore id="c4klne"
.env
__pycache__/
venv/
```

---

# 🧪 Testing

Before submitting:

* Test frontend interactions
* Test weather analysis
* Test chatbot responses
* Verify deployment locally

---

# 📤 Submitting Changes

## ⭐ Star the repo 

---

## 1️⃣ Commit Changes

```bash id="9s5a2m"
git add .

git commit -m "Add: short description"
```

---

## 2️⃣ Push Changes

```bash id="9q4y0k"
git push origin feature/your-feature-name
```

---

## 3️⃣ Open Pull Request

Create a Pull Request describing:

* What changed
* Why it was added
* Screenshots (if UI changes)

---

# 🐞 Reporting Bugs

When reporting bugs include:

* Error message
* Steps to reproduce
* Screenshots/logs
* Browser/OS information

---

# 💡 Suggested Contributions

You can contribute:

* Better weather analytics
* ML prediction models
* Interactive maps
* Notification systems
* Mobile responsiveness
* Accessibility improvements
* Performance optimizations
* Documentation improvements

---

# 🌍 Vision

Climate Shield aims to make climate awareness:

* accessible
* intelligent
* real-time
* community-driven

Your contributions help improve disaster preparedness and climate awareness for everyone.

---

# ⭐ Thank You

Thank you for supporting Climate Shield. Please Star the repo

Together we can build smarter climate resilience systems.
