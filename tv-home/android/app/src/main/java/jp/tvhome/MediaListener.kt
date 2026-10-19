package jp.tvhome

import android.service.notification.NotificationListenerService

/**
 * Registered only so the user can grant TV Home notification access, which Android requires
 * before an app may read other apps' media sessions (MainActivity reads Spotify's). Notifications
 * themselves are never read.
 */
class MediaListener : NotificationListenerService()
