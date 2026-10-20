package jp.tvhome

/**
 * The remote's Prime Video button opens Spotify instead (the user's request, v0.30.0).
 *
 * Xiaomi's system service handles that button (mitv.service GlobalKeyReceiver.startPrimeVideo) and always
 * starts Prime Video by its component: no setting changes the target, and catching the key first would
 * need key filtering, which stops a held volume button on this TV (SettingsKeyService). So the switch is
 * made just after: when Prime Video comes to the front from another app and this launcher did not open
 * it, Spotify is opened over it. Prime Video from the dock or the app list still opens Prime Video.
 */
class AppRedirect(
    private val from: String = PRIME_VIDEO,
    val to: String = SPOTIFY,
    private val ownWindow: Long = 10_000L,
) {
    private var front: String? = null
    private var ownLaunchAt = NEVER

    /** This launcher is opening [packageName] at [now] (ms). */
    fun launching(packageName: String, now: Long) {
        if (packageName == from) ownLaunchAt = now
    }

    /**
     * An app's activity came to the front at [now] (ms). True when it is [from] arriving from another app
     * without this launcher having just opened it — the button — and [to] should be opened instead.
     * Until the app in front is known (just after the service starts), nothing is replaced.
     */
    fun onFront(packageName: String, now: Long): Boolean {
        val previous = front
        front = packageName
        if (packageName != from || previous == null || previous == from) return false
        val ours = now - ownLaunchAt <= ownWindow
        ownLaunchAt = NEVER
        return !ours
    }

    companion object {
        const val PRIME_VIDEO = "com.amazon.amazonvideo.livingroom"
        const val SPOTIFY = "com.spotify.tv.android"
        private const val NEVER = Long.MIN_VALUE / 2
    }
}

/** Shared by the launcher (its own launches) and the accessibility service (what comes to the front). */
val primeVideoButton = AppRedirect()
