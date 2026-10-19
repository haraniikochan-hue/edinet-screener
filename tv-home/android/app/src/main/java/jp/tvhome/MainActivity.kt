package jp.tvhome

import android.annotation.SuppressLint
import android.app.Activity
import android.content.BroadcastReceiver
import android.content.ComponentName
import android.content.Context
import android.content.IntentFilter
import android.content.Intent
import android.net.Uri
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.drawable.AdaptiveIconDrawable
import android.graphics.drawable.Drawable
import android.media.MediaMetadata
import android.media.session.MediaController
import android.media.session.MediaSessionManager
import android.media.session.PlaybackState
import android.os.Build
import android.os.Bundle
import android.os.SystemClock
import android.util.Base64
import android.provider.Settings
import android.view.KeyEvent
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.webkit.WebViewAssetLoader
import org.json.JSONArray
import org.json.JSONObject
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

private const val HOST = "appassets.androidplatform.net"
private const val HOME_URL = "https://$HOST/index.html"

// The dashboard's fixed dock, in the order the user chose. Names pick the artwork in launcher.js;
// only packages that are installed are shown. SmartTube keeps the YouTube artwork but launches SmartTube.
private val PINNED = listOf(
    "org.smarttube.stable" to "SmartTube",
    "jp.unext.tv.player" to "U-NEXT",
    "com.netflix.ninja" to "Netflix",
    "com.amazon.amazonvideo.livingroom" to "Prime Video",
    "com.disney.disneyplus" to "Disney+",
    "com.spotify.tv.android" to "Spotify",
)
// Left out of the dock: the terrestrial TV shortcut the user removed, and Xiaomi's system tools.
private val HIDDEN = Regex("^(com\\.mitv\\.livetv|com\\.xiaomi\\.mitv\\..*)$")

// The only feeds the page may fetch through the native proxy (dashboard/js/feeds.js UPSTREAM_FEEDS).
private val UPSTREAM = setOf(
    "https://news.web.nhk/n-data/conf/na/rss/cat5.xml",
    "https://www.bls.gov/schedule/news_release/bls.ics",
    "https://www.bea.gov/news/schedule/ics/online-calendar-subscription.ics",
)
// Nasdaq's earnings calendar, one US date per request (dashboard/js/earnings.js EARNINGS_URL).
private val EARNINGS = Regex("^https://api\\.nasdaq\\.com/api/calendar/earnings\\?date=\\d{4}-\\d{2}-\\d{2}$")

// The city searches the page may ask Unsplash for (dashboard/js/feeds.js PHOTO_CITIES).
private val PHOTO_QUERIES = setOf(
    "new york city skyline", "london city skyline", "paris city", "chicago downtown",
    "tokyo city", "hong kong skyline", "singapore skyline", "dubai downtown",
)

// The Spotify TV app, whose media session feeds the Spotify card without a Spotify login.
private const val SPOTIFY_TV = "com.spotify.tv.android"

// Sites the Spotify login may pass through. Only the login view opens them; the dashboard never leaves its page.
private val LOGIN_HOSTS = Regex("^(accounts\\.spotify\\.com|([a-z0-9-]+\\.)*spotify\\.com|accounts\\.google\\.com|appleid\\.apple\\.com|([a-z0-9-]+\\.)*facebook\\.com)$")

