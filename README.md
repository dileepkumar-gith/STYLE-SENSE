# STYLE-SENSE
StyleSense – AI Fashion Advisor

An intelligent AI-powered fashion advisor that generates personalized outfit recommendations, realistic AI fashion images, smart color suggestions, and direct shopping links — all tailored to your profile, location, season, and occasion.

StyleSense combines Vision AI, Large Language Models, and Image Generation AI to create a complete fashion styling experience.

🚀 Features
🤖 AI-Powered Outfit Recommendations

Personalized suggestions based on:

Gender

Age

Height & Body Size

Skin Tone

Country & Season

Occasion & Time

Budget Range

Powered by Groq LLaMA models

🎨 Smart Color Suggestions

Country-specific palettes

Season-aware combinations

Occasion-based styling

Custom color input option

Climate & culture-aware recommendations

🖼 AI Image Generation

Generates ultra-realistic fashion visuals

Full-body outfit representation

Fashion magazine-quality styling

Powered by Google Imagen models

👁 Vision Analysis

Upload your image

Detects skin tone & body shape

Provides AI-enhanced styling insights

🛍 Shopping Links Integration

Auto-generates price-filtered links for:

Amazon India

Flipkart

Ajio

Meesho

Links are automatically filtered according to your selected budget.

🌍 Multi-Country Support

Supports styling for:

United States

India

United Kingdom

Eurozone

Japan

Canada

Australia

🧠 AI Models Used
Google Gemini

Vision Analysis: gemini-2.0-flash / gemini-1.5-pro

Image Generation: imagen-4.0-generate-001 / imagen-3.0-generate-001

Groq

Outfit Recommendation Engine:

llama-3.3-70b-versatile

llama-3.1-70b-versatile

🛠 Tech Stack

Frontend: Streamlit

LLM Engine: Groq (LLaMA 3.3 70B)

Vision AI: Google Gemini

Image Generation: Google Imagen

Image Processing: Pillow, OpenCV

Data Handling: NumPy, JSON

📂 Project Structure
stylesense-ai/
│
├── app.py               # Main Streamlit application
├── requirements.txt     # Dependencies
├── .env.example         # API key template
└── README.md            # Documentation
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/yourusername/stylesense-ai.git
cd stylesense-ai
2️⃣ Create Virtual Environment (Recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Configure API Keys

Create a .env file in the root directory:

GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key

Get API keys from:

Google AI Studio

Groq

▶️ Run the Application
streamlit run app.py

Open in browser:

http://localhost:8501
🧑‍💻 How It Works

Enter personal details

Select country, season & occasion

Choose suggested or custom colors

Upload your photo (optional but recommended)

Generate outfit

View AI image + shopping links

🔮 Future Enhancements

Virtual Try-On

Brand-based size recommendations

Outfit history saving

Social media sharing

Trend-based AI styling

Cross-platform price comparison

Real-time stock tracking

📜 License

This project is licensed under the MIT License.

🙌 Credits

Built with Streamlit

Powered by Google Gemini

LLM Engine by Groq

Integrated with major Indian e-commerce platforms

📌 Version

Version: 2.0
Status: Active Development
Last Updated: February 2026
