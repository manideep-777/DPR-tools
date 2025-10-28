# 🛠️ Getting Started - Copy-Paste Ready Code

## Part 1: FastAPI Backend Setup

### Step 1: Create project structure

```bash
mkdir dpr-generator
cd dpr-generator
mkdir backend frontend
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Step 2: Install dependencies

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv google-generativeai python-jose[cryptography] pydantic python-multipart
```

### Step 3: Create `.env` file

```
DATABASE_URL=postgresql://user:password@localhost:5432/dpr_db
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your-super-secret-key-here-make-it-long
ALGORITHM=HS256
```

### Step 4: Create `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MSME DPR Generator API")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "API is running"}

@app.get("/api/test-gemini")
async def test_gemini():
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, write 50 words about business planning")
    return {"status": "ok", "response": response.text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Step 5: Test your backend

```bash
python main.py
# Visit: http://localhost:8000/docs (Swagger UI)
# Visit: http://localhost:8000/api/health
```

---

## Part 2: PostgreSQL Setup

### Option A: Local PostgreSQL (Development)

```bash
# Mac (using Homebrew):
brew install postgresql
brew services start postgresql

# Windows: Download installer from postgresql.org
# Linux (Ubuntu/Debian):
sudo apt-get install postgresql postgresql-contrib
```

### Option B: Railway (Easy, Cloud-based)

1. Go to https://railway.app
2. Create new project
3. Add PostgreSQL
4. Copy connection string to `.env` as `DATABASE_URL`

---

## Part 3: Create Database Models

Create `models.py`:

```python
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class DPRForm(Base):
    __tablename__ = "dpr_forms"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    business_name = Column(String)
    sector = Column(String)
    investment_amount = Column(Float)
    number_of_employees = Column(Integer)
    location = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="draft")  # draft, generating, completed

class DPRContent(Base):
    __tablename__ = "dpr_content"
    
    id = Column(Integer, primary_key=True, index=True)
    dpr_form_id = Column(Integer, index=True)
    executive_summary = Column(Text)
    market_analysis = Column(Text)
    financial_projections = Column(Text)
    government_schemes = Column(Text)
    pdf_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Part 4: Create API Endpoints

Create `routers/dpr.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import DPRForm, DPRContent, get_db
from pydantic import BaseModel
import google.generativeai as genai
import os

router = APIRouter(prefix="/api", tags=["dpr"])

class DPRFormData(BaseModel):
    business_name: str
    sector: str
    investment_amount: float
    number_of_employees: int
    location: str
    description: str

@router.post("/dpr/create")
async def create_dpr(data: DPRFormData, db: Session = Depends(get_db)):
    # Save form data
    dpr_form = DPRForm(
        user_id=1,  # TODO: Get from JWT token
        business_name=data.business_name,
        sector=data.sector,
        investment_amount=data.investment_amount,
        number_of_employees=data.number_of_employees,
        location=data.location,
        description=data.description,
        status="generating"
    )
    db.add(dpr_form)
    db.commit()
    db.refresh(dpr_form)
    
    # Generate content with Gemini
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    
    # Generate executive summary
    summary_prompt = f"""
    Write a professional executive summary (200 words) for a business plan:
    - Business: {data.business_name}
    - Sector: {data.sector}
    - Investment: ₹{data.investment_amount}
    - Employees: {data.number_of_employees}
    - Location: {data.location}
    - Description: {data.description}
    """
    
    summary_response = model.generate_content(summary_prompt)
    executive_summary = summary_response.text
    
    # Generate market analysis
    market_prompt = f"""
    Write market analysis (300 words) for {data.sector} sector in {data.location}:
    - Current market size
    - Growth potential
    - Competition overview
    - Customer demand
    """
    
    market_response = model.generate_content(market_prompt)
    market_analysis = market_response.text
    
    # Save content
    dpr_content = DPRContent(
        dpr_form_id=dpr_form.id,
        executive_summary=executive_summary,
        market_analysis=market_analysis,
        government_schemes="",  # TODO: Add scheme matching logic
        financial_projections=""  # TODO: Add financial modeling
    )
    db.add(dpr_content)
    db.commit()
    
    # Update status
    dpr_form.status = "completed"
    db.commit()
    
    return {
        "id": dpr_form.id,
        "status": "success",
        "content": {
            "executive_summary": executive_summary,
            "market_analysis": market_analysis
        }
    }

@router.get("/dpr/{dpr_id}")
async def get_dpr(dpr_id: int, db: Session = Depends(get_db)):
    content = db.query(DPRContent).filter(DPRContent.dpr_form_id == dpr_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="DPR not found")
    return content
```

---

## Part 5: Frontend Setup (Next.js)

```bash
cd ../frontend
npx create-next-app@latest . --typescript --tailwind

# When prompted:
# - Would you like to use TypeScript? → Yes
# - Would you like to use Tailwind CSS? → Yes
# - Would you like to use the app/ directory? → Yes
```

### Create `app/components/DPRForm.tsx`:

```typescript
'use client';

import { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export default function DPRForm() {
  const [formData, setFormData] = useState({
    business_name: '',
    sector: '',
    investment_amount: '',
    number_of_employees: '',
    location: '',
    description: ''
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/dpr/create`, {
        ...formData,
        investment_amount: parseFloat(formData.investment_amount),
        number_of_employees: parseInt(formData.number_of_employees)
      });

      setResult(response.data);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate DPR');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow">
      <h1 className="text-3xl font-bold mb-6">MSME DPR Generator</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Business Name</label>
          <input
            type="text"
            name="business_name"
            value={formData.business_name}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border rounded-lg"
            placeholder="Your business name"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Sector</label>
          <select
            name="sector"
            value={formData.sector}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border rounded-lg"
          >
            <option value="">Select sector...</option>
            <option value="food">Food Processing</option>
            <option value="textiles">Textiles</option>
            <option value="manufacturing">Manufacturing</option>
            <option value="it">IT Services</option>
            <option value="retail">Retail</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Investment Amount (₹)</label>
          <input
            type="number"
            name="investment_amount"
            value={formData.investment_amount}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border rounded-lg"
            placeholder="Amount in rupees"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Number of Employees</label>
          <input
            type="number"
            name="number_of_employees"
            value={formData.number_of_employees}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border rounded-lg"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Location</label>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border rounded-lg"
            placeholder="City/District"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Business Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            rows={4}
            className="w-full px-4 py-2 border rounded-lg"
            placeholder="Describe your business idea..."
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Generating DPR...' : 'Generate DPR'}
        </button>
      </form>

      {result && (
        <div className="mt-8 bg-green-50 p-6 rounded-lg">
          <h2 className="text-2xl font-bold mb-4">Generated DPR Content</h2>
          
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-2">Executive Summary</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{result.content.executive_summary}</p>
          </div>

          <div>
            <h3 className="text-xl font-semibold mb-2">Market Analysis</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{result.content.market_analysis}</p>
          </div>

          <button className="mt-6 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700">
            Download as PDF
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## Part 6: Run Everything

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py
# Visit: http://localhost:8000/docs

# Terminal 2: Frontend
cd frontend
npm run dev
# Visit: http://localhost:3000
```

---

## What You Just Built

✅ FastAPI backend running  
✅ PostgreSQL connected  
✅ Gemini API integrated  
✅ Next.js frontend displaying form  
✅ Working end-to-end flow  

**Next: Add PDF generation, improve UI, deploy to Vercel + Railway**

---

## Next Development Steps

1. **Add PDF Generation**:
   ```bash
   pip install reportlab weasyprint
   ```

2. **Add File Upload to Cloudinary**:
   ```bash
   pip install cloudinary
   ```

3. **Add Authentication**:
   ```bash
   pip install python-jose python-passlib bcrypt
   ```

4. **Deploy**:
   - Vercel: `vercel` (from frontend folder)
   - Railway: Connect your GitHub repo

---

## Development Best Practices

- Commit to GitHub regularly
- Test features as you build
- Keep frontend simple and responsive
- Use FastAPI auto-docs at `/docs` for debugging
- Leverage free tiers effectively

**Build with quality and confidence.** 🚀

Good luck! 💪
