#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VIDEHA & SADEHA PDF SEARCH SERVER - FIXED VERSION
Handles special characters and Unicode errors
"""

import os
import sys
import json
import re
import glob
import traceback
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Try to use pypdf for text extraction
try:
    from pypdf import PdfReader
    HAS_PYPDF = True
    print("✅ pypdf loaded successfully")
except ImportError:
    HAS_PYPDF = False
    print("⚠️ pypdf not installed. Run: pip install pypdf")

PORT = 8080
INDEX_FILE = "pdf_index.json"

def safe_json_dump(data, filepath):
    """Safely save JSON data, handling Unicode errors"""
    try:
        with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return True
    except Exception as e:
        print(f"⚠️ JSON save error: {e}")
        # Try with ascii encoding only
        try:
            with open(filepath, 'w', encoding='ascii', errors='ignore') as f:
                json.dump(data, f, ensure_ascii=True, indent=2, default=str)
            print("   Saved with ASCII encoding")
            return True
        except Exception as e2:
            print(f"❌ Failed to save index: {e2}")
            return False

def clean_text(text):
    """Clean text by removing invalid Unicode characters"""
    if not text:
        return ""
    # Replace invalid surrogate pairs
    text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text

class PDFSearchEngine:
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
        self.index = {}
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using pypdf with error handling"""
        if not HAS_PYPDF:
            return ""
        try:
            reader = PdfReader(str(pdf_path))
            text = ""
            num_pages = len(reader.pages)
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += clean_text(page_text) + " "
                except Exception as e:
                    # Skip problematic pages
                    pass
                # Show progress
                if (page_num + 1) % 10 == 0 or page_num + 1 == num_pages:
                    print(f"      Page {page_num+1}/{num_pages}", end="\r")
            return clean_text(text)
        except Exception as e:
            print(f"\n      ⚠️ Error reading PDF: {e}")
            return ""
    
    def build_index(self):
        print("\n" + "="*60)
        print("📚 Building PDF index with pypdf...")
        print("="*60)
        print(f"📂 Folder: {self.folder_path}")
        
        if not self.folder_path.exists():
            print(f"❌ Folder not found!")
            return False
        
        pdf_files = list(self.folder_path.glob("*.pdf")) + list(self.folder_path.glob("*.PDF"))
        pdf_files = sorted(pdf_files)
        print(f"📄 Found {len(pdf_files)} PDF files")
        
        if len(pdf_files) == 0:
            print("❌ No PDF files found!")
            return False
        
        print("\n📖 Extracting text from PDFs (this will take 5-10 minutes for 478 files)...")
        print("   Each dot = 1 file processed\n")
        
        for i, pdf_path in enumerate(pdf_files):
            file_size = pdf_path.stat().st_size / (1024 * 1024)
            filename = pdf_path.name.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            
            print(f"   [{i+1}/{len(pdf_files)}] {filename[:60]} ({file_size:.1f} MB)")
            
            text = ""
            if HAS_PYPDF:
                text = self.extract_text_from_pdf(pdf_path)
                if text:
                    # Limit text size to avoid memory issues
                    text = text[:150000]
                    print(f"      ✅ {len(text)} characters extracted")
                else:
                    print(f"      ⚠️ No text extracted")
            
            # Store in index with clean keys
            safe_filename = filename
            self.index[safe_filename] = {
                "path": str(pdf_path).encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'),
                "name": safe_filename,
                "text": text[:150000] if text else "",
                "size_mb": round(file_size, 2),
                "has_text": bool(text)
            }
        
        # Save index with error handling
        print("\n💾 Saving index...")
        if safe_json_dump(self.index, INDEX_FILE):
            print(f"✅ Index saved to {INDEX_FILE}")
        else:
            print("⚠️ Could not save index, but search will work in memory")
        
        text_count = sum(1 for d in self.index.values() if d.get("has_text"))
        print(f"\n📊 Total files indexed: {len(self.index)}")
        print(f"📖 Files with extractable text: {text_count}/{len(self.index)}")
        
        if not HAS_PYPDF:
            print("\n⚠️  To enable full text search, install pypdf:")
            print('   C:\\Users\\DELL\\AppData\\Local\\Python\\pythoncore-3.14-64\\Scripts\\pip.exe install pypdf')
        
        print("="*60)
        return True
    
    def load_index(self):
        if os.path.exists(INDEX_FILE):
            try:
                with open(INDEX_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                    self.index = json.load(f)
                text_count = sum(1 for d in self.index.values() if d.get("has_text", False))
                print(f"✅ Loaded {len(self.index)} PDFs from index")
                print(f"📖 Files with text content: {text_count}")
                return True
            except Exception as e:
                print(f"⚠️ Could not load index: {e}")
                return False
        return False
    
    def search(self, query):
        """Search through indexed PDFs"""
        if not query:
            return []
        
        query_lower = query.lower()
        results = []
        
        for filename, data in self.index.items():
            match_found = False
            context = ""
            count = 0
            
            # Search in text content if available
            if data.get("text"):
                try:
                    text_lower = data["text"].lower()
                    if query_lower in text_lower:
                        match_found = True
                        count = text_lower.count(query_lower)
                        # Find context around first match
                        pos = text_lower.find(query_lower)
                        start = max(0, pos - 150)
                        end = min(len(data["text"]), pos + 200)
                        context = data["text"][start:end] if pos >= 0 else ""
                        context = clean_text(context)
                except Exception:
                    pass
            
            # Also search in filename
            if not match_found and query_lower in filename.lower():
                match_found = True
                count = 1
                context = f"Filename matches: {filename}"
            
            if match_found:
                results.append({
                    "filename": filename,
                    "path": data["path"],
                    "name": data["name"],
                    "context": context[:300] if context else "",
                    "count": count,
                    "size_mb": data.get("size_mb", 0),
                    "has_text": data.get("has_text", False)
                })
        
        results.sort(key=lambda x: x["count"], reverse=True)
        return results

class SearchHandler(BaseHTTPRequestHandler):
    engine = None
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        try:
            if self.path == "/" or self.path == "/index.html":
                self.serve_html()
            elif self.path.startswith("/search"):
                self.handle_search()
            elif self.path == "/status":
                self.send_status()
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def send_status(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        text_count = sum(1 for d in self.engine.index.values() if d.get("has_text", False)) if self.engine else 0
        status = {
            "status": "running",
            "pdf_count": len(self.engine.index) if self.engine else 0,
            "has_full_text": text_count > 0 if self.engine else False,
            "text_files": text_count
        }
        try:
            self.wfile.write(json.dumps(status).encode('utf-8', errors='ignore'))
        except:
            self.wfile.write(b'{"status":"running"}')
    
    def serve_html(self):
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>विदेह आ सदेह | PDF ताकू इंजिन</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Noto Serif Devanagari', 'Segoe UI', Georgia, serif;
            background: #f5f0e8;
            color: #2c2418;
        }
        .container { max-width: 1300px; margin: 0 auto; padding: 20px; }
        
        .header {
            background: #8B1A1A;
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 0 0 30px 30px;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5rem; font-family: 'Playfair Display', serif; }
        .header h1 span { font-size: 1.8rem; }
        .header p { margin-top: 10px; opacity: 0.9; }
        .stats-badge {
            background: rgba(255,255,255,0.2);
            display: inline-block;
            padding: 8px 20px;
            border-radius: 50px;
            margin-top: 15px;
            font-size: 0.9rem;
        }
        
        .search-card {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .search-label {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: #8B1A1A;
        }
        .search-wrapper {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .search-input {
            flex: 1;
            padding: 15px 20px;
            font-size: 1rem;
            border: 2px solid #e0d6c5;
            border-radius: 50px;
            font-family: inherit;
            outline: none;
        }
        .search-input:focus { border-color: #8B1A1A; box-shadow: 0 0 0 3px rgba(139,26,26,0.1); }
        .search-btn {
            background: #8B1A1A;
            color: white;
            border: none;
            padding: 15px 35px;
            font-size: 1rem;
            border-radius: 50px;
            cursor: pointer;
            font-weight: 600;
        }
        .search-btn:hover { background: #a52a2a; }
        
        .example-tags {
            margin-top: 15px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .example-tag {
            background: #f0e8dc;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            cursor: pointer;
        }
        .example-tag:hover { background: #e0d6c5; }
        
        .result-card {
            background: white;
            border-radius: 16px;
            border: 1px solid #e0d6c5;
            margin-bottom: 15px;
        }
        .result-item { padding: 20px; }
        .result-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; }
        .result-title a { color: #8B1A1A; text-decoration: none; }
        .result-title a:hover { text-decoration: underline; }
        .result-meta {
            font-size: 0.75rem;
            color: #7a6848;
            margin-bottom: 12px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .result-snippet {
            background: #f9f5ec;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 0.9rem;
            color: #3a3025;
            line-height: 1.5;
        }
        .result-snippet mark {
            background: #ffeb99;
            padding: 2px 4px;
            border-radius: 4px;
        }
        .no-results {
            text-align: center;
            padding: 50px;
            background: white;
            border-radius: 16px;
            color: #8B1A1A;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #8B1A1A;
        }
        .footer {
            text-align: center;
            padding: 30px;
            color: #7a6848;
            font-size: 0.8rem;
            border-top: 1px solid #e0d6c5;
            margin-top: 30px;
        }
        @media (max-width: 700px) {
            .container { padding: 15px; }
            .header h1 { font-size: 1.8rem; }
            .search-wrapper { flex-direction: column; }
            .search-btn { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 विदेह <span>&</span> सदेह</h1>
        <p>प्रथम मैथिली पाक्षिक ई पत्रिका — पूरा पाठ PDF ताकू इंजिन</p>
        <div class="stats-badge" id="statsBadge">⏳ लोड होइत अछि...</div>
    </div>
    
    <div class="container">
        <div class="search-card">
            <div class="search-label">
                🔍 478 PDF अंक के भीतर ताकू
            </div>
            <div class="search-wrapper">
                <input type="text" id="searchInput" class="search-input" 
                       placeholder="ताकू: मैथिली, कविता, गद्य, लेखक, अंक..." autocomplete="off">
                <button id="searchBtn" class="search-btn">🔎 ताकू</button>
            </div>
            <div class="example-tags">
                <span class="example-tag" onclick="setQuery('मैथिली')">मैथिली</span>
                <span class="example-tag" onclick="setQuery('कविता')">कविता</span>
                <span class="example-tag" onclick="setQuery('गद्य')">गद्य</span>
                <span class="example-tag" onclick="setQuery('विदेह')">विदेह</span>
                <span class="example-tag" onclick="setQuery('सदेह')">सदेह</span>
            </div>
        </div>
        
        <div id="resultsArea">
            <div class="loading">🔍 ऊपर देल गेल खोज बॉक्समे लिखू आ ताकू कुंजी दबाउ।</div>
        </div>
        
        <div class="footer">
            ⚡ स्थानीय सर्वर — <span id="pdfCount">478</span> PDF अंक
        </div>
    </div>
    
    <script>
        async function loadStatus() {
            try {
                const res = await fetch('/status');
                const data = await res.json();
                const statusText = data.has_full_text ? 
                    '✅ पूरा पाठ खोज सक्षम' : 
                    '⚠️ फाइलनाम मात्र खोज';
                document.getElementById('statsBadge').innerHTML = `📄 ${data.pdf_count} PDF अंक | ${statusText}`;
                document.getElementById('pdfCount').innerText = data.pdf_count;
            } catch(e) {
                document.getElementById('statsBadge').innerHTML = `✅ सर्वर चालू अछि`;
            }
        }
        
        async function searchPDFs() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) {
                document.getElementById('resultsArea').innerHTML = '<div class="no-results">⚠️ कृपया ताकू शब्द लिखू</div>';
                return;
            }
            
            document.getElementById('resultsArea').innerHTML = '<div class="loading">⏳ खोज होइत अछि...</div>';
            
            try {
                const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
                const data = await res.json();
                
                if (data.results.length === 0) {
                    document.getElementById('resultsArea').innerHTML = `
                        <div class="no-results">
                            📭 कोनो परिणाम नै भेटल।<br><br>
                            कृपया दोसर शब्द ताकू।
                        </div>`;
                    return;
                }
                
                let html = `<div style="margin-bottom: 20px; padding: 10px; background: #f0e8dc; border-radius: 10px;">✅ कुल ${data.results.length} PDF मिलल</div>`;
                
                for (const r of data.results) {
                    let context = r.context || '';
                    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&')})`, 'gi');
                    context = context.replace(regex, '<mark>$1</mark>');
                    
                    const filePath = r.path.replace(/\\\\/g, '/');
                    const searchType = r.has_text ? '📖 पूरा पाठ' : '📄 फाइलनाम';
                    
                    html += `
                        <div class="result-card">
                            <div class="result-item">
                                <div class="result-title">
                                    <a href="file:///${filePath}" target="_blank">📄 ${escapeHtml(r.name)}</a>
                                </div>
                                <div class="result-meta">
                                    <span>📦 ${r.size_mb} MB</span>
                                    <span>🔍 मिलल: ${r.count} बेर</span>
                                    <span>${searchType}</span>
                                </div>
                                ${context ? `<div class="result-snippet">${context}...</div>` : ''}
                            </div>
                        </div>
                    `;
                }
                document.getElementById('resultsArea').innerHTML = html;
            } catch(e) {
                document.getElementById('resultsArea').innerHTML = '<div class="no-results">⚠️ त्रुटि: सर्वर सँ कनेक्शन नहि अछि</div>';
            }
        }
        
        function escapeHtml(str) {
            if (!str) return '';
            return String(str).replace(/[&<>]/g, function(m) {
                if (m === '&') return '&amp;';
                if (m === '<') return '&lt;';
                if (m === '>') return '&gt;';
                return m;
            });
        }
        
        function setQuery(text) {
            document.getElementById('searchInput').value = text;
            searchPDFs();
        }
        
        document.getElementById('searchBtn').addEventListener('click', searchPDFs);
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') searchPDFs();
        });
        
        loadStatus();
        setInterval(loadStatus, 30000);
    </script>
</body>
</html>'''
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8', errors='ignore'))
    
    def handle_search(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query).get('q', [''])[0]
        results = self.engine.search(query) if self.engine and query else []
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        try:
            self.wfile.write(json.dumps({"results": results}, ensure_ascii=False, default=str).encode('utf-8', errors='ignore'))
        except:
            self.wfile.write(b'{"results":[]}')

def main():
    pdf_folder = r"C:\Users\DELL\Desktop\Videha PDFs"
    
    print("\n" + "="*60)
    print("📚 VIDEHA & SADEHA PDF SEARCH SERVER (Fixed)")
    print("="*60)
    print(f"📂 PDF Folder: {pdf_folder}")
    
    if not os.path.exists(pdf_folder):
        print(f"\n❌ Folder not found: {pdf_folder}")
        return
    
    # Delete old corrupted index if exists
    if os.path.exists(INDEX_FILE):
        try:
            os.remove(INDEX_FILE)
            print("🗑️ Removed old index file")
        except:
            pass
    
    engine = PDFSearchEngine(pdf_folder)
    
    # Build new index
    print("\n📖 Building search index...")
    print("⏳ This will take 5-10 minutes for 478 PDFs...")
    engine.build_index()
    
    SearchHandler.engine = engine
    
    print("\n" + "="*60)
    print(f"🚀 SERVER RUNNING!")
    print(f"📡 Open in browser: http://localhost:{PORT}")
    print(f"📁 PDF Folder: {pdf_folder}")
    print(f"📊 Indexed PDFs: {len(engine.index)}")
    text_count = sum(1 for d in engine.index.values() if d.get("has_text", False))
    if text_count > 0:
        print(f"📖 Full text search: ENABLED ({text_count} files with text)")
    else:
        print(f"⚠️ Full text search: DISABLED")
    print("="*60)
    print("\n🛑 Press Ctrl+C to stop the server\n")
    
    server = HTTPServer(('localhost', PORT), SearchHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped.")

if __name__ == "__main__":
    main()