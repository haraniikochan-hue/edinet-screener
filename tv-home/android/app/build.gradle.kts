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

android {
    namespace = "jp.tvhome"
    compileSdk = 35
    defaultConfig {
        applicationId = "jp.tvhome.launcher"
        minSdk = 28
        targetSdk = 35
        versionCode = 1
        versionName = "0.10.0"
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
