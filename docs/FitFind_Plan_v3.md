# FitFind — Project Plan v3

**Shop any aesthetic. Paste a TikTok or upload a screenshot — get shoppable results.**

Project Planning Document • Summer 2025 • Josh • Solo Project

| 12 Weeks | 5 Phases | 2 APIs (MVP) | Vercel + Render |
|:---:|:---:|:---:|:---:|

---

## Project Summary

FitFind lets you paste a TikTok or Instagram URL — or upload a screenshot — and returns shoppable fashion results matching the detected outfit and aesthetic. The core insight: the platforms where trends actually live have locked APIs, but publicly visible video content is processable via yt-dlp. FitFind bridges that gap.

The pipeline: video frame extraction → Gemini Vision (clothing detection + style classification in one call) → two result sections (Exact Items and Related Items) with sort and filter controls. Pinterest is scoped post-launch. Everything runs local-first; Vercel + Render deploy for a live portfolio URL.

### Core Pipeline

| Input | Frame Extract | Gemini Vision | Classification | Results |
|:---:|:---:|:---:|:---:|:---:|
| URL or Screenshot | yt-dlp key frames | Clothing item detection | Aesthetic label | Exact + Related sections |

---

## 1. Core Features

### 1.1 URL Input — Shop from a TikTok or Instagram Post

The primary entry point. The user pastes a public TikTok or Instagram URL. yt-dlp extracts the video server-side, the backend samples 3–5 key frames, and the full CV pipeline runs on the best frame.

- Paste any public TikTok or Instagram URL
- Backend uses yt-dlp to download and sample 3–5 key frames automatically
- Gemini Vision analyzes the best frame: detects individual clothing items and infers the overall aesthetic in a single API call
- Detected items shown as tags above results (e.g. "oversized hoodie", "cargo pants")
- Aesthetic label displayed as a badge (e.g. "Gorpcore", "Quiet Luxury")
- Results split into two sections: Exact Items and Related Items
- Sort and price filter controls apply to both sections

### 1.2 Screenshot / Image Upload

Secondary entry point for saved screenshots, Pinterest images, or photos of outfits where the user has an image but not a URL. Runs the same pipeline as URL input.

- Drag-and-drop or file picker upload (JPG, PNG, WEBP)
- Same Gemini Vision pipeline — detection + classification in one call
- Detected items and aesthetic badge shown above results, identical to URL flow
- Error states handled: unsupported file type, no clothing detected, API failure

### 1.3 Results — Two Sections

Both sections are populated from the same Gemini output and render on one results page. Sorting and filtering apply to both without re-running the pipeline.

| Section | What it shows | Query strategy |
|---|---|---|
| **Exact Items** | Products matching the specific clothing items Gemini detected — the actual hoodie, the actual cargo pants. Closest match to what was literally in the source. | Detected item names as individual search queries |
| **Related Items** | Products that match the detected aesthetic more broadly — items that fit the vibe even if they weren't in the source. Expands the shoppable universe. | Aesthetic label as a style search query |

### 1.4 Sorting & Filtering

All sort and filter operations are applied server-side in FastAPI before results are returned. This keeps the frontend simple and reduces client-side computation.

| Control | Options | Implementation note |
|---|---|---|
| **Sort by** | Relevance (default), Price: Low–High, Price: High–Low, Popularity, Newest | Passed as a sort_by param to the RapidAPI endpoint. Check in Week 1 which sort values the API actually supports — remove any that aren't available |
| **Price Range** | Min / Max input fields | Server-side filter applied after the API response. If the API supports price params natively, pass them directly; otherwise filter the response array in FastAPI |
| **Section Toggle** | Show/hide Exact Items and Related Items independently | Client-side only — no API call needed. Simple show/hide state in the frontend |

### 1.5 Product Cards

- Product image, brand name, item name, price
- Section badge indicating Exact or Related
- Buy button — external link to retailer site (opens in new tab)
- Graceful fallback if price is missing — show "See price" rather than crashing

### MVP Scope

