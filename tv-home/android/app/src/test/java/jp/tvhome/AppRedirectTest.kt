package jp.tvhome

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AppRedirectTest {
    private val home = "jp.tvhome.launcher"
    private val prime = AppRedirect.PRIME_VIDEO
    private val netflix = "com.netflix.ninja"

    @Test fun `the button opens Prime Video from home or another app, and it is replaced`() {
        val redirect = AppRedirect()
        redirect.onFront(home, 0)
        assertTrue(redirect.onFront(prime, 1_000))
        redirect.onFront(AppRedirect.SPOTIFY, 1_500)
        redirect.onFront(netflix, 60_000)
        assertTrue(redirect.onFront(prime, 61_000))
    }

    @Test fun `Prime Video opened from the dock or the app list stays`() {
        val redirect = AppRedirect()
        redirect.onFront(home, 0)
        redirect.launching(prime, 5_000)
        assertFalse(redirect.onFront(prime, 6_200))
    }

    @Test fun `a dock launch covers that one opening only`() {
        val redirect = AppRedirect()
        redirect.onFront(home, 0)
        redirect.launching(prime, 5_000)
        assertFalse(redirect.onFront(prime, 6_000))
        redirect.onFront(home, 7_000)
        assertTrue(redirect.onFront(prime, 8_000))
    }

    @Test fun `moving between Prime Video's own screens is not a new opening`() {
        val redirect = AppRedirect()
        redirect.onFront(home, 0)
        redirect.launching(prime, 1_000)
        assertFalse(redirect.onFront(prime, 2_000))
        assertFalse(redirect.onFront(prime, 30_000))
    }

    @Test fun `nothing is replaced before the app in front is known`() {
        assertFalse(AppRedirect().onFront(prime, 0))
    }

    @Test fun `other apps are never replaced`() {
        val redirect = AppRedirect()
        redirect.onFront(home, 0)
        assertFalse(redirect.onFront(netflix, 1_000))
        assertFalse(redirect.onFront(AppRedirect.SPOTIFY, 2_000))
    }
}
