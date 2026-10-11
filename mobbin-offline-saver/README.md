# Mobbin Offline Saver

Save any Mobbin page (flows, screens, an app's page) as **one `.html` file** that keeps working with no internet:

- Every screenshot is embedded inside the file. Nothing loads from the web.
- Each flow gets its own row with **‹ / ›** buttons to slide left and right.
- Click any screen (or **Slideshow ▶** / **Play all ▶**) to open a full-screen slideshow:
  - **‹ / ›** buttons, **← / →** arrow keys, **swipe** on phones and tablets
  - Thumbnail strip, screen counter, Home/End, Esc to close; it wraps from the last screen back to the first

Try `demo.html` (open it directly, offline) to see the viewer.

## How to save a page

Mobbin only shows flows to logged-in users, so this runs in **your own browser** while you're logged in.

### Chrome extension (recommended)
**Install once:**
1. Get the `extension` folder onto your computer: unzip `mobbin-offline-saver-extension.zip`, or download this repo and use `mobbin-offline-saver/extension`.
   Keep the folder somewhere permanent, because Chrome loads it from there.
2. Open `chrome://extensions` and turn on **Developer mode** (top right).
3. Click **Load unpacked** and pick the `extension` folder.
4. Click the puzzle-piece icon in the toolbar and **pin** "Mobbin Offline Saver".

**Use it whenever you want:**
1. Log in to Mobbin and open any app's **Flows** page (or its Screens page).
2. Click the extension's button, or press **Alt+Shift+S**.
3. Leave the page alone (about a minute per 100 screens). A box at the bottom-right shows progress, such as "found 64 of 110 screens in 7 flows".
   - If every flow's count matches (e.g. "4 screens" → 4 found), `…-offline.html` downloads automatically.
   - If something is missing, the box lists those flows. Scroll to them yourself (they're picked up automatically), then press **Save now**.

On a non-Mobbin tab the button shows a red **!**. Clicking it again while a save is running does nothing.
If Mobbin's image server refuses a download from the page, the extension fetches that image itself.

### Without the extension
- **Bookmark button:** open `install.html` and drag **Save Mobbin page** onto your bookmarks bar. Click it on any Mobbin page.
- **Console:** press `F12` → **Console**, paste the whole of `save-mobbin-page.js`, and press Enter. Chrome may ask you to type `allow pasting` first.

## Notes
- Open the saved file by double-clicking it. It works in any modern browser, on desktop and phone, with no internet.
- If the progress box reports images that "could not be embedded", those few will only show when you're online. Run the saver again if that happens.
- Each flow keeps its own slider, named from the caption under it on Mobbin (e.g. "Connecting to Gmail from Onboarding · 4 screens").
  Mobbin's menu previews and the "More like …" suggestions from other apps are left out.
- A screen that appears in several flows is kept in each of them.
- Saved with an older version? `node fix-saved-file.js your-file.html` cleans it up. Re-running the saver gets you the complete set of flows, though.
- The saved file is for your personal reference. Mobbin's content belongs to Mobbin and the app makers, so don't republish it.

## Development
`save-mobbin-page.js` is the single source. `node build.js` regenerates `bookmarklet.txt`, `install.html`, `demo.html` and `extension/save-mobbin-page.js` from it.
After changing it, run the build, then click the reload icon on the extension in `chrome://extensions`.