| IN SCOPE | OUT OF SCOPE |
|---|---|
| ✓ URL input → yt-dlp frame extraction | ✗ Pinterest API integration (post-launch) |
| ✓ Screenshot / image upload | ✗ Automated trend feed / trend scoring |
| ✓ Gemini Vision: clothing detection + style classification | ✗ User accounts, saved items, wishlists |
| ✓ Exact Items section (specific detected items) | ✗ Mobile app (iOS/Android) |
| ✓ Related Items section (aesthetic-matched) | ✗ Affiliate monetization |
| ✓ Sort by: relevance, price, popularity, newest | ✗ Private / authenticated social content |
| ✓ Price range filter | ✗ Real-time social media scraping |
| ✓ Deployed live URL (Vercel + Render) | |

---

## 2. Technical Architecture

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Next.js + TypeScript | Web app UI — pages, routing, API calls. New to both. Runs on localhost:3000. TypeScript catches type mismatches at build time, which is especially useful when learning the codebase. |
| **Styling** | Tailwind CSS | Utility-first CSS. Ships with Next.js by default. Focus on functional layout first — polish later. |
| **Backend** | Python + FastAPI | CV pipeline endpoints, product search logic, API orchestration. Runs on localhost:8000. Interactive API docs auto-generated at localhost:8000/docs — use this instead of Postman. |
| **Frame Extraction** | yt-dlp + OpenCV | yt-dlp downloads the video (no API key needed). OpenCV samples key frames. RoboMaster CV experience applies directly here — same cv2.VideoCapture pattern. |
| **CV + Classification** | Gemini Vision API (free tier) | Single API call per frame: detects clothing items AND classifies aesthetic. Returns structured JSON. Free tier: 15 requests/min, 1500/day — plenty for dev with caching. |
| **Product Data** | RapidAPI — Real-Time Product Search | Product listings, prices, images, buy links. Powers both Exact Items and Related Items via different query strings. Free tier with caching. |
| **Database** | SQLite → Supabase | SQLite locally — just a file, zero setup. Swap to Supabase free tier for deployment. Schema is identical; only the connection string changes. |
| **Hosting** | Vercel + Render | Vercel for Next.js (free). Render for FastAPI (free). Personal portfolio URL — no scale config needed. |

### Folder Structure

Set this up on day one. Everything has a fixed home so you never have to decide where something goes mid-build.

| Path | What goes here |
|---|---|
| `frontend/app/page.tsx` | Home page — URL input + image upload |
| `frontend/app/results/page.tsx` | Results page — Exact + Related sections, sort/filter controls |
| `frontend/app/layout.tsx` | Global layout — nav bar, shared wrappers |
| `frontend/components/ProductCard.tsx` | Reusable product card component |
| `frontend/components/SortFilter.tsx` | Sort dropdown + price range inputs |
| `frontend/components/DetectedTags.tsx` | Clothing item tags + aesthetic badge |
| `frontend/lib/api.ts` | All fetch calls to FastAPI — one file, nowhere else |
| `frontend/types/index.ts` | Shared TypeScript types (Product, AnalysisResult, etc.) |
| `backend/main.py` | FastAPI app entry point — all route definitions |
| `backend/services/frame_extractor.py` | yt-dlp download + OpenCV frame sampling |
| `backend/services/gemini_service.py` | Gemini Vision API calls + JSON normalization |
| `backend/services/query_builder.py` | Builds exact and related query strings |
| `backend/services/product_service.py` | RapidAPI calls + sorting + filtering + normalization |
| `backend/models/schemas.py` | Pydantic models — request/response shapes |
| `backend/db/cache.py` | SQLite caching logic |

### How the Two Sections Use the Same API

- Both Exact Items and Related Items call the same RapidAPI endpoint
- Exact Items query: built from detected item names — e.g. "oversized cargo pants streetwear"
- Related Items query: built from the aesthetic label — e.g. "gorpcore fashion outfit"
- product_service.py is called twice per request with different query strings and tags each result with its section
- Both calls are cached independently in SQLite — same query string = no repeat API call

### API Key Security

- Both Gemini and RapidAPI keys live in `backend/.env` only
- The Next.js frontend never calls Gemini or RapidAPI directly — it only calls localhost:8000
- Keys are never exposed in browser network requests or client-side code
- `frontend/.env.local` holds only `NEXT_PUBLIC_API_URL=http://localhost:8000` — safe to expose

### Example Gemini Response

