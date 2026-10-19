package jp.tvhome

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class VolumeHoldTest {
    @Test fun `the pause between moves shrinks the longer the button is held`() {
        assertEquals(150L, VolumeHold.interval(VolumeHold.FIRST_DELAY))
        assertTrue(VolumeHold.interval(1_000L) < VolumeHold.interval(500L))
        assertEquals(45L, VolumeHold.interval(5_000L))
    }

    @Test fun `moves grow on a fine scale only`() {
        assertEquals(1, VolumeHold.steps(0L, 100))
        assertEquals(2, VolumeHold.steps(2_000L, 100))
        assertEquals(3, VolumeHold.steps(4_000L, 100))
        assertEquals(1, VolumeHold.steps(4_000L, 15))
    }

    @Test fun `silence to full takes a few seconds of holding`() {
        var time = 0L; var level = VolumeHold.steps(time, 100)
        time = VolumeHold.FIRST_DELAY
        while (level < 100) { level += VolumeHold.steps(time, 100); time += VolumeHold.interval(time) }
        assertTrue("took ${time} ms", time in 3_000L..5_000L)
    }
}