class MainActivity : Activity() {
    private lateinit var web: WebView
    private lateinit var root: FrameLayout
    private var login: WebView? = null
    // Null until the user grants TV Home notification access (HANDOFF 3.4).
    private var sessions: MediaSessionManager? = null
    @Volatile private var spotify: MediaController? = null
    private var artKey = ""
    private var artUrl = ""
    private val mediaCallback = object : MediaController.Callback() {
        override fun onMetadataChanged(metadata: MediaMetadata?) = notifyMedia()
        override fun onPlaybackStateChanged(state: PlaybackState?) = notifyMedia()
        override fun onSessionDestroyed() { attach(null); notifyMedia() }
    }
    private val sessionsChanged = MediaSessionManager.OnActiveSessionsChangedListener { attach(it) }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Chrome DevTools over ADB, for checking the page on the TV; never in the installed release build.
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)
        assets = WebViewAssetLoader.Builder()
            .setDomain(HOST)
            .addPathHandler("/", WwwHandler(WebViewAssetLoader.AssetsPathHandler(this)))
            .build()
        Thread { installedApps() }.start()
        registerReceiver(packagesChanged, IntentFilter().apply {
            addAction(Intent.ACTION_PACKAGE_ADDED); addAction(Intent.ACTION_PACKAGE_REMOVED)
            addAction(Intent.ACTION_PACKAGE_CHANGED); addDataScheme("package")
        })
        root = FrameLayout(this)
        setContentView(root)
        showDashboard(HOME_URL)
    }

    private lateinit var assets: WebViewAssetLoader

    @SuppressLint("SetJavaScriptEnabled")
    private fun showDashboard(url: String) {
        web = WebView(this).apply {
            setBackgroundColor(0xFF05070C.toInt())
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.mediaPlaybackRequiresUserGesture = true
            webViewClient = object : WebViewClient() {
                override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse? {
                    val url = request.url
                    if (url.host == HOST && url.path == "/api/upstream") return upstream(url)
                    if (url.host == HOST && url.path == "/api/unsplash") return unsplash(url.getQueryParameter("query"))
                    return assets.shouldInterceptRequest(url)
                }
                // The launcher never leaves its own page: links to other sites are ignored,
                // except the Spotify sign-in, which opens in its own view without the bridge.
                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                    val url = request.url
                    if (url.host == HOST) return false
                    if (url.scheme == "https" && url.host == "accounts.spotify.com" && url.path == "/authorize") openLogin(url.toString())
                    return true
                }
            }
            // Exposed only to this app's own page; the dashboard disables the TradingView iframe when it sees the bridge.
            addJavascriptInterface(Bridge(), "Android")
            isFocusable = true
            isFocusableInTouchMode = true
        }
        root.addView(web, 0, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        web.loadUrl(url)
        web.requestFocus(View.FOCUS_DOWN)
    }

    // Home must come back instantly, so the dashboard stays alive while another app or a cast is in
    // front and only stops its timers. The TV has 1.8 GB of RAM: if Android reports memory running low,
    // TV Home destroys the WebView (about 180 MB; WebView keeps its renderer process) and rebuilds it
    // on return without the entrance animation, showing its saved data at once.
    private var unloaded = false
    private val unload = Runnable {
        if (!unloaded) {
            unloaded = true
            closeLogin()
            root.removeView(web)
            web.destroy()
        }
    }
    override fun onStart() {
        super.onStart()
        if (unloaded) { unloaded = false; showDashboard("$HOME_URL?instant") }
        web.resumeTimers()
    }
    override fun onStop() {
        web.pauseTimers()
        super.onStop()
    }
    override fun onTrimMemory(level: Int) {
        super.onTrimMemory(level)
        if (level >= TRIM_MEMORY_RUNNING_LOW && !hasWindowFocus()) unload.run()
    }
    override fun onResume() { super.onResume(); web.onResume(); watchMedia() }
    override fun onPause() { web.onPause(); super.onPause() }
    override fun onDestroy() {
        unregisterReceiver(packagesChanged)
        sessions?.removeOnActiveSessionsChangedListener(sessionsChanged)
        spotify?.unregisterCallback(mediaCallback)
        closeLogin(); if (!unloaded) web.destroy(); super.onDestroy()
    }

    /** Follows the Spotify app's media session once notification access has been granted. */
    private fun watchMedia() {
        if (sessions != null) return
        val manager = getSystemService(MediaSessionManager::class.java) ?: return
        val listener = ComponentName(this, MediaListener::class.java)
        try {
            val active = manager.getActiveSessions(listener)
            manager.addOnActiveSessionsChangedListener(sessionsChanged, listener)
            sessions = manager
            attach(active)
            notifyMedia()
        } catch (e: SecurityException) { /* notification access not granted: the card keeps the web login */ }
    }

    private fun attach(controllers: List<MediaController>?) {
        val next = controllers?.firstOrNull { it.packageName == SPOTIFY_TV }
        if (next?.sessionToken == spotify?.sessionToken) return
        spotify?.unregisterCallback(mediaCallback)
        spotify = next
        next?.registerCallback(mediaCallback)
        notifyMedia()
    }

    private fun notifyMedia() = runOnUiThread {
        web.evaluateJavascript("window.tvHomeMedia&&window.tvHomeMedia()", null)
    }

    /** What the Spotify TV app is playing, shaped like the Web API's currently-playing response. */
    private fun nowPlaying(): String {
        if (sessions == null) return ""
        val result = JSONObject().put("connected", true).put("source", "tv").put("fetchedAt", System.currentTimeMillis())
        val controller = spotify
        val state = controller?.playbackState
        val metadata = controller?.metadata
        val active = state?.state in setOf(PlaybackState.STATE_PLAYING, PlaybackState.STATE_PAUSED, PlaybackState.STATE_BUFFERING)
        if (state == null || metadata == null || !active) return result.put("item", JSONObject.NULL).toString()
        var position = state.position
        if (state.state == PlaybackState.STATE_PLAYING) {
            position += ((SystemClock.elapsedRealtime() - state.lastPositionUpdateTime) * state.playbackSpeed).toLong()
        }
        val title = metadata.getString(MediaMetadata.METADATA_KEY_TITLE) ?: ""
        val album = metadata.getString(MediaMetadata.METADATA_KEY_ALBUM) ?: ""
        val artist = metadata.getString(MediaMetadata.METADATA_KEY_ARTIST) ?: ""
        val key = "$title\u0000$album"
        if (key != artKey) {
            artKey = key
            artUrl = (metadata.getBitmap(MediaMetadata.METADATA_KEY_ALBUM_ART)
                ?: metadata.getBitmap(MediaMetadata.METADATA_KEY_ART))?.let { jpegDataUrl(it) } ?: ""
        }
        val images = JSONArray().apply { if (artUrl.isNotEmpty()) put(JSONObject().put("url", artUrl)) }
        return result
            .put("is_playing", state.state != PlaybackState.STATE_PAUSED)
            .put("progress_ms", position.coerceAtLeast(0))
            .put("item", JSONObject()
                .put("name", title)
                .put("artists", JSONArray().apply { if (artist.isNotEmpty()) put(JSONObject().put("name", artist)) })
                .put("album", JSONObject().put("name", album).put("images", images))
                .put("duration_ms", metadata.getLong(MediaMetadata.METADATA_KEY_DURATION)))
            .toString()
    }

    /**
     * Shows Spotify's sign-in full screen. When Spotify redirects back to this app's page, the
     * dashboard loads that URL and completes the PKCE exchange itself.
     */
    @SuppressLint("SetJavaScriptEnabled")
    private fun openLogin(url: String) {
        closeLogin()
        login = WebView(this).apply {
            setBackgroundColor(0xFF121212.toInt())
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                    val next = request.url
                    if (next.host == HOST) { closeLogin(); web.loadUrl(next.toString()); return true }
                    return next.scheme != "https" || !LOGIN_HOSTS.matches(next.host ?: "")
                }
            }
            loadUrl(url)
        }
        root.addView(login, ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
        login?.requestFocus(View.FOCUS_DOWN)
    }

    private fun closeLogin() {
        val view = login ?: return
        login = null
        root.removeView(view)
        view.destroy()
        web.requestFocus(View.FOCUS_DOWN)
    }

    // Home pressed: close any sheet and return to the dock. Pressed twice quickly, from any app, it
    // opens the TV's settings instead (the remote's settings button cannot be caught without breaking
    // a held volume button; see SettingsKeyService).
    private val homePresses = DoublePress()
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        if (Intent.ACTION_MAIN != intent.action) return
        if (homePresses.press(SystemClock.uptimeMillis())) openTvSettings() else { closeLogin(); sendEscape() }
    }

    // BACK reaches the page as Escape (HANDOFF 3.2); a home screen never closes itself.
    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        if (event.keyCode == KeyEvent.KEYCODE_BACK) {
            // In the Spotify sign-in, BACK steps back a page and finally cancels the sign-in.
            val view = login
            if (event.action == KeyEvent.ACTION_UP) {
                if (view == null) sendEscape() else if (view.canGoBack()) view.goBack() else closeLogin()
            }
            return true
        }
        return super.dispatchKeyEvent(event)
    }

    private fun openTvSettings() {
        try { startActivity(Intent(Settings.ACTION_SETTINGS).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) } catch (e: Exception) { }
    }

    private fun sendEscape() {
        web.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_ESCAPE))
        web.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_UP, KeyEvent.KEYCODE_ESCAPE))
    }

    private fun upstream(url: Uri): WebResourceResponse {
        val target = url.getQueryParameter("url")
        if (target == null || (target !in UPSTREAM && !EARNINGS.matches(target))) return json(403, JSONObject().put("error", "許可されていない配信元です"))
        return try {
            val connection = URL(target).openConnection() as HttpURLConnection
            connection.connectTimeout = 10000
            connection.readTimeout = 10000
            connection.setRequestProperty("User-Agent", "TVHomeDashboard/0.10 (personal dashboard)")
            try {
                val code = connection.responseCode
                val text = if (code in 200..299) connection.inputStream.bufferedReader().use { it.readText() }
                // BLS screens clients by how they connect and refuses Android's HTTP stack (403),
                // while it serves the WebView's Chromium, so a refusal is retried through a WebView.
                else if (code == 403) fetchInWebView(target!!) else null
                if (text == null) json(502, JSONObject().put("error", "配信元から取得できません ($code)"))
                else json(200, JSONObject().put("text", text))
            } finally { connection.disconnect() }
        } catch (e: Exception) {
            json(502, JSONObject().put("error", "配信元に接続できません"))
        }
    }

    /**
     * Fetches [target] from an off-screen WebView whose blank page has the target's origin, so the
     * request is same-origin (no CORS) and made by Chromium. Called off the main thread; waits up to 20 s.
     */
    private fun fetchInWebView(target: String): String? {
        val done = CountDownLatch(1)
        var result: String? = null
        var view: WebView? = null
        val receiver = object {
            @JavascriptInterface
            fun done(text: String?) { result = text; done.countDown() }
        }
        runOnUiThread {
            view = WebView(this).apply {
                settings.javaScriptEnabled = true
                addJavascriptInterface(receiver, "TVHomeFeed")
                webViewClient = object : WebViewClient() {
                    private var started = false
                    override fun onPageFinished(v: WebView, url: String) {
                        if (started) return
                        started = true
                        v.evaluateJavascript("fetch(${JSONObject.quote(target)},{credentials:'omit'})" +
                            ".then(r=>r.ok?r.text():null,()=>null).then(t=>TVHomeFeed.done(t))", null)
                    }
                    override fun shouldOverrideUrlLoading(v: WebView, request: WebResourceRequest) = true
                }
                val origin = Uri.parse(target).let { "${it.scheme}://${it.host}/" }
                loadDataWithBaseURL(origin, "<!doctype html><title></title>", "text/html", "utf-8", null)
            }
        }
        done.await(20, TimeUnit.SECONDS)
        runOnUiThread { view?.destroy() }
        return result
    }

    /** A few random photos for one city search (dashboard/js/feeds.js unsplashRandom), with the Access Key added here. */
    private fun unsplash(query: String?): WebResourceResponse {
        if (BuildConfig.UNSPLASH_ACCESS_KEY.isEmpty()) return json(503, JSONObject().put("error", "Unsplash APIキー未設定"))
        if (query !in PHOTO_QUERIES) return json(403, JSONObject().put("error", "許可されていない検索です"))
        return try {
            val target = Uri.parse("https://api.unsplash.com/photos/random").buildUpon()
                .appendQueryParameter("query", query).appendQueryParameter("count", "3")
                .appendQueryParameter("orientation", "landscape").appendQueryParameter("content_filter", "high")
                .build().toString()
            val connection = URL(target).openConnection() as HttpURLConnection
            connection.connectTimeout = 10000
            connection.readTimeout = 10000
            connection.setRequestProperty("Authorization", "Client-ID ${BuildConfig.UNSPLASH_ACCESS_KEY}")
            connection.setRequestProperty("Accept-Version", "v1")
            try {
                val code = connection.responseCode
                if (code !in 200..299) json(if (code == 429 || code == 403) 429 else 502, JSONObject().put("error", "Unsplashから取得できません ($code)"))
                else WebResourceResponse("application/json", "utf-8", 200, "OK", mapOf("Cache-Control" to "no-store"),
                    ByteArrayInputStream(connection.inputStream.readBytes()))
            } finally { connection.disconnect() }
        } catch (e: Exception) {
            json(502, JSONObject().put("error", "Unsplashに接続できません"))
        }
    }

    private fun json(status: Int, body: JSONObject) = WebResourceResponse(
        "application/json", "utf-8", status, if (status == 200) "OK" else "Error",
        mapOf("Cache-Control" to "no-store"), ByteArrayInputStream(body.toString().toByteArray()),
    )

    /** Installed TV apps: the pinned dock first, then the rest by name. The page arranges the dock from these. */
    // Reading every app's label and icon takes over a second on this TV, so the list is built once,
    // off the main thread at start-up, and again only when an app is installed, updated or removed.
    private class TvApp(val packageName: String, val name: String, val icon: String?)
    private val appsLock = Any()
    @Volatile private var apps: List<TvApp>? = null
    @Volatile private var appsJson: String? = null
    private fun installedApps(): List<TvApp> = apps ?: synchronized(appsLock) {
        apps ?: run {
            val pm = packageManager
            val found = launchableActivities().associateBy { it.activityInfo.packageName }
            val labels = found.mapValues { it.value.loadLabel(pm).toString() }
            val pinned = PINNED.filter { it.first in found }
            val others = labels.filterKeys { key -> PINNED.none { it.first == key } }.toList().sortedBy { it.second }
            (pinned + others).map { (pkg, name) ->
                TvApp(pkg, name, try { iconDataUrl(found.getValue(pkg).loadIcon(pm)) } catch (e: Exception) { null })
            }.also { list ->
                appsJson = JSONArray(list.map {
                    JSONObject().put("name", it.name).put("packageName", it.packageName).put("icon", it.icon ?: JSONObject.NULL)
                }).toString()
                apps = list
            }
        }
    }
    private val packagesChanged = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            synchronized(appsLock) { apps = null; appsJson = null }
            Thread {
                installedApps()
                runOnUiThread { web.evaluateJavascript("window.tvHomeAppsChanged&&window.tvHomeAppsChanged()", null) }
            }.start()
        }
    }

    private fun launchableActivities() = packageManager.queryIntentActivities(
        Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LEANBACK_LAUNCHER), 0,
    ).filter { it.activityInfo.packageName != packageName && !HIDDEN.matches(it.activityInfo.packageName) }


    inner class Bridge {
        @JavascriptInterface
        fun spotifyClientId(): String = BuildConfig.SPOTIFY_CLIENT_ID

        /** The Android TV settings, which the stock home screen used to open; reached from the Settings sheet. */
        @JavascriptInterface
        fun openTvSettings() = runOnUiThread { this@MainActivity.openTvSettings() }

        @JavascriptInterface
        fun hasUnsplash(): Boolean = BuildConfig.UNSPLASH_ACCESS_KEY.isNotEmpty()

        /** Empty until notification access is granted; then the Spotify TV app's now playing as JSON. */
        @JavascriptInterface
        fun nowPlaying(): String = this@MainActivity.nowPlaying()

        @JavascriptInterface
        fun getApps(): String = appsJson ?: run { installedApps(); appsJson ?: "[]" }

        @JavascriptInterface
        fun launchApp(packageName: String) {
            // Only apps this launcher listed can be started from the page.
            if (installedApps().none { it.packageName == packageName }) return
            runOnUiThread {
                val intent = packageManager.getLeanbackLaunchIntentForPackage(packageName)
                    ?: packageManager.getLaunchIntentForPackage(packageName)
                // A system screen may refuse other apps; the tile then simply does nothing.
                try { intent?.let { startActivity(it.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) } } catch (e: Exception) { }
            }
        }
    }
}

