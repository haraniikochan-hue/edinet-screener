package jp.tvhome

import android.accessibilityservice.AccessibilityService
import android.content.BroadcastReceiver
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.media.AudioManager
import android.os.Build
import android.os.SystemClock
import android.view.accessibility.AccessibilityEvent

/**
 * Speeds up a held volume button, in every app ([VolumeBoost]), and turns the remote's Prime Video
 * button into a Spotify button ([AppRedirect]). It reads no keys and no screen content: it follows the
 * TV's own volume changes and, while a hold lasts, adds steps; and it notes which app's screen comes to
 * the front (the package and activity names of window changes, nothing inside them).
 *
 * It must not filter key events. On this TV an accessibility service that filters keys makes the
 * system handle the volume keys before it and drop their repeats, so a held button moved the volume
 * only once (v0.16.0–v0.26.0, when this service also caught the settings button). The settings button
 * is now replaced by pressing Home twice (MainActivity). The class keeps its name so the accessibility
 * permission the TV already granted stays in place.
 */
class SettingsKeyService : AccessibilityService() {
    private val boost = VolumeBoost()
    private var ownValue = -1
    private var ownAt = 0L

    private val volumeChanged = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            if (intent.getIntExtra(EXTRA_STREAM, -1) != AudioManager.STREAM_MUSIC) return
            val value = intent.getIntExtra(EXTRA_VALUE, -1)
            val previous = intent.getIntExtra(EXTRA_PREVIOUS, -1)
            if (value < 0 || previous < 0 || value == previous) return
            val now = SystemClock.uptimeMillis()
            // The change this service just made comes back as a broadcast too.
            if (value == ownValue && now - ownAt < 300) return
            val direction = if (value > previous) 1 else -1
            val extra = boost.onMove(now, direction)
            if (extra == 0) return
            val audio = getSystemService(AudioManager::class.java) ?: return
            val target = (value + direction * extra)
                .coerceIn(audio.getStreamMinVolume(AudioManager.STREAM_MUSIC), audio.getStreamMaxVolume(AudioManager.STREAM_MUSIC))
            if (target == value) return
            ownValue = target; ownAt = now
            try { audio.setStreamVolume(AudioManager.STREAM_MUSIC, target, 0) } catch (e: Exception) { }
        }
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        val filter = IntentFilter(VOLUME_CHANGED)
        if (Build.VERSION.SDK_INT >= 33) registerReceiver(volumeChanged, filter, Context.RECEIVER_NOT_EXPORTED)
        else registerReceiver(volumeChanged, filter)
    }

    override fun onDestroy() {
        try { unregisterReceiver(volumeChanged) } catch (e: Exception) { }
        super.onDestroy()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event?.eventType != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) return
        // Only the user's own TV turns the Prime Video button into Spotify; the parents' TV keeps Prime Video.
        if (BuildConfig.PROFILE != "home") return
        val app = event.packageName?.toString() ?: return
        val window = event.className?.toString() ?: return
        // Only an activity is an app coming to the front: dialogs, the keyboard and the volume bar are not.
        try { packageManager.getActivityInfo(ComponentName(app, window), 0) } catch (e: PackageManager.NameNotFoundException) { return }
        if (!primeVideoButton.onFront(app, SystemClock.uptimeMillis())) return
        val open = packageManager.getLeanbackLaunchIntentForPackage(primeVideoButton.to)
            ?: packageManager.getLaunchIntentForPackage(primeVideoButton.to) ?: return
        // Back from Spotify returns home, not to the Prime Video left behind it.
        try { startActivity(open.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_TASK_ON_HOME)) } catch (e: Exception) { }
    }
    override fun onInterrupt() {}

    private companion object {
        // AudioManager's volume change broadcast (sent by the system for every change; not in the public SDK).
        const val VOLUME_CHANGED = "android.media.VOLUME_CHANGED_ACTION"
        const val EXTRA_STREAM = "android.media.EXTRA_VOLUME_STREAM_TYPE"
        const val EXTRA_VALUE = "android.media.EXTRA_VOLUME_STREAM_VALUE"
        const val EXTRA_PREVIOUS = "android.media.EXTRA_PREV_VOLUME_STREAM_VALUE"
    }
}
