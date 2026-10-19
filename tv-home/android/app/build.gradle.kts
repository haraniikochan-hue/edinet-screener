import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// The WebView serves the same dashboard/ sources as `npm run dev`, copied in at build time.
val webAssets = layout.buildDirectory.dir("generated/web")
val copyDashboard by tasks.registering(Sync::class) {
    from(rootProject.file("../dashboard")) {
        exclude("**/.*", "**/*.local.json")
    }
    into(webAssets.map { it.dir("www") })
}

// Credentials are read from local.properties (not committed):
// spotify.clientId=<32 hex>, unsplash.accessKey=<Unsplash Access Key>.
// The user's Mac also keeps them in ~/.config/tv-home/local.properties, outside any session folder;
// the project's own local.properties wins when both have a value.
val localProperties = Properties().apply {
    listOf(File(System.getProperty("user.home"), ".config/tv-home/local.properties"), rootProject.file("local.properties"))
        .filter { it.exists() }.forEach { file -> file.inputStream().use { load(it) } }
}
val spotifyClientId = localProperties.getProperty("spotify.clientId", "")
    .takeIf { it.matches(Regex("^[a-f0-9]{32}$")) } ?: ""
val unsplashAccessKey = localProperties.getProperty("unsplash.accessKey", "")
    .takeIf { it.matches(Regex("^[A-Za-z0-9_-]{20,100}$")) } ?: ""

android {
    namespace = "jp.tvhome"
    compileSdk = 35
    defaultConfig {
        applicationId = "jp.tvhome.launcher"
        minSdk = 28
        targetSdk = 35
        versionCode = 15
        versionName = "0.23.0"
        buildConfigField("String", "SPOTIFY_CLIENT_ID", "\"$spotifyClientId\"")
        buildConfigField("String", "UNSPLASH_ACCESS_KEY", "\"$unsplashAccessKey\"")
    }
    sourceSets["main"].assets.srcDir(webAssets)
    buildTypes {
        release {
            isMinifyEnabled = false
            // Sideloaded with ADB only: the debug key is enough until a store or update channel exists.
            signingConfig = signingConfigs.getByName("debug")
        }
    }
    buildFeatures { buildConfig = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

tasks.named("preBuild") { dependsOn(copyDashboard) }

dependencies {
    implementation("androidx.webkit:webkit:1.12.1")
}