package jp.tvhome

/**
 * Speeds up a held volume button. Held, the TV's own remote handling moves the volume one step after
 * 0.25 s and then every 50 ms (20 steps a second). Each of those moves is seen here as a volume
 * change; moves in the same direction less than [GAP] apart are one hold. Once a hold has lasted
 * 1 s every move gets one extra step, and after 2 s two extra, so silence to full takes under three
 * seconds instead of five. A single press, or presses a little apart, are left alone.
 */
class VolumeBoost {
    private var start = 0L
    private var last = Long.MIN_VALUE / 2
    private var direction = 0

    /** A volume move by the TV at [now] (ms) in [dir] (+1 or −1); returns the extra steps to add. */
    fun onMove(now: Long, dir: Int): Int {
        if (dir != direction || now - last > GAP) start = now
        direction = dir; last = now
        val held = now - start
        return when {
            held < 1_000L -> 0
            held < 2_000L -> 1
            else -> 2
        }
    }

    companion object {
        /** Longer than the TV's first repeat (0.25 s), shorter than two deliberate presses. */
        const val GAP = 450L
    }
}

/** Two presses of the remote's Home button in quick succession. */
class DoublePress(private val within: Long = 700L) {
    private var last = Long.MIN_VALUE / 2

    /** A press at [now] (ms); true when it is the second of a quick pair (the pair is then used up). */
    fun press(now: Long): Boolean {
        val double = now - last <= within
        last = if (double) Long.MIN_VALUE / 2 else now
        return double
    }
}
