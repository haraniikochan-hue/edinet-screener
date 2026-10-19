package jp.tvhome

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class VolumeBoostTest {
    /** The TV's own repeats for a button held from [from] for [length] ms: a move at once, after 0.25 s, then every 50 ms. */
    private fun hold(boost: VolumeBoost, from: Long, length: Long, dir: Int = 1): List<Int> {
        val times = listOf(from) + generateSequence(from + 250) { it + 50 }.takeWhile { it <= from + length }
        return times.map { boost.onMove(it, dir) }
    }

    @Test fun `a short hold or a single press is left alone`() {
        val boost = VolumeBoost()
        assertTrue(hold(boost, 0, 900).all { it == 0 })
        assertEquals(0, boost.onMove(5_000, 1))
    }

    @Test fun `a longer hold gains one extra step after a second and two after two`() {
        val extra = hold(VolumeBoost(), 0, 2_500)
        assertEquals(0, extra.first()); assertEquals(1, extra[17]); assertEquals(2, extra.last())
    }

    @Test fun `silence to full takes under three seconds of holding`() {
        val boost = VolumeBoost(); var level = 0; var time = 0L
        while (level < 100) { level += 1 + boost.onMove(time, 1); time = if (time == 0L) 250 else time + 50 }
        assertTrue("took $time ms", time in 2_000L..3_000L)
    }

    @Test fun `changing direction or pausing starts a new hold`() {
        val boost = VolumeBoost()
        hold(boost, 0, 2_500)
        assertEquals(0, boost.onMove(2_550, -1))
        hold(boost, 10_000, 2_500)
        assertEquals(0, boost.onMove(13_000, 1))
    }

    @Test fun `two quick Home presses make a pair, and the pair is used up`() {
        val home = DoublePress()
        assertFalse(home.press(1_000)); assertTrue(home.press(1_500))
        assertFalse(home.press(1_900)); assertFalse(home.press(3_000)); assertTrue(home.press(3_600))
    }
}
