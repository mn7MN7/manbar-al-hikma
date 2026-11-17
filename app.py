from flask import Flask, render_template_string
import random
import os
import json
import re

app = Flask(__name__)

def remove_tashkeel(text):
    tashkeel = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0640]')
    return tashkeel.sub('', text)

def categorize_quote(text):
    clean_text = remove_tashkeel(text).lower()
    
    if any(w in clean_text for w in ["علم", "عال", "علما", "يتعلم", "يعلم", "فهم", "فقه", "دراي"]):
        return "العلم والمعرفة"
    elif any(w in clean_text for w in ["صبر", "صابر", "اصبر", "بلا", "محن", "تستر", "تحمل"]):
        return "الصبر والتوكل"
    elif any(w in clean_text for w in ["عقل", "عاقل", "حكم", "حكيم", "لباب", "حازم", "رأي", "تدبير"]):
        return "العقل والحكمة"
    elif any(w in clean_text for w in ["دنيا", "موت", "آخر", "قبر", "مال", "غنى", "فقر", "زهد", "أمل", "فناء", "دار"]):
        return "الزهد والحياة"
    elif any(w in clean_text for w in ["عدل", "ظلم", "منصف", "قسط", "جور", "حق", "باطل", "مظلوم", "ظالم"]):
        return "العدل والإنصاف"
    elif any(w in clean_text for w in ["خلق", "صديق", "عدو", "لسان", "جار", "وف", "غدر", "كذب", "صدق", "تواضع", "كبر", "احسان", "معروف", "حب", "بغض", "اخوان"]):
        return "الأخلاق والتعامل"
    else:
        return "حكم عامة"