```json
{
  "items": ["oversized hoodie", "cargo pants", "chunky sneakers"],
  "aesthetic": "gorpcore",
  "confidence": 0.91
}
```

---

## 3. Development Phases & Timeline

Five phases ordered to reduce risk: foundation and prototypes first, then the hardest technical piece (CV pipeline), then product data, then frontend, then polish. 12 weeks total. Each phase has clear exit criteria — do not move on until they are met.

| Phase | Wks | Focus | Deliverable |
|---|:---:|---|---|
| 1 — Research & Setup | 1–2 | Repo scaffold, env setup, API key validation, prototype scripts for all three tools | All tools confirmed working in isolation |
| 2 — CV Pipeline | 3–5 | Frame extraction service, Gemini integration, prompt engineering, query builders | Full pipeline: URL/image → structured JSON output |
| 3 — Product Data | 6–7 | RapidAPI integration, normalization, sort/filter, caching, /results endpoint | Both result sections returning real data |
| 4 — Frontend | 8–10 | Next.js pages, components, wired to backend, sort/filter UI, error states | Complete UI functional end-to-end |
| 5 — Polish & Deploy | 11–12 | Bug fixes, Supabase swap, Vercel + Render deploy, README, demo video | Live public URL, clean repo |

---

## PHASE 1 — Research & Setup `Weeks 1–2`

The goal of Phase 1 is to have zero surprises in Phase 2. Every external tool — yt-dlp, Gemini, RapidAPI — gets validated in isolation before you build anything around it. Do not skip this. A broken API key or an unexpected response shape discovered in Week 4 is far more disruptive than discovering it in Week 1.

### Week 1 — Environment & Repo

- Create the folder structure: `fitfind/frontend/` and `fitfind/backend/` — set this up exactly as defined in the folder structure table above
- Initialize Next.js frontend: `npx create-next-app@latest frontend --typescript --tailwind --eslint --app`
  - When prompted: yes to TypeScript, yes to Tailwind, yes to App Router, no to src directory
  - Confirm it runs: `npm run dev` → localhost:3000 should show the Next.js welcome page
- Initialize FastAPI backend: `python3 -m venv venv`, install fastapi, uvicorn, python-dotenv, yt-dlp, opencv-python, google-generativeai, requests
  - Create a minimal `main.py` with a `/health` endpoint and CORS middleware configured for localhost:3000
  - Confirm it runs: `uvicorn main:app --reload` → localhost:8000/health should return `{"status": "ok"}`
- Set up `.gitignore`: include `.env`, `.env.local`, `venv/`, `node_modules/`, `__pycache__/`, `.next/`
- Create `.env.example` listing `GEMINI_API_KEY` and `RAPIDAPI_KEY` as empty — commit this, never commit the real `.env`
- Get Gemini API key from Google AI Studio (aistudio.google.com) — free tier, no payment info needed
- Confirm RapidAPI key works against the Real-Time Product Search endpoint

### Week 2 — Prototype All Three Tools in Isolation

Write three separate scratch scripts (`test_ytdlp.py`, `test_gemini.py`, `test_rapidapi.py`) in the backend folder. These are not production code — they exist purely to confirm each tool works and to document what it actually returns.

**yt-dlp prototype — what to confirm:**
- Paste a real public TikTok URL. Does it download without error?
- Use `cv2.VideoCapture` to open the downloaded file and sample 3 frames at even intervals
- Save them as `/tmp/frame_0.jpg`, `frame_1.jpg`, `frame_2.jpg` and open them — are they clear frames from the video?
- Test an Instagram URL too. Note any differences in behavior
- Test a private account URL — confirm it throws a `DownloadError` you can catch

**Gemini prototype — what to confirm:**
- Send one of the saved frames to Gemini Vision with a prompt asking for clothing items and aesthetic
- Is the response valid JSON or does it wrap in markdown code fences? Document this — your normalization layer needs to handle whatever format it returns
- Try 5 different frame images: a streetwear outfit, a formal outfit, a non-fashion image (landscape), a blurry frame, and a frame with no people
- Document: what does Gemini return when there's no clothing? What does confidence look like across different images?
- Test the exact prompt you plan to use in Phase 2 — does it return consistent JSON structure?

