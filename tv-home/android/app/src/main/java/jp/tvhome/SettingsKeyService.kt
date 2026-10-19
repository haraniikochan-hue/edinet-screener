package jp.tvhome

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.media.AudioManager
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.provider.Settings
import android.view.KeyEvent
import android.view.accessibility.AccessibilityEvent

/**
 * Two remote buttons, from any app; every other key is passed on untouched, and nothing is recorded.
 *
 * Settings (gear): Xiaomi's system hands KEYCODE_SETTINGS to the stock home's panel, which is disabled,
 * and apps never receive it; an accessibility service sees keys first.
 *
 * Volume up/down: the TV moves the volume once per press, however long the button is held. Here a
 * press moves it at once and holding keeps moving it, faster the longer it is held ([VolumeHold]).
 * The volume itself is changed through AudioManager with the system's volume bar, as the TV does.
 */
class SettingsKeyService : AccessibilityService() {
    private val handler = Handler(Looper.getMainLooper())
    private var held = 0          // the volume key being held, or 0
    private var holdStart = 0L
    private var lastKey = 0
    private var lastUp = 0L
    private val repeat = object : Runnable {
        override fun run() {
            if (held == 0) return
            val time = SystemClock.uptimeMillis() - holdStart
            if (time > VolumeHold.MAX_HOLD) { held = 0; return }
            adjust(held, time)
            handler.postDelayed(this, VolumeHold.interval(time))
        }
    }

    override fun onKeyEvent(event: KeyEvent): Boolean = when (event.keyCode) {
        KeyEvent.KEYCODE_SETTINGS -> {
            if (event.action == KeyEvent.ACTION_UP) {
                try { startActivity(Intent(Settings.ACTION_SETTINGS).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) } catch (e: Exception) { }
            }
            true
        }
        KeyEvent.KEYCODE_VOLUME_UP, KeyEvent.KEYCODE_VOLUME_DOWN -> volumeKey(event)
        else -> false
    }

    private fun volumeKey(event: KeyEvent): Boolean {
        val now = SystemClock.uptimeMillis()
        when (event.action) {
            KeyEvent.ACTION_DOWN -> {
                // The system's own key repeats are ignored: the timer below sets the pace.
                if (event.repeatCount > 0 || held == event.keyCode) return true
                handler.removeCallbacks(repeat)
                // A remote that repeats by sending press and release pairs keeps one hold going.
                if (event.keyCode != lastKey || now - lastUp > VolumeHold.SAME_HOLD_GAP) holdStart = now
                held = event.keyCode; lastKey = event.keyCode
                adjust(held, now - holdStart)
                handler.postDelayed(repeat, VolumeHold.FIRST_DELAY)
            }
            KeyEvent.ACTION_UP -> {
                if (held == event.keyCode) { held = 0; handler.removeCallbacks(repeat) }
                lastUp = now
            }
        }
        return true
    }

    private fun adjust(key: Int, time: Long) {
        val audio = getSystemService(AudioManager::class.java) ?: return
        val direction = if (key == KeyEvent.KEYCODE_VOLUME_UP) AudioManager.ADJUST_RAISE else AudioManager.ADJUST_LOWER
        try {
            repeat(VolumeHold.steps(time, audio.getStreamMaxVolume(AudioManager.STREAM_MUSIC))) {
                audio.adjustStreamVolume(AudioManager.STREAM_MUSIC, direction, AudioManager.FLAG_SHOW_UI)
            }
        } catch (e: Exception) { }
    }

    override fun onInterrupt() { held = 0; handler.removeCallbacks(repeat) }
    override fun onDestroy() { handler.removeCallbacks(repeat); super.onDestroy() }
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {}
}
