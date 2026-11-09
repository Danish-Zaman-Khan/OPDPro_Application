plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val debugAppUrl = providers.gradleProperty("opdAppUrl")
    .orElse("http://10.0.2.2:8000/")
    .get()
val releaseAppUrl = providers.gradleProperty("opdAppUrl")
    .orElse("https://replace-with-your-production-domain/")
    .get()

android {
    namespace = "com.opdpro.mobile"
    compileSdk = 35

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    defaultConfig {
        applicationId = "com.opdpro.mobile"
        minSdk = 23
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        getByName("debug") {
            buildConfigField("String", "OPD_START_URL", "\"$debugAppUrl\"")
        }
        getByName("release") {
            isMinifyEnabled = false
            buildConfigField("String", "OPD_START_URL", "\"$releaseAppUrl\"")
        }
    }

    buildFeatures {
        buildConfig = true
    }
}

dependencies {
    implementation("androidx.swiperefreshlayout:swiperefreshlayout:1.1.0")
}