// Adaptive icons are drawn full bleed (their 108dp canvas cropped to the 72dp visible area);
// the page clips every tile to the same squircle, so no launcher mask is applied here.
// Lossy WebP with alpha keeps each icon a few KB, so the whole list crosses the bridge quickly.
private fun iconDataUrl(drawable: Drawable, size: Int = 160): String {
    val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(bitmap)
    if (drawable is AdaptiveIconDrawable) {
        val bleed = size / 4
        listOfNotNull(drawable.background, drawable.foreground).forEach {
            it.setBounds(-bleed, -bleed, size + bleed, size + bleed); it.draw(canvas)
        }
    } else {
        drawable.setBounds(0, 0, size, size); drawable.draw(canvas)
    }
    val out = ByteArrayOutputStream()
    @Suppress("DEPRECATION")
    val format = if (Build.VERSION.SDK_INT >= 30) Bitmap.CompressFormat.WEBP_LOSSY else Bitmap.CompressFormat.WEBP
    bitmap.compress(format, 90, out)
    return "data:image/webp;base64," + Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
}

// Album art for the card: 300px is plenty for the 120px artwork and the 24px colour wash.
private fun jpegDataUrl(art: Bitmap): String {
    val scaled = Bitmap.createScaledBitmap(art, 300, 300 * art.height / art.width.coerceAtLeast(1), true)
    val out = ByteArrayOutputStream()
    scaled.compress(Bitmap.CompressFormat.JPEG, 85, out)
    return "data:image/jpeg;base64," + Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
}

/** Serves dashboard/ (copied to assets/www) at the site root. */
private class WwwHandler(private val assets: WebViewAssetLoader.AssetsPathHandler) : WebViewAssetLoader.PathHandler {
    override fun handle(path: String): WebResourceResponse? =
        assets.handle("www/" + path.ifEmpty { "index.html" })
}