**RapidAPI prototype — what to confirm:**
- Make a test call with query "oversized gorpcore hoodie" — print the full response
- Write down the actual field names the API returns (e.g. `product_title`, `product_photos`, `typical_price_range`) — your normalization layer maps to these
- Check which `sort_by` values the API actually accepts — confirm relevance, price low-high, price high-low. Note if popularity and newest are supported
- Check if it accepts `min_price` / `max_price` params natively or if you need to filter the response yourself
- Make a second call with a broader aesthetic query like "gorpcore fashion outfit" — do the results feel meaningfully different from the item-specific query?
- Note the free tier rate limits from the response headers

**Other Week 2 tasks:**
- Define TypeScript types in `frontend/types/index.ts` based on what the APIs actually return — do this now so Phase 4 can use them
- Write out all page routes and component names for Phase 4 — lock this list
- Finalize and lock the MVP feature list — no scope changes after this week

> **Exit Criteria:** yt-dlp downloads a real TikTok URL and you can extract 3 frames. Gemini returns clothing labels from a test frame and you know whether it returns clean JSON or markdown-wrapped JSON. RapidAPI returns real product data and you have documented the exact field names. All three tools confirmed in isolation. Repo scaffolded with both apps running.

> **Watch out:** The most common Week 1 failure is discovering the RapidAPI endpoint doesn't support the sort options you planned for. Confirm this now. If popularity and newest aren't available, remove them from the sort dropdown before building the UI around them.

---

## PHASE 2 — CV Pipeline `Weeks 3–5`

The most technically complex phase and the heart of the app. Your OpenCV/Python experience from IEEE RAS applies directly — frame sampling with `cv2.VideoCapture` is the same pattern you used in the RoboMaster detection pipeline. The new piece is the Gemini API integration and the prompt engineering required to get consistent structured output.

### Week 3 — Frame Extraction Service

Build `frame_extractor.py` as a standalone service module. It has two public functions: one for URLs, one for image uploads. Both return the same type — a list of JPEG bytes — so the Gemini service doesn't need to know where the input came from.

**`extract_frames_from_url(url: str) → list[bytes]`**
- Use `yt_dlp.YoutubeDL` with `format: 'worst'` (lowest quality is fine for CV, faster to download)
- Download to a `tempfile.TemporaryDirectory` so the video file is cleaned up automatically on exit
- Use `cv2.VideoCapture` to read the downloaded file
- Sample 5 frames at evenly spaced intervals: `frame_idx = int((i / num_frames) * total_frames)`
- Encode each frame as JPEG bytes with `cv2.imencode('.jpg', frame)` and append to results list
- Wrap the yt-dlp call in `try/except yt_dlp.utils.DownloadError` — raise a `ValueError` with a clean message

**`extract_frames_from_image(file: UploadFile) → list[bytes]`**
- Read the file contents and return as a single-item list — matches the same return type as URL extraction

**FastAPI endpoints to add in `main.py`:**
- `POST /analyze-url` — accepts `{ url: string }`, calls `extract_frames_from_url`
- `POST /analyze-image` — accepts a multipart file upload, calls `extract_frames_from_image`
- Both endpoints return `{ frame_count: int }` for now — Gemini gets wired in Week 4
- Test both endpoints at localhost:8000/docs before moving on

### Week 4 — Gemini Vision Integration

Build `gemini_service.py`. The most important work this week is prompt engineering — getting Gemini to return consistent, parseable JSON every time. Expect to iterate on the prompt multiple times. Do not move on until you have consistent output across at least 10 different test images.

**`analyze_frames(frames: list[bytes]) → AnalysisResult`**
- Loop through frames, send each to Gemini, collect results
- Pick the result with the highest confidence score as the final output
- Wrap each call in `try/except` — skip bad frames and continue rather than crashing

**The Gemini prompt — key requirements:**
- Instruct it to return ONLY a JSON object with no markdown, no code fences, no preamble
- Specify the exact JSON schema: `{ items: [string], aesthetic: string, confidence: float }`
- Give it a fixed list of valid aesthetic values to choose from (streetwear, casual, y2k, gorpcore, quiet luxury, minimalist, preppy, grunge, cottagecore, dark academia, athleisure, coastal, business casual, formal)
- Tell it to be specific with item names: "oversized hoodie" not "top", "wide leg cargo pants" not "pants"
- Tell it to return `items: []` if no clothing or people are visible

