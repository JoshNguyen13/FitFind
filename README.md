# FitFind

Paste a TikTok or Instagram URL (or upload a screenshot) and FitFind identifies every clothing item in the video and surfaces shoppable product results.

## How it works

1. **Analyze** — yt-dlp downloads the video; OpenCV samples 10 frames across the full duration. All frames are sent to Gemini Vision in a single request, which returns a list of detected clothing items and an aesthetic label.
2. **Select** — A checkbox page shows every item Gemini detected. Pick what you want to shop for.
3. **Shop** — Serper (Google Shopping) fetches real product results for each selected item. Results are split into *Exact Items* (matched directly from the video) and *More Picks* (aesthetic-matched suggestions).

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, Tailwind CSS v4 |
| Backend | FastAPI, Python |
| Vision | Gemini 2.5 Flash (`google-genai`) |
| Video | yt-dlp + OpenCV |
| Shopping | Serper.dev Google Shopping API |
| Cache | SQLite (Gemini results + Serper results cached separately) |

## Local setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```
GEMINI_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
GEMINI_FRAMES=10
```

```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Deployment

### Backend (Render)

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `GEMINI_API_KEY`, `SERPER_API_KEY`, `GEMINI_FRAMES`, `FRONTEND_URL` (your Vercel URL)

### Frontend (Vercel)

- Environment variable: `NEXT_PUBLIC_API_URL` (your Render backend URL)

## API limits

| Service | Free tier |
|---|---|
| Gemini 2.5 Flash | 20 requests / day |
| Serper.dev | 2,500 credits total (1 credit per query) |

Gemini results are cached by URL so repeat analyses don't cost a call. Serper results are cached by query + sort + price range.
