import os
import re

def apply_patch(filename="index.html"):
    if not os.path.exists(filename):
        print(f"Error: Cannot find '{filename}'")
        return

    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    print("Applying Patch 8: Database Stability & Mobile UI Enhancements...")
    original_content = content

    # --- 1. FIX THE DATABASE (Switch from .add to .put) ---
    old_db_logic = """    async function saveToDB(notesArray) {
        const transaction = db.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        store.clear().onsuccess = () => {
            notesArray.forEach(note => {
                const cleanNote = { ...note };
                delete cleanNote.__sprite; // Don't save 3D objects to DB
                delete cleanNote.parent; // Don't save circular references
                store.add(cleanNote);
            });
        };
    }"""

    new_db_logic = """    async function saveToDB(notesArray) {
        const transaction = db.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        
        // FIX: Use .put() to safely update existing nodes and insert new ones without race conditions
        notesArray.forEach(note => {
            const cleanNote = { ...note };
            delete cleanNote.__sprite; 
            delete cleanNote.parent; 
            store.put(cleanNote); 
        });
    }"""

    if "store.put(cleanNote);" not in content:
        content = content.replace(old_db_logic, new_db_logic)
        print(" -> Upgraded IndexedDB engine to use robust upserts (.put).")

    # --- 2. FIX THE MOBILE UI (Bottom Sheet layout) ---
    old_mobile_css = """        /* Mobile Overrides */
        @media (max-width: 768px) {
            #controls-container, #search-container { width: 280px; left: 50%; margin-left: -140px; top: 80px; }
            .main-btn, .btn-secondary { padding: 12px; } /* Larger touch targets */
        }"""

    new_mobile_css = """        /* Mobile Overrides */
        @media (max-width: 768px) {
            #controls-container, #search-container { width: 280px; left: 50%; margin-left: -140px; top: 80px; }
            .main-btn, .btn-secondary { padding: 12px; } /* Larger touch targets */
            
            /* Mobile Info Panel Adjustments (Bottom Sheet Style) */
            #info-panel { 
                bottom: 0; width: 100vw; max-width: 100vw; 
                border-radius: 24px 24px 0 0; padding: 20px 15px 10px 15px; 
                border-left: none; border-right: none; border-bottom: none;
            }
            #edit-content-input { max-height: 40vh; } /* Gives keyboard room */
            .toolbar button { font-size: 18px; padding: 5px; } /* Prevent toolbar crowding */
            
            /* Adjust Fullscreen on Mobile */
            #info-panel.info-fullscreen { padding-top: 60px; border-radius: 0; }
        }"""

    if "Bottom Sheet Style" not in content:
        content = content.replace(old_mobile_css, new_mobile_css)
        print(" -> Overhauled mobile CSS for the Mi Notes editor (Bottom Sheet implementation).")

    # --- SAVE FILE ---
    if content == original_content:
        print(" -> No changes needed. The patch may have already been applied.")
    else:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        print("\nPatch 8 successful! Your database is now stable and the mobile UI is optimized.")

if __name__ == "__main__":
    apply_patch()