**Normalization layer — handles Gemini's response inconsistencies:**
- Strip markdown code fences if present: if `raw.startswith("```")` strip everything outside the JSON
- Wrap `json.loads()` in `try/except` — if parsing fails, raise a `ValueError` with the raw response truncated to 100 chars for debugging
- Validate the parsed object has the expected keys before returning

**Other Week 4 tasks:**
- Add `AnalysisResult` as a Pydantic model in `schemas.py`: `items: list[str]`, `aesthetic: str`, `confidence: float`
- Wire Gemini into the `/analyze-url` and `/analyze-image` endpoints — they should now return the full `AnalysisResult`
- Unit test with at least 10 different outfit images: streetwear, formal, y2k, athleisure, no-people image, blurry frame, multiple people, partial outfit visible

### Week 5 — Query Builders & Full Pipeline Integration

Build `query_builder.py` and wire everything together. At the end of this week, a single POST to `/analyze-url` returns detected items, aesthetic label, and both query strings ready for the product API.

**`build_exact_queries(items: list[str]) → list[str]`**
- Takes the detected item list and returns one search query string per item
- Limit to the top 3 items to avoid rate limit pressure from too many product API calls
- e.g. `["oversized hoodie", "cargo pants", "chunky sneakers"]` → `["oversized hoodie streetwear", "cargo pants wide leg", "chunky sneakers"]`

**`build_related_query(aesthetic: str) → str`**
- Maps each aesthetic label to a handcrafted search query that returns good product results
- e.g. gorpcore → "gorpcore outdoor fashion", y2k → "y2k fashion outfit", quiet luxury → "quiet luxury minimal clothing"
- Include a fallback for unexpected aesthetics: `f"{aesthetic} fashion outfit"`

**Other Week 5 tasks:**
- Update `/analyze-url` and `/analyze-image` endpoints to return: `{ analysis: AnalysisResult, exact_queries: list[str], related_query: str }`
- Test the full pipeline end-to-end with 20+ real TikTok/Instagram URLs:
  - Paste URLs spanning different aesthetics — streetwear, formal, y2k, gorpcore, casual
  - Check: are the detected items specific enough to produce useful product queries?
  - Check: does the aesthetic label match what you'd expect from the outfit?
  - Fix the worst failures by adjusting the prompt or the query builder mappings
  - Timebox this: ship what works and move to Phase 3. You can tune accuracy later

> **Exit Criteria:** POST a TikTok URL to `/analyze-url` and receive structured JSON containing detected clothing items, aesthetic classification, confidence score, exact query strings, and related query string. POST an image to `/analyze-image` and get the same output. Pipeline runs end-to-end on 20+ test inputs even if some results are imperfect.

> **Watch out:** Gemini will sometimes return items that are too generic ("top", "pants") despite prompt instructions. If this happens consistently, add examples to the prompt: "Instead of 'top' say 'oversized graphic tee'. Instead of 'pants' say 'wide leg cargo pants'." Few-shot examples in the prompt are often more effective than instructions alone.

---

## PHASE 3 — Product Data & Results Layer `Weeks 6–7`

With the CV pipeline working and outputting clean query strings, this phase builds the product layer: calling RapidAPI, normalizing the response, applying sort/filter, caching results, and exposing a single `/results` endpoint the frontend will call.

### Week 6 — RapidAPI Integration, Normalization & Caching

**`product_service.py` — `search_products()` function:**
- Parameters: `query: str`, `section: str`, `sort: str`, `min_price: float`, `max_price: float`, `limit: int = 12`
- Calls the RapidAPI Real-Time Product Search endpoint with the query and sort params
- Applies price filtering — either via API params if supported, or by filtering the response array
- Returns a list of normalized `Product` objects tagged with their section ("exact" or "related")

**Normalization layer — `_normalize(raw: dict, section: str) → Product`:**
- Use the exact field names you documented in Week 2 from the prototype
- Price: the API likely returns it as a string like "$49.99" — strip the dollar sign and cast to float, return `None` if it fails
- Image URL: some products have multiple images — take the first one
- Set brand to empty string if missing — never let a missing field crash the normalization

**`_is_valid(raw: dict) → bool`:** only include products that have at minimum a title and an image

