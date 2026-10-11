# Mobbin Offline Saver

Save any Mobbin page (flows, screens, an app's page) as **one `.html` file** that keeps working with no internet:

- Every screenshot is embedded inside the file. Nothing loads from the web.
- Each flow gets its own row with **‹ / ›** buttons to slide left and right.
- Click any screen (or **Slideshow ▶** / **Play all ▶**) to open a full-screen slideshow:
  - **‹ / ›** buttons, **← / →** arrow keys, **swipe** on phones and tablets
  - Thumbnail strip, screen counter, Home/End, Esc to close; it wraps from the last screen back to the first

Try `demo.html` (open it directly, offline) to see the viewer.

## How to save a page

Mobbin only shows flows to logged-in users, so you run this in **your own browser** while logged in.

### Option A: Console (simplest)
1. Log in to Mobbin and open the page, e.g.
   `https://mobbin.com/apps/unify-web-2db7c674-f6a1-44be-8e9b-ad96bc225c11/3aeec56b-6264-4443-bba7-eecd6f04a2a2/flows`
2. Press `F12` (Mac: `Cmd+Opt+J`) → **Console** tab.
3. Paste the whole contents of `save-mobbin-page.js` and press **Enter**.
   (Chrome may ask you to type `allow pasting` first.)
4. Wait (about a minute for 100+ screens) and don't scroll yourself. A box at the bottom-right shows progress, such as "found 64 of 110 screens in 7 flows".
   It scrolls the whole page and every flow's slider, collecting screens as they appear.
   - If every flow's count matches (e.g. "4 screens" → 4 found), it downloads `…-offline.html` automatically.
   - If something is missing, the box lists those flows. Scroll to them yourself (they're picked up automatically), then press **Save now**.

### Option B: Bookmarklet (one click next time)
1. Create a new bookmark.
2. Paste the full contents of `bookmarklet.txt` as the bookmark's URL.
3. On any Mobbin page, click the bookmark.

## Notes
- Open the saved file by double-clicking it. It works in any modern browser, on desktop and phone, with no internet.
- If the progress box reports images that "could not be embedded", those few will only show when you're online. Run the saver again if that happens.
- Each flow keeps its own slider, named from the caption under it on Mobbin (e.g. "Connecting to Gmail from Onboarding · 4 screens").
  Mobbin's menu previews and the "More like …" suggestions from other apps are left out.
- A screen that appears in several flows is kept in each of them.
- Saved with an older version? `node fix-saved-file.js your-file.html` cleans it up. Re-running the saver gets you the complete set of flows, though.
- The saved file is for your personal reference. Mobbin's content belongs to Mobbin and the app makers, so don't republish it.

## Development
`node build.js` regenerates `bookmarklet.txt` and `demo.html` from `save-mobbin-page.js`.
