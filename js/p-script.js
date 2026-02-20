(function () {
    'use strict';

    // ── NAVBAR SCROLL ──
    var navbar = document.getElementById('navbar');
    window.addEventListener('scroll', function () {
        navbar.classList.toggle('scrolled', window.scrollY > 50);
    });

    // ── MOBILE NAV ──
    var toggle = document.getElementById('navToggle');
    var links = document.getElementById('navLinks');
    toggle.addEventListener('click', function () {
        links.classList.toggle('open');
        toggle.innerHTML = links.classList.contains('open') ? '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
    });
    document.querySelectorAll('.nav-links a').forEach(function (a) {
        a.addEventListener('click', function () { links.classList.remove('open'); toggle.innerHTML = '<i class="fas fa-bars"></i>'; });
    });

    // ── HERO PARTICLES ──
    var pc = document.getElementById('heroParticles');
    for (var i = 0; i < 50; i++) {
        var p = document.createElement('div');
        p.className = 'particle';
        var s = Math.random() * 3 + 1;
        var colors = ['#6C5CE7', '#00CEC9', '#0984E3', '#FDCB6E'];
        p.style.cssText = 'width:' + s + 'px;height:' + s + 'px;left:' + (Math.random() * 100) + '%;background:' + colors[Math.floor(Math.random() * colors.length)] + ';animation-duration:' + (Math.random() * 15 + 10) + 's;animation-delay:' + (Math.random() * 10) + 's;opacity:' + (Math.random() * 0.5 + 0.1);
        pc.appendChild(p);
    }

    // ── MOUSE PARALLAX ──
    document.addEventListener('mousemove', function (e) {
        var x = (e.clientX / window.innerWidth - 0.5) * 20;
        var y = (e.clientY / window.innerHeight - 0.5) * 20;
        var cube = document.querySelector('.hero-3d-cube');
        if (cube) {
            cube.style.transform = 'rotateX(-20deg) rotateY(' + (x * 0.5) + 'deg) translateZ(0)';
        }
        document.querySelectorAll('.hero-float-shape').forEach(function (el, index) {
            var speed = (index + 1) * 2;
            el.style.transform = 'translate(' + (x * speed) + 'px, ' + (y * speed) + 'px)';
        });
    });

    // ── TYPED TEXT ──
    var words = ['SEO Optimization', 'Follower Growth', 'Team Hiring', 'Social Impact', 'Crypto Solutions', 'Web Development'];
    var ti = 0, ci = 0, deleting = false;
    var typed = document.getElementById('heroTyped');
    function typeEffect() {
        var w = words[ti];
        typed.textContent = deleting ? w.substring(0, ci--) : w.substring(0, ci++);
        if (!deleting && ci === w.length + 1) { setTimeout(function () { deleting = true; typeEffect(); }, 2000); return; }
        if (deleting && ci < 0) { deleting = false; ti = (ti + 1) % words.length; ci = 0; }
        setTimeout(typeEffect, deleting ? 30 : 60);
    }
    typeEffect();

    // ── SCROLL REVEAL ──
    var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
            if (e.isIntersecting) {
                e.target.classList.add('visible');
                obs.unobserve(e.target);
            }
        });
    }, { threshold: 0.15, rootMargin: "0px 0px -50px 0px" });
    document.querySelectorAll('.reveal').forEach(function (el) { obs.observe(el); });

    // ── ANIMATED COUNTERS ──
    var counterObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
            if (e.isIntersecting) {
                var el = e.target;
                var target = parseInt(el.getAttribute('data-count'));
                if (!target) return;
                var duration = 2000, start = 0, step = target / (duration / 16);
                var timer = setInterval(function () {
                    start += step;
                    if (start >= target) { start = target; clearInterval(timer); }
                    el.textContent = Math.floor(start) + (el.textContent.includes('+') ? '+' : '');
                }, 16);
                counterObs.unobserve(el);
            }
        });
    }, { threshold: 0.3 });
    document.querySelectorAll('[data-count]').forEach(function (el) { counterObs.observe(el); });

    // ── TRADINGVIEW MINI CHARTS ──
    function initTradingViewWidget(containerId, symbol) {
        var container = document.getElementById(containerId);
        if (!container) return;
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js';
        script.async = true;
        script.textContent = JSON.stringify({
            "symbol": symbol,
            "width": "100%",
            "height": "220",
            "locale": "en",
            "dateRange": "1M",
            "colorTheme": "dark",
            "isTransparent": true,
            "autosize": false,
            "largeChartUrl": "",
            "noTimeScale": false,
            "chartOnly": false
        });
        container.appendChild(script);
    }

    initTradingViewWidget('tv-btc', 'BINANCE:BTCUSDT');
    initTradingViewWidget('tv-eth', 'BINANCE:ETHUSDT');
    initTradingViewWidget('tv-sol', 'BINANCE:SOLUSDT');

    // Stocks & Gold
    initTradingViewWidget('tv-xau', 'OANDA:XAUUSD');
    initTradingViewWidget('tv-nvda', 'NASDAQ:NVDA');
    initTradingViewWidget('tv-googl', 'NASDAQ:GOOGL');
    initTradingViewWidget('tv-xrp', 'BINANCE:XRPUSDT');
    initTradingViewWidget('tv-xag', 'OANDA:XAGUSD');
    initTradingViewWidget('tv-doge', 'BINANCE:DOGEUSDT');

    // ── NEWS FEED ──
    function fetchNews() {
        var feed = document.getElementById('newsFeed');
        // Use multiple RSS sources as fallbacks
        var sources = [
            'https://api.rss2json.com/v1/api.json?rss_url=https://cointelegraph.com/rss',
            'https://api.rss2json.com/v1/api.json?rss_url=https://www.coindesk.com/arc/outboundfeeds/rss/',
            'https://api.rss2json.com/v1/api.json?rss_url=https://feeds.feedburner.com/TechCrunch/'
        ];

        function tryFetch(index) {
            if (index >= sources.length) {
                // All sources failed — show hardcoded fallback news
                feed.innerHTML = '';
                var fallbackItems = [
                    { title: 'Bitcoin Surges Past Key Resistance Level', author: 'CoinDesk', time: 'Today' },
                    { title: 'Ethereum Layer 2 Networks See Record Transaction Volume', author: 'CoinTelegraph', time: 'Today' },
                    { title: 'SEC Reviews New Crypto ETF Applications', author: 'Bloomberg', time: 'Today' },
                    { title: 'Solana DeFi Ecosystem Expands with New Protocols', author: 'The Block', time: 'Today' },
                    { title: 'Web3 Adoption Accelerates Across Enterprise Sector', author: 'TechCrunch', time: 'Today' },
                    { title: 'AI and Blockchain Convergence Creates New Opportunities', author: 'Forbes', time: 'Today' }
                ];
                fallbackItems.forEach(function (item, idx) {
                    var div = document.createElement('div');
                    div.className = 'news-item';
                    div.innerHTML = '<div class="news-prompt">$ feed&gt;</div><div class="news-content"><h4>' + item.title + '</h4><p>' + item.time + ' — ' + item.author + '</p></div>';
                    div.style.animation = 'fadeInUp 0.5s ease ' + (idx * 0.1) + 's both';
                    feed.appendChild(div);
                });
                return;
            }

            fetch(sources[index])
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (data.items && data.items.length) {
                        feed.innerHTML = '';
                        data.items.slice(0, 8).forEach(function (item, idx) {
                            var d = new Date(item.pubDate);
                            var time = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                            var div = document.createElement('div');
                            div.className = 'news-item';
                            div.innerHTML = '<div class="news-prompt">$ feed&gt;</div><div class="news-content"><h4><a href="' + item.link + '" target="_blank">' + item.title + '</a></h4><p>' + time + ' — ' + (item.author || 'News') + '</p></div>';
                            div.style.animation = 'fadeInUp 0.5s ease ' + (idx * 0.1) + 's both';
                            feed.appendChild(div);
                        });
                    } else {
                        tryFetch(index + 1);
                    }
                })
                .catch(function () {
                    tryFetch(index + 1);
                });
        }

        tryFetch(0);
    }
    fetchNews();


})();