**`SORT_MAP` dict:** maps your sort option strings ("relevance", "price_asc", etc.) to the API's accepted `sort_by` values — only include sort options the API actually supports

**`cache.py` — SQLite caching:**
- `init_db()` — creates `results_cache` table on startup if it doesn't exist
- `make_key(query, sort, min_price, max_price) → str` — MD5 hash of the combined params
- `get_cached(key) → list | None` and `set_cached(key, results)` — serialize results as JSON
- Call `init_db()` once at the top of `main.py` so the table is always ready

### Week 7 — /results Endpoint & Edge Case Handling

**`/results` endpoint in `main.py`:**
- Accepts: `{ exact_queries: list[str], related_query: str, sort: str, min_price: float, max_price: float }`
- For each exact query string: check cache, call `search_products` if not cached, tag results as "exact"
- For the related query string: check cache, call `search_products` if not cached, tag results as "related"
- Merge exact results from all queries into a single `exact_items` list (deduplicate by product id if the same item appears from multiple queries)
- Returns: `{ exact_items: list[Product], related_items: list[Product] }`

**Edge cases — never let these crash the endpoint:**
- Empty `exact_items` or `related_items` — return an empty list, not an error
- RapidAPI timeout — catch `requests.Timeout`, return empty list for that section
- RapidAPI non-200 response — log the status code, return empty list
- Zero valid products after normalization — return empty list

**Testing the full backend flow at localhost:8000/docs:**
- Step 1: POST `/analyze-url` with a TikTok URL → copy the `exact_queries` and `related_query` from the response
- Step 2: POST `/results` with those values + `sort: "relevance"`, `min_price: 0`, `max_price: 500`
- Confirm both sections return real products with images and prices
- Test with `sort: "price_asc"` and confirm results are actually sorted low to high
- Test with `max_price: 50` and confirm expensive items are filtered out
- Use any remaining time to tune the Gemini prompt and query builder mappings based on real test results

> **Exit Criteria:** POST `/results` with real query strings returns both `exact_items` and `related_items` populated with real product data. Sort and price filter params work correctly. All edge cases (empty results, timeout) handled without crashing. Everything independently testable at localhost:8000/docs before the frontend touches it.

> **Watch out:** The Exact vs. Related sections returning near-identical results is the most common Phase 3 problem. If both sections look the same, your query strings are too similar. Exact queries should name specific items ("cargo pants wide leg"). Related queries should name aesthetics ("gorpcore fashion"). If they still overlap, try adding brand qualifiers or gender terms to the exact queries to push them further apart.

---

## PHASE 4 — Frontend `Weeks 8–10`

Build the entire user-facing application in Next.js. You're new to Next.js and TypeScript — the approach here is to keep it functional and learn as you go. The backend is already tested and working, so the frontend's only job is to call the right endpoints and display the data correctly.

### Next.js Fundamentals to Know Before Starting

- **App Router:** each folder inside `app/` is a URL route. `app/page.tsx` = "/". `app/results/page.tsx` = "/results". Create a page by exporting a default function from `page.tsx`
- **"use client":** add this at the top of any component that uses `useState`, `useEffect`, or browser events. Without it, Next.js treats the component as server-rendered and `useState` won't work
- **TypeScript basics needed:** `type Product = { name: string, price: number | null }`. When you see a red underline, read the error — TypeScript will usually tell you exactly what type it expects
- **Tailwind basics needed:** `className="flex gap-4 p-8 text-sm font-bold text-gray-500"`. Read the Tailwind docs for any class you don't know — they're well documented

### Week 8 — Scaffold, Types & Home Page

**`frontend/types/index.ts`:**
- Create all shared types: `Product`, `AnalysisResult`, `ResultsResponse`, `SortOption`
- These should match exactly what the backend returns (confirmed in Phase 3)

**`frontend/lib/api.ts` — all fetch calls to FastAPI:**
- `analyzeUrl(url: string)` — POST `/analyze-url`, returns analysis + query strings
- `analyzeImage(file: File)` — POST `/analyze-image` using FormData, returns same shape
- `getResults(exactQueries, relatedQuery, sort, minPrice, maxPrice)` — POST `/results`, returns `exact_items` + `related_items`
- All functions throw an `Error` with the backend's error message on non-200 responses

