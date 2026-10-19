package jp.tvhome

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.provider.Settings
import android.view.KeyEvent
import android.view.accessibility.AccessibilityEvent

/**
 * The remote's settings (gear) button, from any app. Xiaomi's system hands KEYCODE_SETTINGS to the
 * stock home's panel, which is disabled, and apps never receive it; an accessibility service sees keys
 * first. Only that key is taken: every other key is passed on untouched, and nothing is recorded.
 */
class SettingsKeyService : AccessibilityService() {
    override fun onKeyEvent(event: KeyEvent): Boolean {
        if (event.keyCode != KeyEvent.KEYCODE_SETTINGS) return false
        if (event.action == KeyEvent.ACTION_UP) {
            try { startActivity(Intent(Settings.ACTION_SETTINGS).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) } catch (e: Exception) { }
        }
        return true
    }
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {}
    override fun onInterrupt() {}
}
