# 🤖 LLM-Powered Browser Automation for NBTC

This is a **much simpler** approach to browser automation using AI/LLM to intelligently interact with web pages instead of hardcoding selectors!

## ✨ Why This is Better

❌ **Old approach**: 700+ lines of complex selectors that break when UI changes
✅ **New approach**: AI looks at screenshots and finds elements like humans do

## 🚀 Quick Setup

### 1. Get an API Key

Choose one:

**Option A: Claude (Anthropic) - Recommended**
- Go to https://console.anthropic.com/
- Create API key
- Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`

**Option B: GPT (OpenAI)**
- Go to https://platform.openai.com/api-keys
- Create API key
- Add to `.env`: `OPENAI_API_KEY=your_key_here`

### 2. Install Browser

```bash
# Only needed once
uv run python -m playwright install chromium
```

### 3. Run It!

```bash
# Activate virtual environment and run
source .venv/bin/activate
python llm_browser_automation.py
```

## 🎯 How It Works

1. **Takes Screenshots**: Captures what's on screen
2. **Asks AI**: "Where is the login button in this image?"
3. **Gets Smart Answer**: AI provides the exact selector
4. **Clicks Intelligently**: Uses AI-suggested selectors
5. **Falls Back Gracefully**: Has backup logic if AI fails

## 🔧 Key Features

- **🧠 AI Vision**: Actually "sees" the webpage like humans
- **🌐 Thai Language Support**: Understands Thai text in UI
- **🛡️ Cloudflare Handling**: Built-in bypass capabilities
- **🔄 Adaptive**: Works even when website changes
- **📸 Debug Screenshots**: Saves images for troubleshooting
- **⚡ Fallback Logic**: Works even without API keys

## 📋 Example Usage

Instead of writing complex selectors:
```python
# Old way - brittle!
element = page.wait_for_selector('xpath=//a[contains(text(), "การตรวจสอบมาตรฐานการแพร่")]')

# New way - intelligent!
agent.smart_click("การตรวจสอบมาตรฐานการแพร่")
```

## 🎮 Commands

```bash
# Basic run
python llm_browser_automation.py

# With debug info
python llm_browser_automation.py --verbose

# Test connection only
python -c "from llm_browser_automation import LLMBrowserAgent; agent = LLMBrowserAgent(); print('Ready!')"
```

## 🔍 Troubleshooting

**No API Key?**
- Script will work in "fallback mode" with basic selectors
- But AI mode is much more reliable!

**Screenshots not clear?**
- The script saves `.png` files for debugging
- Check `current_page.png`, `form_page.png` etc.

**Still stuck on element?**
- AI will try multiple approaches automatically
- Much better than manual selector hunting!

## 💡 Pro Tips

1. **Start Simple**: Let AI handle the complex parts
2. **Check Screenshots**: Look at saved images if something fails
3. **Use Descriptive Names**: "login button" works better than "button"
4. **Thai is OK**: AI understands "การตรวจสอบ" perfectly

## 🎉 Benefits

- **90% less code** than manual selector approach
- **Self-healing** when website UI changes
- **Human-readable** task descriptions
- **Future-proof** automation

This approach turns browser automation from a nightmare of brittle selectors into simple, natural language instructions that AI can execute reliably! 🚀