**`app/page.tsx` — home page:**
- URL input: a text field + submit button. On submit: call `analyzeUrl()`, store the response in `sessionStorage`, navigate to `/results`
- Image upload: a file input (or drag-and-drop div). On file select: call `analyzeImage()`, store the response in `sessionStorage`, navigate to `/results`
- Loading state: disable both inputs and show "Analyzing…" while the API call is in flight
- Error state: show the error message below the input if the call fails

**`components/ProductCard.tsx`:** takes a `Product` prop, renders image, brand, name, price, section badge, buy button

### Week 9 — Results Page, Sections & Sort/Filter

**`app/results/page.tsx`:**
- On mount: read the stored analysis data from `sessionStorage`. If missing, redirect to home
- Call `getResults()` with the stored query strings and current sort/filter state
- Show detected item tags and aesthetic badge at the top
- Render the Exact Items section: heading, subtitle ("Items detected directly from the source"), product grid
- Render the Related Items section: heading, subtitle ("More items matching the [aesthetic] aesthetic"), product grid
- Show empty state text if a section has no results ("No exact items found") rather than showing nothing

**`components/SortFilter.tsx`:**
- Sort dropdown with the options your backend supports (confirmed in Week 2)
- Min/max price inputs with an Apply button
- When sort changes: re-call `getResults()` with the new sort value
- When Apply is clicked: re-call `getResults()` with the new price range

**Other Week 9 tasks:**
- Loading state: while `getResults()` is in flight, show skeleton cards (`div` with `animate-pulse` and a gray background) in both sections
- Section toggle: a simple show/hide checkbox or button for each section — client-side only, no API call

### Week 10 — Image Upload Polish & Error Handling

**Polish the image upload component:**
- Add drag-and-drop: listen for `dragover` and `drop` events on a styled div, extract the file from the drop event
- Show a file preview thumbnail after the user selects an image
- Validate file type client-side before sending: reject non-JPG/PNG/WEBP immediately with a clear message

**Harden all error states:**
- Private account URL: show "This video isn't publicly accessible"
- No clothing detected: show "No clothing items found in this image. Try a different photo"
- API failure: show "Something went wrong. Try again" with a retry button
- Empty results for both sections: show "No products found for this look. Try a different image"

**Final check:**
- Ensure both entry points feel unified — the results page should look and behave identically regardless of whether the input was a URL or an image upload
- Walk through the complete user flow end-to-end from both entry points with 5 different inputs each

> **Exit Criteria:** Both entry points are functional end-to-end. Both result sections display real data. Sort and price filter controls work and re-fetch correctly. All error states display clean messages. A complete user flow works from paste/upload through to clicking a buy button on a product.

> **Watch out:** `sessionStorage` is cleared when the tab is closed. If a user refreshes the results page, they'll be redirected to home. This is expected behavior for an MVP — don't try to fix it with `localStorage` or a database this phase. Just make sure the redirect to home happens cleanly rather than showing a broken results page.

---

## PHASE 5 — Polish & Deploy `Weeks 11–12`

### Week 11 — Bug Fixes & Cleanup

- Walk through every user flow and log all bugs — fix functionality issues before visual issues
- Add loading states anywhere a fetch is in flight and they're currently missing
- Add empty states anywhere a section can be empty and currently shows nothing
- Ensure the backend handles all edge cases gracefully: private URLs, API timeouts, malformed images, completely empty results
- Clean up the codebase: remove unused imports, dead code, test scripts. Add comments where the logic is non-obvious
- Write a startup script (`start.sh`) that launches both servers with one command
- Run `npm run build` in the frontend — fix any TypeScript compile errors before attempting to deploy

### Week 12 — Deploy & Document

**Deploy FastAPI backend to Render:**
- Push repo to GitHub if not already done
- New Web Service on Render — connect repo, set root directory to `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
- Add environment variables: `GEMINI_API_KEY` and `RAPIDAPI_KEY`
- Note: SQLite on Render's free tier uses ephemeral disk — the cache resets on redeploy. This is acceptable for a portfolio project. If you want persistence, swap to Supabase: same schema, update the connection string via SQLAlchemy

**Deploy Next.js frontend to Vercel:**
- New Project on Vercel — import from GitHub, set root directory to `frontend`
- Add environment variable: `NEXT_PUBLIC_API_URL=https://your-render-url.onrender.com`
- Update CORS in `main.py` to allow your Vercel URL in addition to localhost:3000
- Deploy and visit the live URL

