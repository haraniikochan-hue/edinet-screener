package jp.tvhome

import kotlin.math.max

/**
 * How a held volume button changes the volume, by how long it has been held (ms since it went down).
 * A press moves one step at once; after a short pause the volume keeps moving, faster the longer the
 * button is held: the pause between moves shrinks from 150 ms to 45 ms, and on a fine scale (the TV's
 * 0–100) each move grows from one step to two after 1.5 s and three after 3 s. Silence to full takes
 * about four seconds.
 */
object VolumeHold {
    /** Before repeating, so a single press moves one step. */
    const val FIRST_DELAY = 350L
    /** A button whose release never arrives stops repeating after this long. */
    const val MAX_HOLD = 15_000L
    /** A remote that sends a press and release for every repeat continues the same hold within this gap. */
    const val SAME_HOLD_GAP = 300L

    fun interval(held: Long): Long = max(45L, 150L - (held - FIRST_DELAY).coerceAtLeast(0L) * 6 / 100)

    fun steps(held: Long, maxIndex: Int): Int = when {
        maxIndex < 50 || held < 1_500L -> 1
        held < 3_000L -> 2
        else -> 3
    }
}