def load_local_quotes():
    quotes = []
    filenames = ['imamali', 'imamali-2']
    
    for filename in filenames:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
                    chunks = raw_text.split('%')
                    for i, chunk in enumerate(chunks):
                        cleaned = chunk.strip()
                        if cleaned:
                            cat = categorize_quote(cleaned)
                            quotes.append({
                                "id": f"{filename}_{i}",
                                "text": cleaned,
                                "category": cat,
                                "source": "نهج البلاغة / غرر الحكم"
                            })
            except Exception as e:
                print(f"⚠️ خطأ في قراءة الملف {filename}: {e}")
                
    if not quotes:
        quotes = [
            {"id": "default_1", "text": "الْلَّهُمَّ إِنِّي أَعُوذُ بِكَ أَنْ أَضِلَّ أَوْ أُضَلَّ.", "category": "العلم والمعرفة", "source": "نهج البلاغة"}
        ]
    return quotes

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منبر الحكمة - درر الإمام علي (ع)</title>
    <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0d1117;
            --card-bg: #161b22;
            --gold: #c5a059;
            --gold-hover: #e6ca85;
            --text-main: #f0f6fc;
            --text-muted: #8b949e;
            --border-color: #30363d;
        }
        body { font-family: 'Cairo', sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 0; }
        header { text-align: center; padding: 40px 20px; background: linear-gradient(180deg, #1f1a10 0%, var(--bg-color) 100%); border-bottom: 1px solid var(--border-color); }
        header h1 { font-family: 'Amiri', serif; color: var(--gold); font-size: 2.7rem; margin: 0; }
        header p { color: var(--text-muted); margin-top: 8px; font-size: 1.05rem; }
        .dev-badge { 
            display: inline-block; 
            margin-top: 12px; 
            background: rgba(197, 160, 89, 0.1); 
            border: 1px solid var(--gold); 
            color: var(--gold); 
            padding: 4px 14px; 
            border-radius: 20px; 
            font-size: 0.85rem; 
            font-weight: 600; 
        }
        
        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
        
        .card { 
            background-color: var(--card-bg); 
            border: 1px solid var(--gold); 
            border-radius: 16px; 
            padding: 40px; 
            margin-bottom: 30px; 
            box-shadow: 0 8px 24px rgba(0,0,0,0.5); 
            text-align: center; 
            position: relative;
            transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
        }
        .daily-title { 
            color: var(--gold); 
            font-weight: 700; 
            margin-bottom: 20px; 
            font-size: 1.15rem; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }
        .quote-text { font-family: 'Amiri', serif; font-size: 1.85rem; color: #f3e5ab; line-height: 1.9; margin-bottom: 25px; }
        .quote-source { color: var(--text-muted); font-size: 1rem; margin-bottom: 20px; }
        
        .btn-group { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }
        .interactive-btn { 
            background-color: var(--gold); 
            color: #0d1117; 
            border: none; 
            padding: 10px 22px; 
            font-weight: 700; 
            border-radius: 8px; 
            cursor: pointer; 
            transition: 0.3s; 
            font-family: 'Cairo', sans-serif; 
            font-size: 0.95rem; 
        }
        .interactive-btn:hover { background-color: var(--gold-hover); transform: scale(1.03); }
        
        .secondary-btn {
            background-color: transparent;
            border: 1px solid var(--gold);
            color: var(--gold);
            padding: 8px 18px;
            border-radius: 8px;
            cursor: pointer;
            font-family: 'Cairo', sans-serif;
            font-weight: 600;
            transition: 0.3s;
        }
        .secondary-btn:hover { background-color: rgba(197, 160, 89, 0.1); }

        .search-box {
            width: 100%;
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 15px 20px;
            border-radius: 12px;
            font-family: 'Cairo', sans-serif;
            font-size: 1.1rem;
            margin-bottom: 20px;
            box-sizing: border-box;
            transition: 0.3s;
        }
        .search-box:focus { border-color: var(--gold); outline: none; box-shadow: 0 0 10px rgba(197, 160, 89, 0.2); }

        .categories-container {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 25px;
        }
        .cat-btn {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-family: 'Cairo', sans-serif;
            font-size: 0.9rem;
            transition: 0.3s;
        }
        .cat-btn:hover, .cat-btn.active {
            background-color: var(--gold);
            color: #0d1117;
            border-color: var(--gold);
            font-weight: 700;
        }

        h2 { font-family: 'Amiri', serif; color: var(--gold); border-bottom: 2px solid var(--border-color); padding-bottom: 10px; margin-top: 40px; font-size: 1.6rem; display: flex; justify-content: space-between; align-items: center; }
        
        .quotes-grid { display: grid; gap: 15px; margin-top: 20px; max-height: 550px; overflow-y: auto; padding-left: 10px; }
        .quote-item { background-color: var(--card-bg); border: 1px solid var(--border-color); border-right: 4px solid var(--gold); border-radius: 10px; padding: 20px; animation: fadeIn 0.3s ease; position: relative; }
        .quote-item p { font-family: 'Amiri', serif; font-size: 1.3rem; margin: 0 0 15px 0; color: #f3e5ab; line-height: 1.6; }
        .quote-footer { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; color: var(--text-muted); flex-wrap: wrap; gap: 10px; }
        
        .action-icons { display: flex; gap: 12px; align-items: center; }
        .icon-btn { background: none; border: none; cursor: pointer; font-size: 1.2rem; transition: transform 0.2s; padding: 0; }
        .icon-btn:hover { transform: scale(1.2); }

        /* إشعار منبثق Toast */
        #toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background-color: var(--gold);
            color: #0d1117;
            padding: 10px 24px;
            border-radius: 30px;
            font-weight: 700;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
            z-index: 1000;
            font-size: 0.95rem;
        }
        #toast.show { transform: translateX(-50%) translateY(0); }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        footer { text-align: center; padding: 30px; color: var(--text-muted); border-top: 1px solid var(--border-color); margin-top: 50px; font-size: 0.9rem; }
    </style>
</head>
<body>
    <header>
        <h1>منبر الحكمة</h1>
        <p>موسوعة درر وحِكم الإمام علي بن أبي طالب (عليه السلام)</p>
        <div class="dev-badge">✨ تم التطوير بواسطة: مازن هجران</div>
    </header>
    
    <div class="container">
        <!-- البطاقة التفاعلية الرئيسية -->
        <div class="card" id="quoteCard">
            <div class="daily-title">
                <span>🌟 درة إشراقية تفاعلية</span>
                <span id="dailyFavBadge" style="cursor: pointer; font-size: 1.3rem;" onclick="toggleCurrentFavorite()" title="إضافة للمفضلة">🤍</span>
            </div>
            <div class="quote-text" id="quoteText">"{{ random_quote.text }}"</div>
            <div class="quote-source" id="quoteMeta">📍 {{ random_quote.source }} &nbsp;|&nbsp; 🏷️ {{ random_quote.category }}</div>
            
            <div class="btn-group">
                <button class="interactive-btn" onclick="getRandomQuote()">✨ مقولة أخرى</button>
                <button class="secondary-btn" onclick="downloadCurrentQuoteImage()">🖼️ تحميل كصورة</button>
                <button class="secondary-btn" onclick="copyCurrentQuote()">📋 نسخ النص</button>
            </div>
        </div>

        <!-- شريط البحث الفوري -->
        <input type="text" id="searchInput" class="search-box" placeholder="🔍 ابحث عن أي كلمة أو حكمة (مثل: العلم، الصبر، العدل...)..." oninput="filterQuotes()">

        <!-- أزرار الأقسام والتصنيفات -->
        <div class="categories-container" id="categoryButtons">
            <button class="cat-btn active" onclick="setCategory('الكل', this)">الكل</button>
            <button class="cat-btn" onclick="setCategory('⭐ المفضلة', this)">⭐ المفضلة</button>
            <button class="cat-btn" onclick="setCategory('العلم والمعرفة', this)">العلم والمعرفة</button>
            <button class="cat-btn" onclick="setCategory('الصبر والتوكل', this)">الصبر والتوكل</button>
            <button class="cat-btn" onclick="setCategory('العقل والحكمة', this)">العقل والحكمة</button>
            <button class="cat-btn" onclick="setCategory('الزهد والحياة', this)">الزهد والحياة</button>
            <button class="cat-btn" onclick="setCategory('العدل والإنصاف', this)">العدل والإنصاف</button>
            <button class="cat-btn" onclick="setCategory('الأخلاق والتعامل', this)">الأخلاق والتعامل</button>
            <button class="cat-btn" onclick="setCategory('حكم عامة', this)">حكم عامة</button>
        </div>

        <h2>
            <span>📚 الأرشيف والتصفح</span>
            <span id="countDisplay" style="font-size: 0.9rem; color: var(--text-muted); font-family: 'Cairo', sans-serif;">(0 مقولة)</span>
        </h2>
        
        <div class="quotes-grid" id="quotesGrid"></div>
    </div>

    <footer>
        <p>تم التطوير والبرمجة باحترافية بواسطة: <strong>مازن هجران</strong> 💻 | منبر الحكمة © 2026</p>
    </footer>

    <!-- Canvas مخفي لتوليد الصور -->
    <canvas id="imageCanvas" style="display:none;"></canvas>

    <!-- إشعار Toast منبثق -->
    <div id="toast">تمت العملية بنجاح!</div>

    <script>
        const quotesList = {{ quotes_json | safe }};
        let currentCategory = 'الكل';
        let activeQuote = {{ random_quote | tojson }};

        let favorites = JSON.parse(localStorage.getItem('imam_favorites') || '[]');

        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.innerText = message;
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 2500);
        }

        function isFavorite(id) {
            return favorites.includes(id);
        }

        function toggleFavorite(id) {
            const index = favorites.indexOf(id);
            if (index > -1) {
                favorites.splice(index, 1);
                showToast('إزالة من المفضلة 🤍');
            } else {
                favorites.push(id);
                showToast('تمت الإضافة للمفضلة ❤️');
            }
            localStorage.setItem('imam_favorites', JSON.stringify(favorites));
            filterQuotes();
            updateDailyFavBadge();
        }

        function toggleCurrentFavorite() {
            if (activeQuote && activeQuote.id) {
                toggleFavorite(activeQuote.id);
            }
        }

        function updateDailyFavBadge() {
            const badge = document.getElementById('dailyFavBadge');
            if (activeQuote && isFavorite(activeQuote.id)) {
                badge.innerText = '❤️';
                badge.title = 'إزالة من المفضلة';
            } else {
                badge.innerText = '🤍';
                badge.title = 'إضافة للمفضلة';
            }
        }

        function copyText(text) {
            navigator.clipboard.writeText(text).then(() => {
                showToast('📋 تم نسخ الحكمة إلى الحافظة!');
            });
        }

        function copyCurrentQuote() {
            if (activeQuote) {
                copyText(`"${activeQuote.text}" - ${activeQuote.source}`);
            }
        }

        // توليد صورة بتصميم AI الفاخر
        function generateQuoteImage(text, source, category) {
            const canvas = document.getElementById('imageCanvas');
            const ctx = canvas.getContext('2d');

            canvas.width = 1200;
            canvas.height = 630;

            const bgGradient = ctx.createRadialGradient(canvas.width / 2, canvas.height / 2, 50, canvas.width / 2, canvas.height / 2, 800);
            bgGradient.addColorStop(0, '#1c2433');
            bgGradient.addColorStop(0.6, '#0d1117');
            bgGradient.addColorStop(1, '#05070a');
            ctx.fillStyle = bgGradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.strokeStyle = '#c5a059';
            ctx.lineWidth = 3;
            ctx.strokeRect(40, 40, canvas.width - 80, canvas.height - 80);

            ctx.strokeStyle = 'rgba(197, 160, 89, 0.3)';
            ctx.lineWidth = 1;
            ctx.strokeRect(50, 50, canvas.width - 100, canvas.height - 100);

            drawCornerOrnament(ctx, 50, 50, 0);
            drawCornerOrnament(ctx, canvas.width - 50, 50, Math.PI / 2);
            drawCornerOrnament(ctx, canvas.width - 50, canvas.height - 50, Math.PI);
            drawCornerOrnament(ctx, 50, canvas.height - 50, -Math.PI / 2);

            ctx.fillStyle = '#e6ca85';
            ctx.font = 'bold 23px "Cairo", sans-serif';
            ctx.textAlign = 'center';
            ctx.direction = 'rtl';
            ctx.fillText('✨ منبر الحكمة - درر الإمام علي (عليه السلام) ✨', canvas.width / 2, 95);

            ctx.strokeStyle = 'rgba(197, 160, 89, 0.4)';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(canvas.width / 2 - 150, 120);
            ctx.lineTo(canvas.width / 2 + 150, 120);
            ctx.stroke();

            ctx.shadowColor = 'rgba(197, 160, 89, 0.35)';
            ctx.shadowBlur = 18;
            ctx.fillStyle = '#fffef4';
            ctx.font = 'bold 36px "Amiri", serif';
            
            wrapText(ctx, `"${text}"`, canvas.width / 2, 260, canvas.width - 240, 60);
            ctx.shadowBlur = 0;

            ctx.strokeStyle = 'rgba(197, 160, 89, 0.3)';
            ctx.beginPath();
            ctx.moveTo(canvas.width / 2 - 200, 470);
            ctx.lineTo(canvas.width / 2 + 200, 470);
            ctx.stroke();

            ctx.fillStyle = '#8b949e';
            ctx.font = '19px "Cairo", sans-serif';
            ctx.fillText(`📍 ${source}   |   🏷️ ${category}`, canvas.width / 2, 515);

            ctx.fillStyle = '#c5a059';
            ctx.font = '14px "Cairo", sans-serif';
            ctx.fillText('تطوير: مازن هجران © 2026', canvas.width / 2, 570);

            const link = document.createElement('a');
            link.download = 'imam-ali-quote-luxury.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
            showToast('🖼️ تم تحميل الصورة بنجاح!');
        }

        function drawCornerOrnament(ctx, x, y, rotation) {
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(rotation);
            ctx.strokeStyle = '#c5a059';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(25, 0);
            ctx.moveTo(0, 0);
            ctx.lineTo(0, 25);
            ctx.stroke();

            ctx.fillStyle = '#c5a059';
            ctx.beginPath();
            ctx.arc(10, 10, 2.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        function wrapText(context, text, x, y, maxWidth, lineHeight) {
            context.direction = 'rtl';
            const words = text.split(' ');
            let line = '';
            let lines = [];

            for (let n = 0; n < words.length; n++) {
                let testLine = line + words[n] + ' ';
                let metrics = context.measureText(testLine);
                let testWidth = metrics.width;
                if (testWidth > maxWidth && n > 0) {
                    lines.push(line);
                    line = words[n] + ' ';
                } else {
                    line = testLine;
                }
            }
            lines.push(line);

            let startY = y - ((lines.length - 1) * lineHeight) / 2;
            for (let k = 0; k < lines.length; k++) {
                context.fillText(lines[k].trim(), x, startY + (k * lineHeight));
            }
        }

        function downloadCurrentQuoteImage() {
            if (activeQuote) {
                generateQuoteImage(activeQuote.text, activeQuote.source, activeQuote.category);
            }
        }

        function renderQuotes(quotes) {
            const grid = document.getElementById('quotesGrid');
            const countDisplay = document.getElementById('countDisplay');
            if (countDisplay) {
                countDisplay.innerText = `(${quotes.length} مقولة)`;
            }
            
            if (quotes.length === 0) {
                grid.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 40px; font-size: 1.1rem;">لا توجد مقولات في هذا القسم أو نتيجة للبحث.</div>';
                return;
            }

            let html = '';
            quotes.forEach(q => {
                const favIcon = isFavorite(q.id) ? '❤️' : '🤍';
                const safeText = q.text.replace(/'/g, "\\'").replace(/"/g, '&quot;');
                const safeSource = q.source.replace(/'/g, "\\'");
                const safeCat = q.category.replace(/'/g, "\\'");

                html += `
                <div class="quote-item">
                    <p>"${q.text}"</p>
                    <div class="quote-footer">
                        <span>📍 ${q.source} &nbsp;|&nbsp; 🏷️ ${q.category}</span>
                        <div class="action-icons">
                            <button class="icon-btn" onclick="copyText('${safeText}')" title="نسخ النص">📋</button>
                            <button class="icon-btn" onclick="generateQuoteImage('${safeText}', '${safeSource}', '${safeCat}')" title="تحميل كصورة AI فاخرة">🖼️</button>
                            <button class="icon-btn" onclick="toggleFavorite('${q.id}')" title="تفضيل">${favIcon}</button>
                        </div>
                    </div>
                </div>`;
            });
            grid.innerHTML = html;
        }

        function filterQuotes() {
            const query = document.getElementById('searchInput').value.trim().toLowerCase();
            
            const filtered = quotesList.filter(q => {
                let matchesCategory = true;
                if (currentCategory === '⭐ المفضلة') {
                    matchesCategory = isFavorite(q.id);
                } else if (currentCategory !== 'الكل') {
                    matchesCategory = (q.category === currentCategory);
                }
                const matchesSearch = q.text.toLowerCase().includes(query) || q.category.toLowerCase().includes(query);
                return matchesCategory && matchesSearch;
            });
            
            renderQuotes(filtered);
        }

        function setCategory(cat, btn) {
            currentCategory = cat;
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterQuotes();
        }

        function getRandomQuote() {
            if (quotesList.length === 0) return;
            const card = document.getElementById('quoteCard');
            card.style.opacity = '0.2';
            card.style.transform = 'translateY(5px)';
            
            setTimeout(() => {
                const randomIndex = Math.floor(Math.random() * quotesList.length);
                activeQuote = quotesList[randomIndex];
                
                document.getElementById('quoteText').innerText = `"${activeQuote.text}"`;
                document.getElementById('quoteMeta').innerHTML = `📍 ${activeQuote.source} &nbsp;|&nbsp; 🏷️ ${activeQuote.category}`;
                updateDailyFavBadge();
                
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 200);
        }

        updateDailyFavBadge();
        renderQuotes(quotesList);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    quotes = load_local_quotes()
    random_quote = random.choice(quotes) if quotes else {"id": "default", "text": "لا حكمة متاحة", "category": "عام", "source": "غير معروف"}
    
    return render_template_string(
        HTML_TEMPLATE, 
        random_quote=random_quote, 
        all_quotes=quotes, 
        quotes_json=json.dumps(quotes, ensure_ascii=False)
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)