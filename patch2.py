import os
import re

def apply_patch(filename="index.html"):
    if not os.path.exists(filename):
        print(f"Error: Cannot find '{filename}'")
        return

    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # --- 1. INJECT THE OPTIMIZED DB LOGIC ---
    # Your provided code is much cleaner, handles transactions with promises properly, 
    # and uses reduce for the ID counter.
    new_db_code = """const DB_NAME = 'MiNotes3D_DB';
    const DB_VERSION = 1;
    const STORE_NAME = 'notes';
    let db;

    function initDB() {
      return new Promise((resolve, reject) => {
        const req = indexedDB.open(DB_NAME, DB_VERSION);
        req.onerror = () => reject(req.error);
        req.onupgradeneeded = (e) => {
          if (!e.target.result.objectStoreNames.contains(STORE_NAME))
            e.target.result.createObjectStore(STORE_NAME, { keyPath: 'id' });
        };
        req.onsuccess = () => { db = req.result; resolve(db); };
      });
    }

    function saveToDB(notesArray) {
      return new Promise((resolve, reject) => {
        const tx = db.transaction([STORE_NAME], 'readwrite');
        const store = tx.objectStore(STORE_NAME);
        store.clear();                          // prevent stale ghost notes
        notesArray.forEach(note => {
          const { __sprite, parent, ...clean } = note;
          store.put(clean);
        });
        tx.oncomplete = resolve;
        tx.onerror = () => reject(tx.error);
      });
    }

    function loadFromDB() {
      return new Promise((resolve, reject) => {
        const tx = db.transaction([STORE_NAME], 'readonly');
        const req = tx.objectStore(STORE_NAME).getAll();
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
      });
    }

    async function startApp() {
      await initDB();
      const savedNotes = await loadFromDB();

      if (savedNotes.length > 0) {
        document.getElementById('empty-state-message').style.opacity = '0';
        idCounter = savedNotes.reduce((max, n) => Math.max(max, n.id), 0) + 1;
        graphData.nodes = savedNotes.map(n => ({ ...n }));

        savedNotes.forEach(note => {
          if (note.parentId != null) {
            graphData.links.push({ source: note.parentId, target: note.id });
            const child = graphData.nodes.find(n => n.id === note.id);
            if (child) child.parent = graphData.nodes.find(p => p.id === note.parentId);
          }
        });
      }

      Graph.graphData(graphData);
      updateActiveNodeDisplay();
    }

    startApp();"""

    # Replace the old DB logic block
    content = re.sub(r"const DB_NAME = 'MiNotes3D_DB';.*?startApp\(\);", new_db_code, content, flags=re.DOTALL)

    # --- 2. ADD PWA INSTALL PROMPT LOGIC ---
    # Browsers block auto-popping the install prompt without a user gesture.
    # We intercept 'beforeinstallprompt' and show a sleek floating "Install App" button.
    
    pwa_btn_html = """\n<!-- PWA Install Button -->
<button id="pwa-install-btn" style="display:none; position:absolute; bottom:30px; left:50%; transform:translateX(-50%); z-index:9999; padding:12px 24px; background:#00ff88; color:#050510; border:none; border-radius:24px; font-weight:bold; font-size:16px; cursor:pointer; box-shadow:0 4px 15px rgba(0,255,136,0.4);">⬇️ Install Mi3D Notes</button>\n"""
    
    if 'id="pwa-install-btn"' not in content:
        content = content.replace('<div id="3d-graph"></div>', pwa_btn_html + '<div id="3d-graph"></div>')

    pwa_js = """
    // --- PWA Install Prompt Listener ---
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent the mini-infobar from appearing on mobile
        e.preventDefault();
        // Stash the event so it can be triggered later.
        deferredPrompt = e;
        // Update UI notify the user they can install the PWA
        const installBtn = document.getElementById('pwa-install-btn');
        installBtn.style.display = 'block';

        installBtn.addEventListener('click', async () => {
            // Hide the app provided install promotion
            installBtn.style.display = 'none';
            // Show the install prompt
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            const { outcome } = await deferredPrompt.userChoice;
            // We've used the prompt, and can't use it again, throw it away
            deferredPrompt = null;
        });
    });

    window.addEventListener('appinstalled', () => {
        // Hide the install button if it's still visible
        document.getElementById('pwa-install-btn').style.display = 'none';
        deferredPrompt = null;
        console.log('PWA was successfully installed');
    });
    """
    
    if 'beforeinstallprompt' not in content:
        content = content.replace('// Service Worker for PWA', pwa_js + '\n    // Service Worker for PWA')

    # --- SAVE FILE ---
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

    print("Patch successful! Replaced with your optimized DB code and added PWA install prompt logic.")

if __name__ == "__main__":
    apply_patch()
