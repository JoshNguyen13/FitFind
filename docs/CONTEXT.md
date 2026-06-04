# FitFind — Project Context for Claude Code

## What this project is
Full-stack fashion discovery app. User pastes a TikTok/Instagram URL or uploads a screenshot → Gemini Vision detects clothing items and classifies the aesthetic → RapidAPI returns shoppable product results in two sections (Exact Items and Related Items).

## Current status
Phase 3 complete. Full backend built end-to-end: frame extraction → Gemini → query builder → RapidAPI → /results. Starting Phase 4 (frontend) next.

## Tech stack
- Frontend: Next.js + TypeScript + Tailwind (in /frontend)
- Backend: Python + FastAPI (in /backend)
- CV: yt-dlp for frame extraction, Gemini Vision API for detection + classification
- Products: RapidAPI Real-Time Product Search
- DB: SQLite locally (Supabase on deploy)

## Key decisions made
- Gemini model: gemini-2.5-flash (only free tier model available on this key)
- RapidAPI response structure: products are at data.data.products (not data directly)
- RapidAPI sort options that work: LOWEST_PRICE, HIGHEST_PRICE, TOP_RATED (BEST_MATCH broken, NEWEST returns 400)
- Price is at offer.price (string like "$84.00"), fallback is typical_price_range[0]
- Purchase URL is at offer.offer_page_url (not product_page_url which goes to Google Shopping)
- Filter out products under $5 (LOWEST_PRICE returns junk like $0.01 results)
- Pinterest deferred to post-launch

## RapidAPI field mapping
- id → product_id
- name → product_title
- price → offer.price (strip $ and cast to float)
- image_url → product_photos[0]
- purchase_url → offer.offer_page_url
- brand → first word of product_title (no dedicated brand field)

## File structure
See FitFind_Plan_v3.md in this folder for the full folder structure and phase plan.