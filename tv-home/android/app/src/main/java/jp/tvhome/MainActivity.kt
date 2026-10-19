package jp.tvhome

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.drawable.AdaptiveIconDrawable
import android.graphics.drawable.Drawable
import android.os.Bundle
import android.util.Base64
import android.provider.Settings
import android.view.KeyEvent
import android.view.View
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
// Opens the Android TV settings, which the stock home screen used to provide.
private const val TV_SETTINGS = "android.settings"
private const val MAX_APPS = 16
// Left out of the dock: the terrestrial TV shortcut the user removed, and Xiaomi's system tools.
private val HIDDEN = Regex("^(com\\.mitv\\.livetv|com\\.xiaomi\\.mitv\\..*)$")

// The only feeds the page may fetch through the native proxy (dashboard/js/feeds.js UPSTREAM_FEEDS).
private val UPSTREAM = setOf(
    "https://news.web.nhk/n-data/conf/na/rss/cat5.xml",
    "https://www.bls.gov/schedule/news_release/bls.ics",
    "https://www.bea.gov/news/schedule/ics/online-calendar-subscription.ics",
)

class MainActivity : Activity() {
    private lateinit var web: WebView
    private val icons = HashMap<String, String>()

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Chrome DevTools over ADB, for checking the page on the TV; never in the installed release build.
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)
        val assets = WebViewAssetLoader.Builder()
            .setDomain(HOST)
            .addPathHandler("/", WwwHandler(WebViewAssetLoader.AssetsPathHandler(this)))
            .build()
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
                    return assets.shouldInterceptRequest(url)
                }
                // The launcher never leaves its own page: links to other sites are ignored.
                override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest) =
                    request.url.host != HOST
            }
            // Exposed only to this app's own page; the dashboard disables the TradingView iframe when it sees the bridge.
            addJavascriptInterface(Bridge(), "Android")
            isFocusable = true
            isFocusableInTouchMode = true
        }
        setContentView(web)
        web.loadUrl(HOME_URL)
        web.requestFocus(View.FOCUS_DOWN)
    }

    override fun onResume() { super.onResume(); web.onResume() }
    override fun onPause() { web.onPause(); super.onPause() }
    override fun onDestroy() { web.destroy(); super.onDestroy() }

    // Home pressed while the dashboard is showing: close any sheet and return to the dock.
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        if (Intent.ACTION_MAIN == intent.action) sendEscape()
    }

    // BACK reaches the page as Escape (HANDOFF 3.2); a home screen never closes itself.
    override fun dispatchKeyEvent(event: KeyEvent): Boolean {
        if (event.keyCode == KeyEvent.KEYCODE_BACK) {
            if (event.action == KeyEvent.ACTION_UP) sendEscape()
            return true
        }
        return super.dispatchKeyEvent(event)
    }

    private fun sendEscape() {
        web.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_ESCAPE))
        web.dispatchKeyEvent(KeyEvent(KeyEvent.ACTION_UP, KeyEvent.KEYCODE_ESCAPE))
    }

    private fun upstream(url: Uri): WebResourceResponse {
        val target = url.getQueryParameter("url")
        if (target !in UPSTREAM) return json(403, JSONObject().put("error", "許可されていない配信元です"))
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

    private fun json(status: Int, body: JSONObject) = WebResourceResponse(
        "application/json", "utf-8", status, if (status == 200) "OK" else "Error",
        mapOf("Cache-Control" to "no-store"), ByteArrayInputStream(body.toString().toByteArray()),
    )

    /** Installed TV apps: the pinned dock first, then TV settings, then the rest by name. */
    private fun installedApps(): List<Pair<String, String>> {
        val pm = packageManager
        val launchable = launchableActivities()
            .associate { it.activityInfo.packageName to it.loadLabel(pm).toString() }
        val pinned = PINNED.filter { it.first in launchable }
        val others = launchable.filterKeys { key -> PINNED.none { it.first == key } }
            .toList().sortedBy { it.second }
        return (pinned + (TV_SETTINGS to "テレビの設定") + others).take(MAX_APPS)
    }

    private fun launchableActivities() = packageManager.queryIntentActivities(
        Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LEANBACK_LAUNCHER), 0,
    ).filter { it.activityInfo.packageName != packageName && !HIDDEN.matches(it.activityInfo.packageName) }

    /** The app's own icon as a PNG data URL; the page shows it for apps without bundled artwork. */
    private fun icon(pkg: String): String? = icons[pkg] ?: try {
        val drawable = if (pkg == TV_SETTINGS) packageManager.getApplicationIcon("com.android.tv.settings")
        else launchableActivities().first { it.activityInfo.packageName == pkg }.loadIcon(packageManager)
        pngDataUrl(drawable).also { icons[pkg] = it }
    } catch (e: Exception) { null }

    inner class Bridge {
        @JavascriptInterface
        fun getApps(): String = JSONArray(installedApps().map { (pkg, name) ->
            JSONObject().put("name", name).put("packageName", pkg).put("icon", icon(pkg) ?: JSONObject.NULL)
        }).toString()

        @JavascriptInterface
        fun launchApp(packageName: String) {
            // Only apps this launcher listed can be started from the page.
            if (installedApps().none { it.first == packageName }) return
            runOnUiThread {
                val intent = if (packageName == TV_SETTINGS) Intent(Settings.ACTION_SETTINGS)
                else packageManager.getLeanbackLaunchIntentForPackage(packageName)
                    ?: packageManager.getLaunchIntentForPackage(packageName)
                intent?.let { startActivity(it.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) }
            }
        }
    }
}

// Adaptive icons are drawn full bleed (their 108dp canvas cropped to the 72dp visible area);
// the page clips every tile to the same squircle, so no launcher mask is applied here.
private fun pngDataUrl(drawable: Drawable, size: Int = 192): String {
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
    bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
    return "data:image/png;base64," + Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
}

/** Serves dashboard/ (copied to assets/www) at the site root. */
private class WwwHandler(private val assets: WebViewAssetLoader.AssetsPathHandler) : WebViewAssetLoader.PathHandler {
    override fun handle(path: String): WebResourceResponse? =
        assets.handle("www/" + path.ifEmpty { "index.html" })
}