**Post-deploy checklist:**
- Run a full end-to-end test on the live URL — not just locally. Both entry points, both result sections, sort and filter
- Write the README: what the project does, how to run locally, tech stack, live URL, known limitations
- Add `.env.example` listing all required keys
- Record a 2–3 minute demo video: paste a TikTok URL, show detected items and aesthetic badge, scroll through Exact and Related sections, demonstrate sort and price filter, upload a screenshot and show the same flow

> **Exit Criteria:** Both entry points work end-to-end on the live Vercel URL. Both result sections populate correctly with working sort and filter. Project runs cleanly from a fresh clone using only the `.env.example` as a guide. README, demo video, and clean GitHub repo with live link ready for job applications.

---

## 4. Key Risks & Mitigations

| Risk | Why It Matters | Mitigation |
|---|---|---|
| **yt-dlp breaks on platform update** | Primary URL input method stops working temporarily | yt-dlp is actively maintained and usually patched within days of a platform change. Pin a working version in requirements.txt and update on a schedule. Acceptable risk for a personal project. |
| **Gemini returns inconsistent JSON** | If the normalization layer can't parse the response, the whole pipeline fails | Invest time on the prompt in Week 4. The normalization layer strips markdown fences and validates keys. Log the raw response on parse failure so you can debug quickly. Add a fallback: if confidence < 0.5, surface the item list and let the user manually pick an aesthetic. |
| **Exact vs. Related sections overlap** | Both sections return near-identical results, making the distinction feel pointless | Confirmed in Phase 3 Week 7. Keep query strategies meaningfully different: exact uses item names, related uses aesthetic labels. If overlap persists, add modifiers to exact queries to push them further apart. |
| **RapidAPI sort options limited** | Popularity and Newest sort may not be available on the free tier | Confirmed in Week 2. Remove any unsupported sort options from the dropdown before building the UI around them. |
| **Free tier rate limits hit** | Development slows down as API calls are throttled or blocked | SQLite caching in Phase 3 prevents repeat calls for the same query. Gemini free tier resets monthly. Monitor rate limit headers in responses. |
| **TypeScript errors block Vercel deploy** | `npm run build` fails on type errors that didn't surface in development | Run `npm run build` locally at the end of Week 11 before attempting to deploy. Fix all type errors then. |
| **Scope creep** | Adding features mid-build stretches the project past summer | Feature list locked at end of Phase 1. New ideas go to Section 5 only. Pinterest is already the model for this — scoped post-launch and hasn't slipped back in. |

---

## 5. Ideas for Later

Ordered by technical interest. None of these are in scope for the summer MVP.

| # | Idea | Description |
|:---:|---|---|
| 1 | **Pinterest Integration** | The natural next API addition. Shoppable pins as a third result section. Requires app approval, an icon, a deployed URL, and a privacy policy page — straightforward to add once the core product is live. |
| 2 | **Outfit Builder** | Let users combine detected items from multiple inputs into one saved outfit, then shop the whole look at once. |
| 3 | **Trend Feed** | Parse Reddit fashion communities (r/streetwear, r/femalefashionadvice) or fashion RSS feeds to auto-surface rising aesthetic keywords — feeds the classification layer automatically. |
| 4 | **Video Reel Input** | Accept a longer video reel, sample more frames, and surface the most commonly detected aesthetic across all frames rather than just the best single frame. |
| 5 | **Saved Looks** | Use SQLite to let users bookmark result sets locally — a lightweight wishlist without needing accounts. |
| 6 | **Custom CV Model** | Fine-tune a clothing classifier on the DeepFashion dataset instead of relying on Gemini Vision — a strong ML portfolio addition and the obvious next step after the MVP. |

---


FitFind is a stronger portfolio piece than a standard visual-search app because the creative angle is defensible: nobody cleanly solves "paste a TikTok, shop the aesthetic" for a general audience. The two-section results model (Exact Items vs. Related Items) adds product thinking that goes beyond basic CV demos.


